from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from uuid import UUID
import structlog

from app.database import get_db
from app.models import Order, Organization, Product, OrderStatusEnum, OrderStatusHistory, Staff, StaffRoleEnum
from app.schemas import OrderResponse, OrderDetailResponse
from app.dependencies import verify_staff_token
from app.services.payment import PaymentService

logger = structlog.get_logger()
router = APIRouter(prefix="/admin")


@router.get("/dashboard", response_model=None)
async def admin_dashboard(
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db)
):
    """Admin dashboard overview"""
    # Get revenue
    revenue_result = await db.execute(
        select(func.sum(Order.total)).where(
            Order.organization_id == org_id,
            Order.payment_status == "paid",
            Order.created_at >= datetime.utcnow() - timedelta(days=30)
        )
    )
    total_revenue = revenue_result.scalar() or 0

    # Get order count
    orders_count_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.organization_id == org_id,
            Order.created_at >= datetime.utcnow() - timedelta(days=30)
        )
    )
    total_orders = orders_count_result.scalar() or 0

    # Active orders
    active_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.organization_id == org_id,
            Order.status.in_([OrderStatusEnum.RECEIVED, OrderStatusEnum.CONFIRMED, OrderStatusEnum.PREPARING])
        )
    )
    active_orders = active_result.scalar() or 0

    # Average order value
    avg_order_value = (total_revenue // total_orders) if total_orders > 0 else 0

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "average_order_value": avg_order_value,
        "active_orders": active_orders,
        "period": "last_30_days"
    }


@router.get("/orders", response_model=None)
async def admin_orders(
    org_id: UUID = Query(..., alias="organization_id"),
    status: OrderStatusEnum = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List all orders for admin"""
    query = select(Order).where(Order.organization_id == org_id)

    if status:
        query = query.where(Order.status == status)

    query = query.order_by(Order.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    orders = result.scalars().all()

    return {
        "orders": [OrderResponse.from_orm(o) for o in orders],
        "count": len(orders)
    }


@router.patch("/orders/{order_id}/status", response_model=None)
async def update_order_status(
    order_id: UUID,
    new_status: OrderStatusEnum = Query(...),
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db)
):
    """Update order status from admin panel"""
    order_result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.organization_id == org_id
        )
    )
    order = order_result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order.status
    order.status = new_status
    order.updated_at = datetime.utcnow()

    # Add to history
    history = OrderStatusHistory(
        order_id=order.id,
        status=new_status,
        changed_by="admin"
    )
    db.add(history)

    await db.commit()

    logger.info(
        "order_status_updated",
        order_id=str(order.id),
        old_status=old_status,
        new_status=new_status
    )

    return OrderDetailResponse.from_orm(order)


@router.get("/menu/products")
async def list_products(
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db)
):
    """List products"""
    result = await db.execute(
        select(Product).where(Product.organization_id == org_id)
    )
    products = result.scalars().all()
    return {"products": products, "count": len(products)}


@router.post("/menu/products")
async def create_product(
    org_id: UUID = Query(..., alias="organization_id"),
):
    """Create product"""
    return {"product_id": "stub", "status": "created"}


@router.get("/staff")
async def list_staff(
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db)
):
    """List staff"""
    result = await db.execute(
        select(Staff).where(Staff.organization_id == org_id)
    )
    staff_members = result.scalars().all()
    return {"staff": staff_members, "count": len(staff_members)}
