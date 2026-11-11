"""
Café OS — Simplified Demo (No Database Required)
Full API testing without PostgreSQL dependency
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import uuid4, UUID
import json

app = FastAPI(
    title="Café OS API",
    description="Premium Telegram Ordering Platform",
    version="0.1.0"
)

# ============================================================================
# MODELS (In-Memory)
# ============================================================================

class MenuItem(BaseModel):
    id: str
    name: str
    price: int
    description: str
    category: str

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: int

class Order(BaseModel):
    id: str
    order_number: str
    status: str
    items: List[OrderItem]
    total: int
    created_at: str

class Dashboard(BaseModel):
    total_revenue: int
    total_orders: int
    average_order_value: int
    active_orders: int

# ============================================================================
# IN-MEMORY DATABASE
# ============================================================================

MENU = [
    {"id": "1", "name": "Espresso", "price": 150, "description": "Single shot", "category": "Coffee"},
    {"id": "2", "name": "Flat White", "price": 250, "description": "Espresso with milk foam", "category": "Coffee"},
    {"id": "3", "name": "Cappuccino", "price": 280, "description": "Equal parts espresso and foam", "category": "Coffee"},
    {"id": "4", "name": "Iced Matcha", "price": 320, "description": "Vibrant matcha latte", "category": "Matcha"},
    {"id": "5", "name": "Croissant", "price": 180, "description": "Buttery French croissant", "category": "Bakery"},
    {"id": "6", "name": "Cheesecake", "price": 350, "description": "Basque burnt cheesecake", "category": "Desserts"},
]

ORDERS_DB = {}
STATS = {
    "total_revenue": 550000,
    "total_orders": 5,
    "average_order_value": 110000,
    "active_orders": 2
}

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "ok",
        "version": "0.1.0",
        "environment": "demo",
        "database": "in-memory",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/customer/menu")
async def get_menu(
    organization_id: str = Query(...),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get menu with products"""
    items = MENU

    if category:
        items = [i for i in items if i["category"].lower() == category.lower()]

    if search:
        items = [i for i in items if search.lower() in i["name"].lower()]

    return {
        "categories": ["Coffee", "Tea", "Matcha", "Bakery", "Desserts"],
        "products": items,
        "count": len(items)
    }

class CreateOrderRequest(BaseModel):
    telegram_id: str
    org_id: str
    order_type: str = "takeaway"
    items: Optional[List[dict]] = None

@app.post("/api/v1/customer/orders")
async def create_order(req: CreateOrderRequest):
    """Create new order"""
    order_id = str(uuid4())
    order_number = f"#{str(len(ORDERS_DB) + 1).zfill(6)}"

    total = 0
    order_items = []

    # Mock items if not provided
    items = req.items or [{"product_id": "2", "quantity": 2}]

    for item in items:
        product_id = item.get("product_id")
        product = next((p for p in MENU if p["id"] == product_id), None)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        quantity = item.get("quantity", 1)
        item_total = product["price"] * quantity
        total += item_total

        order_items.append({
            "product_id": product_id,
            "product_name": product["name"],
            "quantity": quantity,
            "unit_price": product["price"]
        })

    order = {
        "id": order_id,
        "order_number": order_number,
        "status": "received",
        "order_type": order_type,
        "items": order_items,
        "subtotal": total,
        "tax": int(total * 0.1),
        "total": total + int(total * 0.1),
        "created_at": datetime.utcnow().isoformat(),
        "ready_eta": (datetime.utcnow() + timedelta(minutes=15)).isoformat()
    }

    ORDERS_DB[order_id] = order
    STATS["total_orders"] += 1
    STATS["total_revenue"] += order["total"]

    return order

@app.get("/api/v1/customer/orders/{order_id}")
async def get_order(
    order_id: str,
    telegram_id: str = Query(...),
    org_id: str = Query(...)
):
    """Get order details"""
    order = ORDERS_DB.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

@app.get("/api/v1/customer/orders/{order_id}/tracking-widget")
async def get_tracking_widget(
    order_id: str,
    telegram_id: str = Query(...),
    org_id: str = Query(...)
):
    """Get HTML tracking widget"""
    order = ORDERS_DB.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Return HTML widget
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Order Tracking</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI'; background: #f5f1e8; padding: 20px; }}
            .container {{ background: white; padding: 20px; border-radius: 12px; max-width: 500px; margin: 0 auto; }}
            .order-number {{ font-size: 32px; font-weight: bold; color: #241813; }}
            .status {{ color: #95877d; margin: 10px 0; }}
            .timeline {{ margin: 20px 0; }}
            .step {{ padding: 10px; margin: 5px 0; background: #f7f2e9; border-radius: 8px; }}
            .step.active {{ background: #c58b58; color: white; }}
            .total {{ font-size: 20px; font-weight: bold; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="order-number">#{order['order_number']}</div>
            <div class="status">Status: {order['status'].upper()}</div>
            <div class="timeline">
                <div class="step {'active' if order['status'] in ['received', 'confirmed', 'preparing', 'almost_ready', 'ready', 'completed'] else ''}">01 - ORDER RECEIVED ✓</div>
                <div class="step {'active' if order['status'] in ['confirmed', 'preparing', 'almost_ready', 'ready', 'completed'] else ''}">02 - CONFIRMED {'✓' if order['status'] != 'received' else ''}</div>
                <div class="step {'active' if order['status'] in ['preparing', 'almost_ready', 'ready', 'completed'] else ''}">03 - PREPARING ☕</div>
                <div class="step {'active' if order['status'] in ['almost_ready', 'ready', 'completed'] else ''}">04 - ALMOST READY ⏱</div>
                <div class="step {'active' if order['status'] in ['ready', 'completed'] else ''}">05 - READY 🎉</div>
                <div class="step {'active' if order['status'] == 'completed' else ''}">06 - COMPLETED ✓</div>
            </div>
            <div class="total">Total: ₽{order['total'] / 100:.2f}</div>
            <p style="color: #95877d; font-size: 12px;">Ready in 15 min</p>
        </div>
    </body>
    </html>
    """

    return {"html": html, "order_id": order_id, "status": order["status"]}

@app.get("/api/v1/admin/dashboard")
async def admin_dashboard(org_id: str = Query(...)):
    """Admin dashboard"""
    return STATS

@app.get("/api/v1/admin/orders")
async def admin_orders(
    org_id: str = Query(...),
    status: Optional[str] = Query(None),
    limit: int = Query(10)
):
    """List admin orders"""
    orders = list(ORDERS_DB.values())

    if status:
        orders = [o for o in orders if o["status"] == status]

    return {"orders": orders[:limit], "count": len(orders)}

@app.patch("/api/v1/admin/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    new_status: str = Query(...),
    org_id: str = Query(...)
):
    """Update order status"""
    order = ORDERS_DB.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order["status"]
    order["status"] = new_status
    order["updated_at"] = datetime.utcnow().isoformat()

    return {
        "id": order_id,
        "old_status": old_status,
        "new_status": new_status,
        "updated_at": order["updated_at"]
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": "Café OS",
        "version": "0.1.0",
        "status": "🚀 LIVE",
        "docs": "/docs",
        "endpoints": {
            "menu": "/api/v1/customer/menu",
            "create_order": "/api/v1/customer/orders",
            "track_order": "/api/v1/customer/orders/{order_id}/tracking-widget",
            "dashboard": "/api/v1/admin/dashboard",
            "admin_orders": "/api/v1/admin/orders"
        }
    }

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    print("🎯 Café OS — Demo Server Starting")
    print("📊 In-Memory Database Ready")
    print("🚀 API Server Running on http://localhost:8000")
    print("📖 Docs available at http://localhost:8000/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
