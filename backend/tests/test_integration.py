"""
Integration tests for Café OS
Tests complete order flow from creation to delivery
"""

import pytest
import httpx
from uuid import uuid4
from datetime import datetime, timedelta
import asyncio

BASE_URL = "http://localhost:8000/api/v1"
ORG_ID = "00000000-0000-0000-0000-000000000001"  # Demo org


@pytest.fixture
def client():
    """HTTP client for API testing"""
    return httpx.AsyncClient(base_url=BASE_URL, timeout=10.0)


@pytest.fixture
async def demo_order():
    """Create demo order for testing"""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Create order
        response = await client.post(
            "/customer/orders",
            json={
                "order_type": "takeaway",
                "branch_id": "00000000-0000-0000-0000-000000000002",
                "items": [
                    {
                        "product_id": "00000000-0000-0000-0000-000000000010",
                        "quantity": 1,
                        "modifiers": []
                    }
                ]
            },
            params={
                "telegram_id": "test_user_1",
                "organization_id": ORG_ID
            }
        )
        assert response.status_code == 200
        return response.json()


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_get_menu(client):
    """Test getting menu"""
    response = await client.get(
        "/customer/menu",
        params={"organization_id": ORG_ID}
    )
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "products" in data


@pytest.mark.asyncio
async def test_create_order(client):
    """Test order creation"""
    response = await client.post(
        "/customer/orders",
        json={
            "order_type": "takeaway",
            "branch_id": "00000000-0000-0000-0000-000000000002",
            "items": [
                {
                    "product_id": "00000000-0000-0000-0000-000000000010",
                    "quantity": 2,
                    "modifiers": []
                }
            ]
        },
        params={
            "telegram_id": "test_user_integration",
            "organization_id": ORG_ID
        }
    )
    assert response.status_code == 200
    order = response.json()
    assert order["order_type"] == "takeaway"
    assert len(order["items"]) == 1
    assert order["items"][0]["quantity"] == 2
    assert order["status"] == "received"
    return order


@pytest.mark.asyncio
async def test_get_order_status(client, demo_order):
    """Test getting order status"""
    order_id = demo_order["id"]
    response = await client.get(
        f"/customer/orders/{order_id}",
        params={
            "telegram_id": "test_user_1",
            "organization_id": ORG_ID
        }
    )
    assert response.status_code == 200
    order = response.json()
    assert order["id"] == order_id
    assert order["status"] in ["received", "confirmed", "preparing", "almost_ready", "ready", "completed"]


@pytest.mark.asyncio
async def test_get_tracking_widget(client, demo_order):
    """Test getting HTML tracking widget"""
    order_id = demo_order["id"]
    response = await client.get(
        f"/customer/orders/{order_id}/tracking-widget",
        params={
            "telegram_id": "test_user_1",
            "organization_id": ORG_ID
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "html" in data
    assert len(data["html"]) > 100
    assert "tracking" in data["html"].lower()


@pytest.mark.asyncio
async def test_admin_dashboard(client):
    """Test admin dashboard endpoint"""
    response = await client.get(
        "/admin/dashboard",
        params={"organization_id": ORG_ID}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "total_orders" in data
    assert "active_orders" in data


@pytest.mark.asyncio
async def test_admin_list_orders(client):
    """Test admin list orders"""
    response = await client.get(
        "/admin/orders",
        params={"organization_id": ORG_ID}
    )
    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert "count" in data


@pytest.mark.asyncio
async def test_payment_flow():
    """Test complete payment flow"""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Create order
        order_response = await client.post(
            "/customer/orders",
            json={
                "order_type": "takeaway",
                "branch_id": "00000000-0000-0000-0000-000000000002",
                "items": [
                    {
                        "product_id": "00000000-0000-0000-0000-000000000010",
                        "quantity": 1,
                        "modifiers": []
                    }
                ]
            },
            params={
                "telegram_id": "payment_test_user",
                "organization_id": ORG_ID
            }
        )
        assert order_response.status_code == 200
        order = order_response.json()

        # Initialize payment
        payment_response = await client.post(
            f"/customer/orders/{order['id']}/checkout",
            params={
                "telegram_id": "payment_test_user",
                "organization_id": ORG_ID,
                "return_url": "http://localhost:8000/checkout/success"
            }
        )
        assert payment_response.status_code == 200
        payment_data = payment_response.json()
        assert "payment_id" in payment_data
        assert "redirect_url" in payment_data


@pytest.mark.asyncio
async def test_order_status_update():
    """Test order status update from admin"""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Create order
        order_response = await client.post(
            "/customer/orders",
            json={
                "order_type": "takeaway",
                "branch_id": "00000000-0000-0000-0000-000000000002",
                "items": [
                    {
                        "product_id": "00000000-0000-0000-0000-000000000010",
                        "quantity": 1,
                        "modifiers": []
                    }
                ]
            },
            params={
                "telegram_id": "status_test_user",
                "organization_id": ORG_ID
            }
        )
        order_id = order_response.json()["id"]

        # Update status
        update_response = await client.patch(
            f"/admin/orders/{order_id}/status",
            params={
                "organization_id": ORG_ID,
                "new_status": "confirmed"
            }
        )
        assert update_response.status_code == 200
        updated_order = update_response.json()
        assert updated_order["status"] == "confirmed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
