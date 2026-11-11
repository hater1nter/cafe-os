from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import structlog
import json
from uuid import UUID

from app.config import settings
from app.database import async_session_maker
from app.models import User, Organization, Product, Category, Order, LoyaltyAccount
from app.services.payment import PaymentService

logger = structlog.get_logger()

# Initialize bot and dispatcher
bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()


class OrderState(StatesGroup):
    """FSM states for order flow"""
    selecting_branch = State()
    selecting_category = State()
    selecting_product = State()
    customizing_product = State()
    reviewing_cart = State()
    checkout = State()


async def set_bot_commands():
    """Set bot commands menu"""
    commands = [
        BotCommand(command="start", description="Start ordering"),
        BotCommand(command="menu", description="View menu"),
        BotCommand(command="orders", description="My orders"),
        BotCommand(command="loyalty", description="Loyalty card"),
        BotCommand(command="help", description="Help & support"),
    ]
    await bot.set_my_commands(commands)


@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    """Handle /start command - show greeting"""
    telegram_id = str(message.from_user.id)
    user_name = message.from_user.full_name or "Friend"

    # TODO: Determine organization from bot token
    # For now, use MONO COFFEE demo
    org_id = "00000000-0000-0000-0000-000000000001"  # Demo org ID

    async with async_session_maker() as session:
        # Get or create user
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            # Create new user
            user = User(
                telegram_id=telegram_id,
                full_name=user_name,
                preferred_language="en"
            )
            session.add(user)
            await session.flush()

            # Create loyalty account
            loyalty = LoyaltyAccount(
                user_id=user.id,
                organization_id=UUID(org_id)
            )
            session.add(loyalty)

            await session.commit()
            logger.info("new_user_created", telegram_id=telegram_id)
        else:
            user.last_seen = datetime.utcnow()
            await session.commit()

    # Build greeting message with inline buttons
    greeting_text = f"""☕ Good morning, {user_name}!

Your daily coffee ritual starts here.

Freshly brewed. Made just for you.

MONO COFFEE — Premium Urban Coffee Shop"""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 ORDER NOW",
                    callback_data="order_start"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 VIEW MENU",
                    callback_data="menu_view"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👤 MY PROFILE",
                    callback_data="profile_view"
                )
            ],
        ]
    )

    await message.answer(greeting_text, reply_markup=keyboard)


@dp.message(Command("menu"))
async def menu_handler(message: types.Message, state: FSMContext):
    """Handle /menu command - show menu"""
    telegram_id = str(message.from_user.id)
    org_id = "00000000-0000-0000-0000-000000000001"  # Demo

    async with async_session_maker() as session:
        # Get categories and products
        categories_result = await session.execute(
            select(Category).where(
                Category.organization_id == UUID(org_id),
                Category.is_active == True
            ).order_by(Category.display_order)
        )
        categories = categories_result.scalars().all()

        if not categories:
            await message.answer("❌ Menu not available")
            return

        # Show menu header
        await message.answer(
            "☕ MONO COFFEE Menu\n\nSelect a category:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"📍 {cat.name}",
                        callback_data=f"category:{cat.id}"
                    )]
                    for cat in categories
                ]
            )
        )


@dp.message(Command("orders"))
async def orders_handler(message: types.Message):
    """Handle /orders command - show order history"""
    telegram_id = str(message.from_user.id)
    org_id = "00000000-0000-0000-0000-000000000001"  # Demo

    async with async_session_maker() as session:
        # Get user's orders
        orders_result = await session.execute(
            select(Order).where(
                Order.user_id == User.id,
                User.telegram_id == telegram_id,
                Order.organization_id == UUID(org_id)
            ).order_by(Order.created_at.desc()).limit(5)
        )
        orders = orders_result.scalars().all()

        if not orders:
            await message.answer("📭 No orders yet. Start ordering with /menu")
            return

        orders_text = "📦 Your Recent Orders:\n\n"
        for order in orders:
            orders_text += f"Order #{order.order_number}\n"
            orders_text += f"Status: {order.status.upper()}\n"
            orders_text += f"Total: ₽{order.total / 100:.2f}\n"
            orders_text += f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"

        await message.answer(orders_text)


@dp.message(Command("loyalty"))
async def loyalty_handler(message: types.Message):
    """Handle /loyalty command - show loyalty card"""
    telegram_id = str(message.from_user.id)
    org_id = "00000000-0000-0000-0000-000000000001"  # Demo

    async with async_session_maker() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            await message.answer("👤 Please start with /start first")
            return

        loyalty_result = await session.execute(
            select(LoyaltyAccount).where(
                LoyaltyAccount.user_id == user.id,
                LoyaltyAccount.organization_id == UUID(org_id)
            )
        )
        loyalty = loyalty_result.scalar_one_or_none()

        if not loyalty:
            await message.answer("❌ Loyalty account not found")
            return

        loyalty_text = f"""💳 Your Loyalty Card

Tier: {loyalty.tier.upper()}
Points: {loyalty.points_balance} 🏅

🎁 Rewards:
- Bronze: 1 point per ruble
- Silver (500 pts): +1 bonus point
- Gold (1000 pts): +2 bonus points
- Black (2000 pts): VIP status

Your points are automatically earned with every purchase!"""

        await message.answer(loyalty_text)


@dp.message(Command("help"))
async def help_handler(message: types.Message):
    """Handle /help command"""
    help_text = """🆘 Help & Support

Commands:
/start - Start ordering
/menu - View menu
/orders - My orders
/loyalty - Loyalty card
/help - This help message

How to order:
1. Select /menu
2. Choose category and product
3. Customize your drink
4. Review cart
5. Checkout and pay

Need help? Contact us: support@monoco ffee.local"""

    await message.answer(help_text)


@dp.callback_query(F.data == "order_start")
async def order_start_callback(query: types.CallbackQuery, state: FSMContext):
    """Start order flow"""
    await query.answer("Starting order...")
    await query.message.edit_text(
        "🏪 Select your location:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📍 MONO COFFEE Main", callback_data="branch:main")],
            ]
        )
    )
    await state.set_state(OrderState.selecting_branch)


@dp.callback_query(F.data.startswith("category:"))
async def category_callback(query: types.CallbackQuery, state: FSMContext):
    """Show products in category"""
    category_id = query.data.split(":")[1]
    org_id = "00000000-0000-0000-0000-000000000001"  # Demo

    async with async_session_maker() as session:
        products_result = await session.execute(
            select(Product).where(
                Product.category_id == UUID(category_id),
                Product.is_available == True,
                Product.organization_id == UUID(org_id)
            ).order_by(Product.display_order)
        )
        products = products_result.scalars().all()

        if not products:
            await query.answer("No products in this category")
            return

        products_text = "Select a product:\n\n"
        for prod in products:
            products_text += f"💰 ₽{prod.price / 100:.2f}\n"

        await query.message.edit_text(
            products_text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"{prod.name}",
                        callback_data=f"product:{prod.id}"
                    )]
                    for prod in products
                ]
            )
        )


@dp.callback_query(F.data == "menu_view")
async def menu_view_callback(query: types.CallbackQuery):
    """Show menu categories"""
    org_id = "00000000-0000-0000-0000-000000000001"  # Demo

    async with async_session_maker() as session:
        categories_result = await session.execute(
            select(Category).where(
                Category.organization_id == UUID(org_id),
                Category.is_active == True
            ).order_by(Category.display_order)
        )
        categories = categories_result.scalars().all()

        await query.message.edit_text(
            "📋 Menu Categories\n\nSelect category:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"📍 {cat.name}",
                        callback_data=f"category:{cat.id}"
                    )]
                    for cat in categories
                ]
            )
        )


@dp.callback_query(F.data == "profile_view")
async def profile_view_callback(query: types.CallbackQuery):
    """Show user profile"""
    telegram_id = str(query.from_user.id)

    async with async_session_maker() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            await query.answer("User not found")
            return

        profile_text = f"""👤 Your Profile

Name: {user.full_name or 'Not set'}
Phone: {user.phone or 'Not set'}
Email: {user.email or 'Not set'}
Member since: {user.registration_date.strftime('%B %Y')}

📊 Stats:
Orders: 0
Total spent: ₽0.00"""

        await query.message.edit_text(profile_text)


async def setup_bot():
    """Setup bot before starting"""
    await set_bot_commands()
    logger.info("bot_setup_complete", bot_token=settings.telegram_bot_token[:10] + "...")
