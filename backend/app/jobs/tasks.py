

from typing import List, Dict, Any
from datetime import datetime, timedelta
from celery import shared_task
from sqlalchemy import select
from app.models.data_point import DataPoint
from app.services.data_service import data_service
from app.core.notifications import send_notification

@shared_task(
    name="process_data_quality",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def process_data_quality(self):
    """Process and update data quality scores"""
    try:
        # Get recent data points
        async with AsyncSession() as session:
            stmt = select(DataPoint).where(
                DataPoint.created_at >= datetime.utcnow() - timedelta(hours=1)
            )
            result = await session.execute(stmt)
            data_points = result.scalars().all()

            # Process each data point
            for point in data_points:
                quality_score = await data_service.calculate_quality_score(point)
                point.quality = quality_score
                session.add(point)

            await session.commit()

    except Exception as e:
        logger.error(f"Error processing data quality: {str(e)}")
        self.retry(exc=e)

@shared_task(
    name="cleanup_expired_data",
    bind=True
)
def cleanup_expired_data(self):
    """Clean up expired data points"""
    try:
        async with AsyncSession() as session:
            # Get expired data points
            stmt = select(DataPoint).where(
                DataPoint.expires_at <= datetime.utcnow()
            )
            result = await session.execute(stmt)
            expired_points = result.scalars().all()

            # Archive or delete expired points
            for point in expired_points:
                await data_service.archive_data_point(point)

            await session.commit()

    except Exception as e:
        logger.error(f"Error cleaning up expired data: {str(e)}")
        self.retry(exc=e)


@shared_task(
    name="process_notifications",
    bind=True,
    max_retries=3,
    default_retry_delay=30
)
def process_notifications(self, data_point_id: str, subscriptions: List[Dict]):
    """Process notifications for subscribers"""
    try:
        async with AsyncSession() as session:
            # Get data point
            data_point = await data_service.get(session, id=data_point_id)
            if not data_point:
                logger.error(f"Data point {data_point_id} not found")
                return

            # Process each subscription
            for subscription in subscriptions:
                try:
                    # Check if data matches subscription filters
                    if not data_service.matches_filters(data_point, subscription["filters"]):
                        continue

                    # Prepare notification
                    notification = {
                        "type": "data_update",
                        "subscription_id": subscription["id"],
                        "data": {
                            "id": str(data_point.id),
                            "category": data_point.category.value,
                            "timestamp": data_point.created_at.isoformat(),
                            "summary": data_service.generate_summary(data_point)
                        }
                    }

                    # Send notification
                    if subscription.get("webhook_url"):
                        await send_webhook_notification(
                            subscription["webhook_url"],
                            notification
                        )

                    if subscription.get("email"):
                        await send_email_notification(
                            subscription["email"],
                            notification
                        )

                    # Publish to WebSocket
                    await manager.publish(
                        f"data:{data_point.category.value}",
                        notification
                    )

                except Exception as e:
                    logger.error(f"Error processing subscription {subscription['id']}: {str(e)}")
                    continue

    except Exception as e:
        logger.error(f"Error processing notifications: {str(e)}")
        self.retry(exc=e)

@shared_task(
    name="process_data_batch",
    bind=True,
    max_retries=3
)
def process_data_batch(self, batch_id: str):
    """Process a batch of data points"""
    try:
        async with AsyncSession() as session:
            # Get batch
            batch = await data_service.get_batch(session, batch_id)
            if not batch:
                logger.error(f"Batch {batch_id} not found")
                return

            # Process each data point
            for data_point in batch.data_points:
                try:
                    # Validate data
                    validation_result = await data_service.validate_data_point(data_point)
                    if not validation_result["valid"]:
                        logger.warning(
                            f"Data point {data_point.id} validation failed: "
                            f"{validation_result['errors']}"
                        )
                        continue

                    # Process data
                    processed_point = await data_service.process_data_point(data_point)
                    session.add(processed_point)

                    # Get matching subscriptions
                    subscriptions = await data_service.get_matching_subscriptions(
                        session,
                        processed_point
                    )

                    # Queue notifications
                    if subscriptions:
                        process_notifications.delay(
                            str(processed_point.id),
                            [sub.dict() for sub in subscriptions]
                        )

                except Exception as e:
                    logger.error(f"Error processing data point {data_point.id}: {str(e)}")
                    continue

            # Update batch status
            batch.status = "completed"
            batch.processed_at = datetime.utcnow()
            session.add(batch)
            await session.commit()

    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        self.retry(exc=e)

