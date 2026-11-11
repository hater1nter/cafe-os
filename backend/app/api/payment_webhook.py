from fastapi import APIRouter, Request, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import structlog
import json

from app.database import get_db
from app.models import Organization
from app.services.payment import PaymentService

logger = structlog.get_logger()
router = APIRouter(prefix="/payments")


@router.post("/webhook/yandex_kassa")
async def yandex_kassa_webhook(
    request: Request,
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = None
):
    """Yandex.Kassa payment webhook"""
    try:
        # Get organization
        db = db or AsyncSession()
        org_result = await db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = org_result.scalar_one_or_none()

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        payload = await request.json()

        # Verify signature
        signature = request.headers.get("X-Yandex-Checkout-Shop-API-Signature", "")
        is_valid = await PaymentService.verify_webhook_signature(
            "yandex_kassa",
            payload,
            signature
        )

        if not is_valid:
            logger.warning(
                "webhook_signature_invalid",
                provider="yandex_kassa",
                org_id=str(org_id)
            )
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Handle payment event
        event_type = payload.get("event")
        payment_data = payload.get("object", {})
        payment_id = payment_data.get("id")
        status_val = payment_data.get("status")

        if event_type == "payment.succeeded":
            await PaymentService.handle_payment_success(db, org_id, payment_id)
        elif event_type in ["payment.canceled", "payment.expired"]:
            await PaymentService.handle_payment_failure(
                db, org_id, payment_id, reason=status_val
            )

        logger.info(
            "webhook_processed",
            provider="yandex_kassa",
            event_type=event_type,
            payment_id=payment_id
        )

        return {"status": "success"}

    except Exception as e:
        logger.error("webhook_error", provider="yandex_kassa", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/yukassa")
async def yukassa_webhook(
    request: Request,
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db)
):
    """ЮKassa payment webhook"""
    try:
        org_result = await db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = org_result.scalar_one_or_none()

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        payload = await request.json()

        # Verify signature
        signature = request.headers.get("X-Signature", "")
        is_valid = await PaymentService.verify_webhook_signature(
            "yukassa",
            payload,
            signature
        )

        if not is_valid:
            logger.warning(
                "webhook_signature_invalid",
                provider="yukassa",
                org_id=str(org_id)
            )
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Handle payment event
        payment_id = payload.get("paymentId")
        status_val = payload.get("status")

        if status_val == "completed":
            await PaymentService.handle_payment_success(db, org_id, payment_id)
        elif status_val in ["failed", "cancelled"]:
            await PaymentService.handle_payment_failure(
                db, org_id, payment_id, reason=status_val
            )

        logger.info(
            "webhook_processed",
            provider="yukassa",
            status=status_val,
            payment_id=payment_id
        )

        return {"status": "success"}

    except Exception as e:
        logger.error("webhook_error", provider="yukassa", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/sberpay")
async def sberpay_webhook(
    request: Request,
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db)
):
    """SberPay payment webhook"""
    try:
        org_result = await db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = org_result.scalar_one_or_none()

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        payload = await request.json()

        # Verify signature
        signature = request.headers.get("X-Signature", "")
        is_valid = await PaymentService.verify_webhook_signature(
            "sberpay",
            payload,
            signature
        )

        if not is_valid:
            logger.warning(
                "webhook_signature_invalid",
                provider="sberpay",
                org_id=str(org_id)
            )
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Handle payment event
        payment_id = payload.get("id")
        status_val = payload.get("status")

        if status_val == "completed":
            await PaymentService.handle_payment_success(db, org_id, payment_id)
        elif status_val in ["failed", "declined"]:
            await PaymentService.handle_payment_failure(
                db, org_id, payment_id, reason=status_val
            )

        logger.info(
            "webhook_processed",
            provider="sberpay",
            status=status_val,
            payment_id=payment_id
        )

        return {"status": "success"}

    except Exception as e:
        logger.error("webhook_error", provider="sberpay", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
