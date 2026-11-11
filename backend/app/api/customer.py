from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.models import Organization, User, Product, Category, Order, OrderStatusEnum, OrderTypeEnum
from app.schemas import (
    MenuResponse, ProductDetailResponse, CategoryResponse,
    OrderCreate, OrderResponse, OrderDetailResponse
)
from app.dependencies import verify_telegram_user, get_current_org_id

router = APIRouter(prefix="/customer")


@router.get("/menu", response_model=MenuResponse)
async def get_menu(
    org_id: UUID = Query(..., alias="organization_id"),
    category_id: UUID = Query(None),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get menu for customer"""
    # Get categories
    categories_query = select(Category).where(
        Category.organization_id == org_id,
        Category.is_active == True
    ).order_by(Category.display_order)

    categories_result = await db.execute(categories_query)
    categories = categories_result.scalars().all()

    # Get products
    products_query = select(Product).where(
        Product.organization_id == org_id,
        Product.is_available == True
    )

    if category_id:
        products_query = products_query.where(Product.category_id == category_id)

    if search:
        products_query = products_query.where(
            Product.name.ilike(f"%{search}%") |
            Product.description.ilike(f"%{search}%")
        )

    products_query = products_query.order_by(Product.display_order)
    products_result = await db.execute(products_query)
    products = products_result.scalars().all()

    return MenuResponse(
        categories=[CategoryResponse.from_orm(c) for c in categories],
        products=[ProductDetailResponse.from_orm(p) for p in products]
    )


@router.get("/orders/{order_id}/tracking-widget")
async def get_tracking_widget(
    order_id: UUID,
    telegram_id: str = Query(...),
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db)
):
    """Get HTML tracking widget for order"""
    from app.services.telegram_widgets import generate_tracking_widget_html

    user = await verify_telegram_user(telegram_id, org_id, db)

    order_result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == user.id,
            Order.organization_id == org_id
        )
    )
    order = order_result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    html = await generate_tracking_widget_html(
        order_id=order.id,
        org_id=org_id,
        order_number=order.order_number
    )

    return {
        "html": html,
        "order_id": str(order.id),
        "order_number": order.order_number,
        "status": order.status
    }


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    telegram_id: str = Query(...),
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db)
):
    """Create new order"""
    # Verify user
    user = await verify_telegram_user(telegram_id, org_id, db)

    # Validate branch exists
    from app.models import Branch
    branch_result = await db.execute(
        select(Branch).where(
            Branch.id == order_data.branch_id,
            Branch.organization_id == org_id
        )
    )
    branch = branch_result.scalar_one_or_none()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    # Calculate order total
    subtotal = 0
    items = []

    for item in order_data.items:
        product_result = await db.execute(
            select(Product).where(Product.id == item.product_id)
        )
        product = product_result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        item_price = product.price
        for modifier in item.modifiers:
            # Find modifier option price
            for mod in product.modifiers:
                if mod.id == modifier.modifier_id:
                    for opt in mod.options:
                        if opt.get("name") == modifier.selected_option:
                            item_price += opt.get("price_delta", 0)

        item_total = item_price * item.quantity
        subtotal += item_total

        items.append({
            "product_id": str(item.product_id),
            "product_name": product.name,
            "quantity": item.quantity,
            "unit_price": item_price,
            "total_price": item_total,
            "modifiers": [m.dict() for m in item.modifiers]
        })

    # Calculate tax (assume 10%)
    tax = int(subtotal * 0.1)
    total = subtotal + tax

    # Generate order number
    from app.models import Order as OrderModel
    last_order_result = await db.execute(
        select(OrderModel).where(
            OrderModel.organization_id == org_id
        ).order_by(OrderModel.created_at.desc()).limit(1)
    )
    last_order = last_order_result.scalar_one_or_none()
    order_number = f"#{int(last_order.order_number.lstrip('#')) + 1:06d}" if last_order else "#000001"

    # Create order
    new_order = OrderModel(
        organization_id=org_id,
        user_id=user.id,
        branch_id=order_data.branch_id,
        order_number=order_number,
        status=OrderStatusEnum.RECEIVED,
        order_type=order_data.order_type,
        table_number=order_data.table_number,
        items=items,
        subtotal=subtotal,
        tax=tax,
        total=total,
        notes=order_data.notes
    )

    db.add(new_order)
    await db.flush()

    # Add to status history
    from app.models import OrderStatusHistory
    history = OrderStatusHistory(
        order_id=new_order.id,
        status=OrderStatusEnum.RECEIVED,
        changed_by="customer"
    )
    db.add(history)

    await db.commit()
    await db.refresh(new_order)

    return OrderResponse.from_orm(new_order)


@router.get("/orders/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    order_id: UUID,
    telegram_id: str = Query(...),
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db)
):
    """Get order details"""
    user = await verify_telegram_user(telegram_id, org_id, db)

    order_result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == user.id,
            Order.organization_id == org_id
        )
    )
    order = order_result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderDetailResponse.from_orm(order)


@router.get("/orders", response_model=list[OrderResponse])
async def get_orders(
    telegram_id: str = Query(...),
    org_id: UUID = Query(..., alias="organization_id"),
    status: OrderStatusEnum = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get user's orders"""
    user = await verify_telegram_user(telegram_id, org_id, db)

    query = select(Order).where(
        Order.user_id == user.id,
        Order.organization_id == org_id
    )

    if status:
        query = query.where(Order.status == status)

    query = query.order_by(Order.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    orders = result.scalars().all()

    return [OrderResponse.from_orm(o) for o in orders]


@router.patch("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: UUID,
    telegram_id: str = Query(...),
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db)
):
    """Cancel order"""
    user = await verify_telegram_user(telegram_id, org_id, db)

    order_result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == user.id,
            Order.organization_id == org_id
        )
    )
    order = order_result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status in [OrderStatusEnum.COMPLETED, OrderStatusEnum.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed or already cancelled order"
        )

    order.status = OrderStatusEnum.CANCELLED
    order.cancelled_at = __import__('datetime').datetime.utcnow()

    await db.commit()
    await db.refresh(order)

    return OrderResponse.from_orm(order)


@router.get("/user/profile")
async def get_user_profile(
    telegram_id: str = Query(...),
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db)
):
    """Get user profile"""
    user = await verify_telegram_user(telegram_id, org_id, db)

    return {
        "id": str(user.id),
        "telegram_id": user.telegram_id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "preferred_language": user.preferred_language,
        "registration_date": user.registration_date.isoformat()
    }


@router.get("/user/loyalty-card")
async def get_loyalty_card(
    telegram_id: str = Query(...),
    org_id: UUID = Query(..., alias="organization_id"),
    db: AsyncSession = Depends(get_db)
):
    """Get user loyalty card"""
    from app.models import LoyaltyAccount

    user = await verify_telegram_user(telegram_id, org_id, db)

    loyalty_result = await db.execute(
        select(LoyaltyAccount).where(
            LoyaltyAccount.user_id == user.id,
            LoyaltyAccount.organization_id == org_id
        )
    )
    loyalty = loyalty_result.scalar_one_or_none()

    if not loyalty:
        raise HTTPException(status_code=404, detail="Loyalty account not found")

    return {
        "id": str(loyalty.id),
        "tier": loyalty.tier,
        "points_balance": loyalty.points_balance,
        "created_at": loyalty.created_at.isoformat()
    }


@router.post("/orders/{order_id}/checkout")
async def checkout_order(
    order_id: UUID,
    telegram_id: str = Query(...),
    org_id: UUID = Query(..., alias="organization_id"),
    return_url: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Initialize payment for order"""
    from app.services.payment import PaymentService

    user = await verify_telegram_user(telegram_id, org_id, db)

    # Verify order belongs to user
    order_result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == user.id,
            Order.organization_id == org_id
        )
    )
    order = order_result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.payment_status != PaymentStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already paid or in wrong state"
        )

    try:
        payment_response = await PaymentService.create_payment_for_order(
            db=db,
            org_id=org_id,
            order_id=order_id,
            return_url=return_url
        )
        return payment_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
