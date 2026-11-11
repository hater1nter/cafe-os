from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import structlog

from app.models import Order, OrderStatusEnum, PaymentStatusEnum, OrderStatusHistory
from app.services.payment_provider import get_payment_provider, PaymentStatusEnum as ProviderPaymentStatus
from app.config import settings

logger = structlog.get_logger()


class PaymentService:
    """Handle payment operations and state transitions"""

    @staticmethod
    async def create_payment_for_order(
        db: AsyncSession,
        org_id: UUID,
        order_id: UUID,
        return_url: str
    ) -> dict:
        """Create payment session for order"""
        # Get order
        order_result = await db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.organization_id == org_id
            )
        )
        order = order_result.scalar_one_or_none()

        if not order:
            raise ValueError(f"Order {order_id} not found")

        if order.payment_status != PaymentStatusEnum.PENDING:
            raise ValueError(f"Order already paid or in wrong state")

        # Get organization to determine provider
        from app.models import Organization
        org_result = await db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = org_result.scalar_one_or_none()

        # Get payment provider
        provider = get_payment_provider(org.payment_provider, {})

        # Get customer info
        customer = order.user
        from app.services.payment_provider import PaymentCustomer
        payment_customer = PaymentCustomer(
            customer_id=str(customer.id),
            email=customer.email or "customer@cafe-os.local",
            phone=customer.phone or "+7-000-000-0000"
        )

        # Create payment
        try:
            payment = await provider.create_payment(
                order_id=str(order.id),
                amount=order.total,
                customer=payment_customer,
                return_url=return_url
            )

            # Save payment provider transaction ID
            order.payment_provider_transaction_id = payment.payment_id

            await db.commit()

            logger.info(
                "payment_created",
                order_id=str(order.id),
                payment_id=payment.payment_id,
                provider=org.payment_provider,
                amount=order.total
            )

            return {
                "payment_id": payment.payment_id,
                "redirect_url": payment.redirect_url,
                "order_id": str(order.id)
            }
        except Exception as e:
            logger.error(
                "payment_creation_failed",
                order_id=str(order.id),
                error=str(e)
            )
            raise

    @staticmethod
    async def handle_payment_success(
        db: AsyncSession,
        org_id: UUID,
        payment_id: str
    ) -> Order:
        """Handle successful payment callback"""
        # Find order by payment provider transaction ID
        order_result = await db.execute(
            select(Order).where(
                Order.payment_provider_transaction_id == payment_id,
                Order.organization_id == org_id
            )
        )
        order = order_result.scalar_one_or_none()

        if not order:
            logger.warning("payment_success_no_order", payment_id=payment_id)
            raise ValueError(f"Order not found for payment {payment_id}")

        if order.payment_status == PaymentStatusEnum.PAID:
            logger.info("payment_already_processed", payment_id=payment_id)
            return order

        # Update order payment status
        order.payment_status = PaymentStatusEnum.PAID
        order.confirmed_at = datetime.utcnow()

        # Update order status to CONFIRMED
        if order.status == OrderStatusEnum.RECEIVED:
            order.status = OrderStatusEnum.CONFIRMED

            # Add to history
            history = OrderStatusHistory(
                order_id=order.id,
                status=OrderStatusEnum.CONFIRMED,
                changed_by="payment_system",
                reason="Payment confirmed"
            )
            db.add(history)

        await db.commit()

        logger.info(
            "payment_success_processed",
            order_id=str(order.id),
            payment_id=payment_id
        )

        return order

    @staticmethod
    async def handle_payment_failure(
        db: AsyncSession,
        org_id: UUID,
        payment_id: str,
        reason: str = "Unknown"
    ) -> Order:
        """Handle payment failure"""
        order_result = await db.execute(
            select(Order).where(
                Order.payment_provider_transaction_id == payment_id,
                Order.organization_id == org_id
            )
        )
        order = order_result.scalar_one_or_none()

        if not order:
            logger.warning("payment_failure_no_order", payment_id=payment_id)
            raise ValueError(f"Order not found for payment {payment_id}")

        # Update payment status
        order.payment_status = PaymentStatusEnum.FAILED

        await db.commit()

        logger.warning(
            "payment_failure_processed",
            order_id=str(order.id),
            payment_id=payment_id,
            reason=reason
        )

        return order

    @staticmethod
    async def verify_webhook_signature(
        provider_name: str,
        payload: dict,
        signature: str
    ) -> bool:
        """Verify payment provider webhook signature"""
        try:
            provider = get_payment_provider(provider_name, {})
            return await provider.verify_webhook(payload, signature)
        except Exception as e:
            logger.error(
                "webhook_verification_failed",
                provider=provider_name,
                error=str(e)
            )
            return False

    @staticmethod
    async def refund_order(
        db: AsyncSession,
        org_id: UUID,
        order_id: UUID,
        reason: str = "Customer request"
    ) -> bool:
        """Refund order payment"""
        order_result = await db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.organization_id == org_id
            )
        )
        order = order_result.scalar_one_or_none()

        if not order:
            raise ValueError(f"Order {order_id} not found")

        if order.payment_status != PaymentStatusEnum.PAID:
            raise ValueError("Only paid orders can be refunded")

        # Get organization for provider
        from app.models import Organization
        org_result = await db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = org_result.scalar_one_or_none()

        provider = get_payment_provider(org.payment_provider, {})

        # Refund via provider
        try:
            success = await provider.refund_payment(
                order.payment_provider_transaction_id,
                order.total
            )

            if success:
                order.payment_status = PaymentStatusEnum.REFUNDED
                order.status = OrderStatusEnum.CANCELLED
                await db.commit()

                logger.info(
                    "order_refunded",
                    order_id=str(order.id),
                    reason=reason
                )

            return success
        except Exception as e:
            logger.error(
                "refund_failed",
                order_id=str(order.id),
                error=str(e)
            )
            raise
