

"""initial

Revision ID: 001
Revises: 
Create Date: 2024-02-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'))
    )

    # Data points table
    op.create_table(
        'data_points',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('value', postgresql.JSONB, nullable=False),
        sa.Column('quality', sa.String(), nullable=False),
        sa.Column('privacy_level', sa.String(), nullable=False),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'))
    )

    # Subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('filters', postgresql.JSONB),
        sa.Column('notification_url', sa.String()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'))
    )

def downgrade():
    op.drop_table('subscriptions')
    op.drop_table('data_points')
    op.drop_table('users')

# File: backend/app/db/seed.py

import asyncio
from datetime import datetime, timezone
from uuid import uuid4
import json
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models import User, DataPoint, Subscription

async def seed_data():
    async with SessionLocal() as db:
        # Create test users
        users = [
            {
                "id": uuid4(),
                "email": "admin@example.com",
                "hashed_password": get_password_hash("admin123"),
                "full_name": "Admin User",
                "is_superuser": True
            },
            {
                "id": uuid4(),
                "email": "user@example.com",
                "hashed_password": get_password_hash("user123"),
                "full_name": "Test User",
                "is_superuser": False
            }
        ]

        for user_data in users:
            user = User(**user_data)
            db.add(user)

        # Create test data points
        data_points = [
            {
                "id": uuid4(),
                "category": "SENSOR",
                "value": json.dumps({
                    "temperature": 25.5,
                    "humidity": 60
                }),
                "quality": "HIGH",
                "privacy_level": "PUBLIC",
                "metadata": {
                    "location": "Room A",
                    "device_id": "sensor-001"
                }
            },
            {
                "id": uuid4(),
                "category": "BEHAVIORAL",
                "value": json.dumps({
                    "action": "login",
                    "duration": 300
                }),
                "quality": "MEDIUM",
                "privacy_level": "PRIVATE",
                "metadata": {
                    "user_agent": "Mozilla/5.0",
                    "ip_country": "US"
                }
            }
        ]

        for point_data in data_points:
            point = DataPoint(**point_data)
            db.add(point)

        # Create test subscriptions
        subscriptions = [
            {
                "id": uuid4(),
                "user_id": users[0]["id"],
                "category": "SENSOR",
                "filters": {
                    "location": "Room A"
                },
                "notification_url": "https://example.com/webhook"
            },
            {
                "id": uuid4(),
                "user_id": users[1]["id"],
                "category": "BEHAVIORAL",
                "filters": {
                    "action": "login"
                },
                "notification_url": "https://https://example.com/webhook2"
            }
        ]

        for sub_data in subscriptions:
            subscription = Subscription(**sub_data)
            db.add(subscription)

        await db.commit()