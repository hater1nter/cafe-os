from sqlalchemy import Column, String, UUID, DateTime, Integer, Float, JSON, Boolean, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid

from app.database import Base


class OrderStatusEnum(str, enum.Enum):
    RECEIVED = "received"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    ALMOST_READY = "almost_ready"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderTypeEnum(str, enum.Enum):
    TAKEAWAY = "takeaway"
    DINE_IN = "dine_in"
    DELIVERY = "delivery"


class PaymentStatusEnum(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class LoyaltyTierEnum(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    BLACK = "black"


class StaffRoleEnum(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    BARISTA = "barista"
    CUSTOMER_SUPPORT = "customer_support"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)

    # Branding
    branding = Column(JSON, default={
        "primary_color": "#241813",
        "secondary_color": "#C58B58",
        "accent_color": "#9AA58C",
        "logo_url": None,
        "font_family": "Inter"
    })

    # Subscription
    subscription_tier = Column(String(50), default="starter")  # starter, pro, business, enterprise

    # Telegram
    telegram_bot_token = Column(String(255), nullable=True, unique=True)

    # Payment provider (can switch between providers)
    payment_provider = Column(String(50), default="yandex_kassa")  # yandex_kassa, yukassa, sberpay

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    branches = relationship("Branch", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="organization", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="organization", cascade="all, delete-orphan")
    staff = relationship("Staff", back_populates="organization", cascade="all, delete-orphan")
    loyalty_accounts = relationship("LoyaltyAccount", back_populates="organization", cascade="all, delete-orphan")


class Branch(Base):
    __tablename__ = "branches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)

    # Operating hours
    operating_hours = Column(JSON, default={
        "monday": {"open": "08:00", "close": "20:00"},
        "tuesday": {"open": "08:00", "close": "20:00"},
        "wednesday": {"open": "08:00", "close": "20:00"},
        "thursday": {"open": "08:00", "close": "20:00"},
        "friday": {"open": "08:00", "close": "20:00"},
        "saturday": {"open": "09:00", "close": "21:00"},
        "sunday": {"open": "09:00", "close": "21:00"}
    })

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="branches")
    orders = relationship("Order", back_populates="branch")
    staff = relationship("Staff", back_populates="branch")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    telegram_id = Column(String(255), nullable=False, index=True)

    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)

    preferred_language = Column(String(10), default="en")

    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), nullable=True)

    is_active = Column(Boolean, default=True)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    orders = relationship("Order", back_populates="user")
    loyalty_account = relationship("LoyaltyAccount", back_populates="user", uselist=False)


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # in cents

    image_url = Column(String(500), nullable=True)

    # Nutritional info
    nutritional_info = Column(JSON, nullable=True)  # calories, fat, protein, carbs
    allergens = Column(JSON, default=[])

    is_available = Column(Boolean, default=True)
    is_seasonal = Column(Boolean, default=False)

    display_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="products")
    modifiers = relationship("Modifier", back_populates="product", cascade="all, delete-orphan")


class Modifier(Base):
    __tablename__ = "modifiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)  # "Milk Type", "Extra Shot", "Size"
    type = Column(String(50), nullable=False)  # single_choice, multiple_choice

    # Options: [{name: "Oat Milk", price_delta: 50}, ...]
    options = Column(JSON, nullable=False, default=[])

    is_required = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)

    # Relationships
    product = relationship("Product", back_populates="modifiers")


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False, index=True)

    order_number = Column(String(50), nullable=False, index=True)  # Display-friendly: #001234

    status = Column(SQLEnum(OrderStatusEnum), default=OrderStatusEnum.RECEIVED, index=True)
    order_type = Column(SQLEnum(OrderTypeEnum), nullable=False)

    table_number = Column(String(50), nullable=True)  # For dine_in

    # Items: [{product_id, quantity, modifiers: {...}, unit_price}]
    items = Column(JSON, nullable=False)

    subtotal = Column(Integer, nullable=False)  # in cents
    tax = Column(Integer, default=0)
    discount = Column(Integer, default=0)
    total = Column(Integer, nullable=False)  # in cents

    payment_status = Column(SQLEnum(PaymentStatusEnum), default=PaymentStatusEnum.PENDING, index=True)
    payment_method = Column(String(50), nullable=True)  # telegram_payment, card, cash
    payment_provider_transaction_id = Column(String(255), nullable=True)

    notes = Column(Text, nullable=True)

    estimated_time = Column(Integer, default=15)  # minutes
    ready_eta = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="orders")
    user = relationship("User", back_populates="orders")
    branch = relationship("Branch", back_populates="orders")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)

    status = Column(SQLEnum(OrderStatusEnum), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    changed_by = Column(String(255), nullable=True)  # staff_id or "system"
    reason = Column(String(255), nullable=True)

    # Relationships
    order = relationship("Order", back_populates="status_history")


class LoyaltyAccount(Base):
    __tablename__ = "loyalty_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)

    tier = Column(SQLEnum(LoyaltyTierEnum), default=LoyaltyTierEnum.BRONZE)
    points_balance = Column(Integer, default=0)

    last_reset_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="loyalty_account")
    organization = relationship("Organization", back_populates="loyalty_accounts")
    transactions = relationship("LoyaltyTransaction", back_populates="loyalty_account", cascade="all, delete-orphan")


class LoyaltyTransaction(Base):
    __tablename__ = "loyalty_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loyalty_account_id = Column(UUID(as_uuid=True), ForeignKey("loyalty_accounts.id"), nullable=False, index=True)

    transaction_type = Column(String(50), nullable=False)  # purchase, redemption, bonus, refund
    amount = Column(Integer, nullable=False)
    reference_id = Column(String(255), nullable=True)  # order_id or promo_id

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    loyalty_account = relationship("LoyaltyAccount", back_populates="transactions")


class Staff(Base):
    __tablename__ = "staff"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=True, index=True)

    telegram_id = Column(String(255), nullable=True, unique=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, unique=True)

    password_hash = Column(String(255), nullable=True)  # For web dashboard access

    role = Column(SQLEnum(StaffRoleEnum), nullable=False)
    permissions = Column(JSON, default=[])  # Array of permission strings

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="staff")
    branch = relationship("Branch", back_populates="staff")
