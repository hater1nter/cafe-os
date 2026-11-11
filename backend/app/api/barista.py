from fastapi import APIRouter

router = APIRouter(prefix="/barista")


@router.get("/queue")
async def get_queue():
    """Get queue of orders for barista"""
    return {"queue": [], "status": "stub"}


@router.patch("/order/{order_id}/start")
async def start_preparing(order_id: str):
    """Mark order as preparation started"""
    return {"order_id": order_id, "status": "started"}


@router.patch("/order/{order_id}/ready")
async def mark_ready(order_id: str):
    """Mark order as ready"""
    return {"order_id": order_id, "status": "ready"}


@router.patch("/order/{order_id}/complete")
async def complete_order(order_id: str):
    """Mark order as completed"""
    return {"order_id": order_id, "status": "completed"}
