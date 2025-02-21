
from typing import Optional, List, Union, Dict, Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from backend.app.crud.base import CRUDBase

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    # ... (previous methods remain the same)

    async def delete(self, db: AsyncSession, *, id: UUID) -> Optional[User]:
        """
        Hard delete a user and all related data.
        Use with caution as this will permanently remove the user and all associated data.
        """
        user = await super().delete(db=db, id=id)
        if user:
            # Optionally: Add cleanup of related data
            # This could include deleting associated subscriptions, API keys, etc.
            await db.execute(delete(self.model).where(self.model.id == id))
            await db.commit()
        return user

    async def soft_delete(self, db: AsyncSession, *, id: UUID) -> Optional[User]:
        """
        Soft delete a user by setting is_active to False.
        This is the preferred method for "deleting" users as it preserves data integrity.
        """
        return await super().soft_delete(db=db, id=id)

    async def remove_with_related_data(self, db: AsyncSession, *, id: UUID) -> bool:
        """
        Completely remove a user and all related data.
        This is a dangerous operation and should only be used when absolutely necessary.
        """
        user = await self.get(db=db, id=id)
        if not user:
            return False

        try:
            # Delete related subscriptions
            await db.execute(delete(User.subscriptions).where(
                User.subscriptions.user_id == id
            ))

            # Delete API keys
            await db.execute(delete(User.api_keys).where(
                User.api_keys.user_id == id
            ))

            # Delete data points
            await db.execute(delete(User.data_points).where(
                User.data_points.creator_id == id
            ))

            # Finally, delete the user
            await db.execute(delete(User).where(User.id == id))
            
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            raise e

    async def bulk_delete(
        self, 
        db: AsyncSession, 
        *, 
        ids: List[UUID], 
        soft: bool = True
    ) -> Dict[UUID, bool]:
        """
        Delete multiple users at once.
        Returns a dictionary mapping user IDs to deletion success status.
        """
        results = {}
        for user_id in ids:
            try:
                if soft:
                    user = await self.soft_delete(db=db, id=user_id)
                else:
                    user = await self.delete(db=db, id=user_id)
                results[user_id] = bool(user)
            except Exception:
                results[user_id] = False
                await db.rollback()

        await db.commit()
        return results

user = CRUDUser(User)