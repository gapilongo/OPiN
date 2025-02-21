import asyncio
from app.db.session import SessionLocal
from app.db.seed import seed_data
from app.core.config import settings

async def init_db():
    try:
        db = SessionLocal()
        await db.execute("SELECT 1")  # Test the connection
        print("Database is already initialized")
    except Exception:
        print("Creating database...")
        await create_database()
    
    # Run migrations
    print("Running migrations...")
    import alembic.config
    alembicArgs = [
        '--raiseerr',
        'upgrade', 'head',
    ]
    alembic.config.main(argv=alembicArgs)

    # Seed data only in development environment
    if settings.ENVIRONMENT == "development":
        print("Seeding development data...")
        await seed_data()
    
    print("Database initialization completed")

async def create_database():
    """Create database if it doesn't exist"""
    from sqlalchemy_utils import create_database, database_exists
    if not database_exists(settings.DATABASE_URL):
        create_database(settings.DATABASE_URL)

# File: backend/app/db/base.py

from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

# File: backend/app/db/session.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    future=True,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW
)

SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# File: backend/app/db/repositories/base.py

from typing import Generic, TypeVar, Type, Any, Optional, List, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: Union[UUID, str]) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: Union[UUID, str], obj_in: dict[str, Any]) -> Optional[ModelType]:
        query = update(self.model).where(self.model.id == id).values(**obj_in).returning(self.model)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete(self, id: Union[UUID, str]) -> bool:
        query = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0

# File: backend/app/db/repositories/users.py

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from app.models.user import User
from app.db.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(self.model).where(self.model.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_active_users(self, skip: int = 0, limit: int = 100):
        query = select(self.model).where(self.model.is_active == True).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

# Database initialization script
# File: backend/scripts/init_db.py

import asyncio
import typer
from app.db.init_db import init_db

app = typer.Typer()

@app.command()
def init():
    """Initialize the database."""
    asyncio.run(init_db())

if __name__ == "__main__":
    app()