"""
Demo data initialization script for Café OS
Creates MONO COFFEE demonstration café with sample menu and orders
"""

import asyncio
from datetime import datetime, timedelta
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker, engine, Base
from app.models import (
    Organization, Branch, Category, Product, Modifier,
    User, Order, LoyaltyAccount, Staff,
    OrderStatusEnum, OrderTypeEnum, PaymentStatusEnum, LoyaltyTierEnum, StaffRoleEnum
)


async def init_demo_data():
    """Initialize demo café and sample data"""

    # Create all tables first
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        # Create MONO COFFEE organization
        org = Organization(
            id=uuid.uuid4(),
            slug="mono-coffee",
            name="MONO COFFEE",
            branding={
                "primary_color": "#241813",
                "secondary_color": "#C58B58",
                "accent_color": "#9AA58C",
                "logo_url": "https://via.placeholder.com/200",
                "font_family": "Inter"
            },
            subscription_tier="pro",
            telegram_bot_token="demo_token_12345",
            payment_provider="yandex_kassa"
        )
        session.add(org)
        await session.flush()

        # Create main branch
        branch = Branch(
            id=uuid.uuid4(),
            organization_id=org.id,
            name="MONO COFFEE Main",
            address="123 Coffee Street, Moscow, Russia",
            phone="+7-999-123-4567",
            operating_hours={
                "monday": {"open": "08:00", "close": "20:00"},
                "tuesday": {"open": "08:00", "close": "20:00"},
                "wednesday": {"open": "08:00", "close": "20:00"},
                "thursday": {"open": "08:00", "close": "20:00"},
                "friday": {"open": "08:00", "close": "22:00"},
                "saturday": {"open": "09:00", "close": "22:00"},
                "sunday": {"open": "10:00", "close": "20:00"}
            },
            is_active=True
        )
        session.add(branch)
        await session.flush()

        # Create categories
        categories = {}
        category_names = ["Coffee", "Signature Drinks", "Matcha", "Tea", "Cold Drinks", "Breakfast", "Bakery", "Desserts"]
        for i, cat_name in enumerate(category_names):
            cat = Category(
                id=uuid.uuid4(),
                organization_id=org.id,
                name=cat_name,
                display_order=i,
                is_active=True
            )
            session.add(cat)
            await session.flush()
            categories[cat_name] = cat.id

        # Create products
        products_data = [
            {
                "name": "Espresso",
                "category": "Coffee",
                "price": 150,
                "description": "Single shot of premium espresso",
                "modifiers": [
                    {
                        "name": "Size",
                        "type": "single_choice",
                        "options": [
                            {"name": "Single (25ml)", "price_delta": 0},
                            {"name": "Double (50ml)", "price_delta": 50}
                        ]
                    }
                ]
            },
            {
                "name": "Flat White",
                "category": "Coffee",
                "price": 250,
                "description": "Espresso with velvety microfoam milk",
                "modifiers": [
                    {
                        "name": "Milk Type",
                        "type": "single_choice",
                        "options": [
                            {"name": "Regular Milk", "price_delta": 0},
                            {"name": "Oat Milk", "price_delta": 30},
                            {"name": "Almond Milk", "price_delta": 30},
                            {"name": "Coconut Milk", "price_delta": 30}
                        ]
                    }
                ]
            },
            {
                "name": "Cappuccino",
                "category": "Coffee",
                "price": 280,
                "description": "Espresso with equal parts steamed milk and foam",
                "modifiers": [
                    {
                        "name": "Milk Type",
                        "type": "single_choice",
                        "options": [
                            {"name": "Regular Milk", "price_delta": 0},
                            {"name": "Oat Milk", "price_delta": 30},
                            {"name": "Almond Milk", "price_delta": 30}
                        ]
                    }
                ]
            },
            {
                "name": "Iced Matcha Latte",
                "category": "Matcha",
                "price": 320,
                "description": "Vibrant matcha with cold milk and ice",
                "modifiers": [
                    {
                        "name": "Sugar Level",
                        "type": "single_choice",
                        "options": [
                            {"name": "No Sugar", "price_delta": 0},
                            {"name": "Light", "price_delta": 0},
                            {"name": "Regular", "price_delta": 0},
                            {"name": "Extra Sweet", "price_delta": 0}
                        ]
                    }
                ]
            },
            {
                "name": "Croissant",
                "category": "Bakery",
                "price": 180,
                "description": "Buttery French croissant",
                "modifiers": []
            },
            {
                "name": "Pistachio Cookie",
                "category": "Bakery",
                "price": 120,
                "description": "Crunchy pistachio cookie",
                "modifiers": []
            },
            {
                "name": "Basque Cheesecake",
                "category": "Desserts",
                "price": 350,
                "description": "Rich and creamy Basque burnt cheesecake",
                "modifiers": []
            }
        ]

        for prod_data in products_data:
            product = Product(
                id=uuid.uuid4(),
                organization_id=org.id,
                category_id=categories[prod_data["category"]],
                name=prod_data["name"],
                description=prod_data["description"],
                price=prod_data["price"],
                image_url="https://via.placeholder.com/300x300",
                is_available=True,
                is_seasonal=False
            )
            session.add(product)
            await session.flush()

            # Add modifiers
            for i, mod_data in enumerate(prod_data["modifiers"]):
                modifier = Modifier(
                    id=uuid.uuid4(),
                    product_id=product.id,
                    name=mod_data["name"],
                    type=mod_data["type"],
                    options=mod_data["options"],
                    is_required=True,
                    display_order=i
                )
                session.add(modifier)

        await session.flush()

        # Create demo users
        demo_users = []
        for i in range(3):
            user = User(
                id=uuid.uuid4(),
                organization_id=org.id,
                telegram_id=f"demo_user_{i+1}",
                phone=f"+7-999-000-{i+1:04d}",
                email=f"customer{i+1}@example.com",
                full_name=f"Demo Customer {i+1}",
                preferred_language="en",
                is_active=True
            )
            session.add(user)
            await session.flush()
            demo_users.append(user)

            # Create loyalty account
            loyalty = LoyaltyAccount(
                id=uuid.uuid4(),
                user_id=user.id,
                organization_id=org.id,
                tier=LoyaltyTierEnum.BRONZE,
                points_balance=100 * (i + 1)
            )
            session.add(loyalty)

        await session.flush()

        # Create demo staff
        admin_staff = Staff(
            id=uuid.uuid4(),
            organization_id=org.id,
            branch_id=branch.id,
            name="Admin User",
            email="admin@cafe-os.local",
            password_hash="$2b$12$demo_hash",  # Demo password
            role=StaffRoleEnum.ADMIN,
            permissions=["all"],
            is_active=True
        )
        session.add(admin_staff)

        barista_staff = Staff(
            id=uuid.uuid4(),
            organization_id=org.id,
            branch_id=branch.id,
            telegram_id="demo_barista_1",
            name="Barista Demo",
            email="barista@cafe-os.local",
            role=StaffRoleEnum.BARISTA,
            permissions=["orders.manage"],
            is_active=True
        )
        session.add(barista_staff)

        await session.flush()

        # Create demo orders
        products_query = await session.execute("SELECT id FROM products LIMIT 3")
        product_ids = [row[0] for row in products_query]

        for user_idx, user in enumerate(demo_users):
            for order_idx in range(2):
                order_number = f"#{(user_idx * 2 + order_idx + 1):06d}"
                items = [
                    {
                        "product_id": str(product_ids[order_idx % len(product_ids)]),
                        "product_name": f"Product {order_idx}",
                        "quantity": order_idx + 1,
                        "unit_price": 250,
                        "total_price": 250 * (order_idx + 1),
                        "modifiers": []
                    }
                ]

                order = Order(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    user_id=user.id,
                    branch_id=branch.id,
                    order_number=order_number,
                    status=OrderStatusEnum.COMPLETED if order_idx == 0 else OrderStatusEnum.READY,
                    order_type=OrderTypeEnum.TAKEAWAY,
                    items=items,
                    subtotal=250 * (order_idx + 1),
                    tax=25 * (order_idx + 1),
                    total=275 * (order_idx + 1),
                    payment_status=PaymentStatusEnum.PAID,
                    payment_method="card",
                    created_at=datetime.utcnow() - timedelta(hours=24 - order_idx)
                )
                session.add(order)

        await session.commit()
        print("✅ Demo data initialized successfully!")
        print(f"✅ Created: MONO COFFEE organization")
        print(f"✅ Created: {len(categories)} product categories")
        print(f"✅ Created: {len(products_data)} products with modifiers")
        print(f"✅ Created: {len(demo_users)} demo users")
        print(f"✅ Created: 2 staff members (admin + barista)")
        print(f"✅ Created: 6 demo orders")


if __name__ == "__main__":
    asyncio.run(init_demo_data())
