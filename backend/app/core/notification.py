

import aiohttp
import asyncio
from typing import Dict, Any
import logging
from app.core.config import settings
from app.core.email import send_email

logger = logging.getLogger(__name__)

async def send_webhook_notification(url: str, data: Dict[str, Any]) -> bool:
    """Send webhook notification"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"OPiN-Notifications/{settings.VERSION}"
                }
            ) as response:
                if response.status != 200:
                    logger.error(
                        f"Webhook notification failed. Status: {response.status}, "
                        f"Response: {await response.text()}"
                    )
                    return False
                return True
    except Exception as e:
        logger.error(f"Error sending webhook notification: {str(e)}")
        return False

async def send_email_notification(email: str, data: Dict[str, Any]) -> bool:
    """Send email notification"""
    try:
        subject = f"OPiN Notification: {data['type']}"
        
        # Generate email content
        content = f"""
        New {data['type']} notification:
        
        Category: {data['data']['category']}
        Timestamp: {data['data']['timestamp']}
        
        Summary:
        {data['data']['summary']}
        
        View details in your dashboard:
        {settings.FRONTEND_URL}/dashboard
        
        ---
        You're receiving this because you subscribed to these notifications.
        To unsubscribe, visit your subscription settings.
        """

        await send_email(
            to_email=email,
            subject=subject,
            content=content
        )
        return True
    except Exception as e:
        logger.error(f"Error sending email notification: {str(e)}")
        return False