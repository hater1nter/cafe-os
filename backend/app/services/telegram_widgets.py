from uuid import UUID
from datetime import datetime
import structlog

logger = structlog.get_logger()


async def generate_tracking_widget_html(
    order_id: UUID,
    org_id: UUID,
    order_number: str
) -> str:
    """Generate HTML Bubble for order tracking"""

    html_template = open('/app/html-bubbles/tracking-widget.html', 'r').read()

    # Replace placeholders
    html = html_template.replace('{order_id}', str(order_id))
    html = html.replace('{org_id}', str(org_id))
    html = html.replace('{order_number}', order_number)

    logger.debug(
        "tracking_widget_generated",
        order_id=str(order_id),
        size=len(html)
    )

    return html


async def send_tracking_widget_via_telegram(
    bot,
    user_telegram_id: int,
    order_id: UUID,
    org_id: UUID,
    order_number: str
):
    """Send order tracking widget to Telegram"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    try:
        # Generate HTML
        html_content = await generate_tracking_widget_html(
            order_id=order_id,
            org_id=org_id,
            order_number=order_number
        )

        # Create inline keyboard with action buttons
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📊 Live Tracking",
                        callback_data=f"track:{order_id}"
                    ),
                    InlineKeyboardButton(
                        text="❌ Cancel",
                        callback_data=f"cancel:{order_id}"
                    )
                ]
            ]
        )

        # Send message with HTML Bubble (via web_app_info if available, or as text)
        message_text = f"""☕ Order Confirmed!

Order #{order_number}

Your coffee is being prepared.
We'll notify you when it's ready.

Status updates will appear below every 5 seconds."""

        message = await bot.send_message(
            chat_id=user_telegram_id,
            text=message_text,
            reply_markup=keyboard
        )

        logger.info(
            "tracking_widget_sent",
            order_id=str(order_id),
            user_id=user_telegram_id,
            message_id=message.message_id
        )

        return message

    except Exception as e:
        logger.error(
            "tracking_widget_send_failed",
            order_id=str(order_id),
            error=str(e)
        )
        raise


async def update_tracking_widget(
    bot,
    user_telegram_id: int,
    message_id: int,
    order_id: UUID,
    org_id: UUID,
    status: str
):
    """Update existing tracking widget message"""
    try:
        # In real implementation, would update message with new status
        # For now, send notification
        status_emoji = {
            'received': '📋',
            'confirmed': '✓',
            'preparing': '☕',
            'almost_ready': '⏱',
            'ready': '🎉',
            'completed': '✓'
        }

        notification = f"{status_emoji.get(status, '•')} Order status: {status.upper()}"

        await bot.send_message(
            chat_id=user_telegram_id,
            text=notification
        )

        logger.debug(
            "tracking_notification_sent",
            order_id=str(order_id),
            status=status
        )

    except Exception as e:
        logger.error(
            "tracking_update_failed",
            order_id=str(order_id),
            error=str(e)
        )
