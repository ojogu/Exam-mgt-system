from sqlalchemy.ext.asyncio import AsyncSession
from src.v1.model import User
from sqlalchemy import select
from src.v1.base.exception import (
    NotFoundError, 
    AlreadyExistsError
)
class UserService():
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_user(self, **user_data:dict): 
        user = await self.check_if_user_exist_by_email(user_data["email"]) or await self.check_if_user_exist_by_school_id(user_data["school_id"])
        
        if user:
            raise AlreadyExistsError(f"{user.id} already exist")
        
        #do further authentication 
        
        
        
    
    async def check_if_user_exist_by_email(self, email:str):
        stmt = await self.db.execute(
            select(User).where(
                email==User.email
            )
        )
        user = stmt.scalar_one_or_none()
        return user
    
    async def check_if_user_exist_by_school_id(self, school_id:str):
        stmt = await self.db.execute(
            select(User).where(
                school_id == User.school_id
            )
        ) 
        user = stmt.scalar_one_or_none()
        return user
    
    async def update_user():
        pass 
    
    async def delete_user():
        pass 