from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models import (
    OrderStatusEnum, OrderTypeEnum, PaymentStatusEnum,
    LoyaltyTierEnum, StaffRoleEnum
)


# Organization Schemas
class OrganizationBase(BaseModel):
    name: str
    slug: str
    branding: Optional[Dict[str, Any]] = None


class OrganizationCreate(OrganizationBase):
    telegram_bot_token: str


class OrganizationResponse(OrganizationBase):
    id: UUID
    subscription_tier: str
    payment_provider: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Branch Schemas
class BranchBase(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None
    operating_hours: Optional[Dict[str, Any]] = None


class BranchCreate(BranchBase):
    organization_id: UUID


class BranchResponse(BranchBase):
    id: UUID
    organization_id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    preferred_language: str = "en"


class UserCreate(UserBase):
    telegram_id: str
    organization_id: UUID


class UserResponse(UserBase):
    id: UUID
    telegram_id: str
    organization_id: UUID
    registration_date: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    display_order: int = 0


class CategoryCreate(CategoryBase):
    organization_id: UUID


class CategoryResponse(CategoryBase):
    id: UUID
    organization_id: UUID
    is_active: bool

    class Config:
        from_attributes = True


# Modifier Schemas
class ModifierOptionBase(BaseModel):
    name: str
    price_delta: int = 0  # in cents


class ModifierBase(BaseModel):
    name: str
    type: str  # single_choice, multiple_choice
    options: List[ModifierOptionBase]
    is_required: bool = False
    display_order: int = 0


class ModifierCreate(ModifierBase):
    product_id: UUID


class ModifierResponse(ModifierBase):
    id: UUID
    product_id: UUID

    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int  # in cents
    image_url: Optional[str] = None
    nutritional_info: Optional[Dict[str, Any]] = None
    allergens: List[str] = []
    display_order: int = 0


class ProductCreate(ProductBase):
    organization_id: UUID
    category_id: Optional[UUID] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    image_url: Optional[str] = None
    nutritional_info: Optional[Dict[str, Any]] = None
    allergens: Optional[List[str]] = None
    is_available: Optional[bool] = None
    display_order: Optional[int] = None


class ProductResponse(ProductBase):
    id: UUID
    organization_id: UUID
    category_id: Optional[UUID] = None
    is_available: bool
    is_seasonal: bool
    created_at: datetime
    modifiers: List[ModifierResponse] = []

    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    modifiers: List[ModifierResponse] = []


# Order Item Schemas
class OrderItemModifier(BaseModel):
    modifier_id: UUID
    selected_option: str
    price_delta: int = 0


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int
    modifiers: List[OrderItemModifier] = []


class OrderItemResponse(BaseModel):
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: int
    total_price: int
    modifiers: List[OrderItemModifier] = []


# Order Schemas
class OrderBase(BaseModel):
    order_type: OrderTypeEnum
    branch_id: UUID
    table_number: Optional[str] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderResponse(OrderBase):
    id: UUID
    order_number: str
    organization_id: UUID
    user_id: UUID
    status: OrderStatusEnum
    items: List[OrderItemResponse]
    subtotal: int
    tax: int
    discount: int
    total: int
    payment_status: PaymentStatusEnum
    estimated_time: int
    ready_eta: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    payment_method: Optional[str] = None


# Order Status Update
class OrderStatusUpdate(BaseModel):
    status: OrderStatusEnum
    reason: Optional[str] = None


# Loyalty Schemas
class LoyaltyAccountResponse(BaseModel):
    id: UUID
    user_id: UUID
    tier: LoyaltyTierEnum
    points_balance: int
    created_at: datetime

    class Config:
        from_attributes = True


class LoyaltyTransactionResponse(BaseModel):
    id: UUID
    transaction_type: str
    amount: int
    created_at: datetime

    class Config:
        from_attributes = True


# Staff Schemas
class StaffBase(BaseModel):
    name: str
    email: Optional[str] = None
    role: StaffRoleEnum
    permissions: List[str] = []


class StaffCreate(StaffBase):
    organization_id: UUID
    branch_id: Optional[UUID] = None
    password: Optional[str] = None


class StaffResponse(StaffBase):
    id: UUID
    organization_id: UUID
    branch_id: Optional[UUID] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Payment Schemas
class PaymentStatusResponse(BaseModel):
    payment_id: str
    status: PaymentStatusEnum
    created_at: datetime


class PaymentCreateRequest(BaseModel):
    order_id: UUID


# Auth Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthRequest(BaseModel):
    email: str
    password: str


# Health Check
class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


# Menu Response (for customer)
class MenuResponse(BaseModel):
    categories: List[CategoryResponse]
    products: List[ProductDetailResponse]


# Dashboard Stats
class DashboardStatsResponse(BaseModel):
    total_revenue: int  # in cents
    total_orders: int
    average_order_value: int  # in cents
    active_orders: int
    popular_items: List[Dict[str, Any]]
    revenue_chart: List[Dict[str, Any]]
