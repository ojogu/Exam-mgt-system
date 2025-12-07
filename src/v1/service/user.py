from sqlalchemy.ext.asyncio import AsyncSession
from src.v1.model import User
from sqlalchemy import select
from src.v1.schema.user import CreateUser
from src.v1.base.exception import (
    NotFoundError, 
    AlreadyExistsError,
    ServerError
)
from src.v1.auth.service import verify_hash, password_hash
from src.util.log import setup_logger
logger = setup_logger(__name__, "user_service.log")

class UserService():
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_user(self, user_data:CreateUser): 
        try:
            validated_data = CreateUser(user_data)
            logger.info(f"Attempting to create user with email: {validated_data.email} and school_id: {validated_data.school_id}")
            user = await self.check_if_user_exist_by_email(validated_data.email) or await self.check_if_user_exist_by_school_id(validated_data.school_id)
            
            if user:
                logger.warning(f"User with ID {user.id} already exists.")
                raise AlreadyExistsError(f"User with ID {user.id} already exist")
            
            password = password_hash(validated_data.password)
            
            #seed department, link users to dept both lecturer and student(link level too)
            new_user = User(
                **validated_data.model_dump()
            )
            validated_data.password = password
            self.db.add(new_user)
            await self.db.commit()
            logger.info(f"User {new_user.id} created successfully.")
            return new_user
        except AlreadyExistsError as e:
            logger.warning(f"Failed to create user: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            await self.db.rollback()
            raise ServerError(f"Failed to create user: {e}")
        
        #do further authentication 
        
        
        
    
    async def check_if_user_exist_by_email(self, email:str):
        try:
            logger.debug(f"Checking if user exists with email: {email}")
            stmt = await self.db.execute(
                select(User).where(
                    email==User.email
                )
            )
            user = stmt.scalar_one_or_none()
            if user:
                logger.debug(f"User with email {email} found.")
            else:
                logger.debug(f"User with email {email} not found.")
            return user
        except Exception as e:
            logger.error(f"Error checking if user exists by email {email}: {e}")
            raise ServerError()
    
    async def check_if_user_exist_by_school_id(self, school_id:str):
        try:
            logger.debug(f"Checking if user exists with school ID: {school_id}")
            stmt = await self.db.execute(
                select(User).where(
                    school_id == User.school_id
                )
            ) 
            user = stmt.scalar_one_or_none()
            if user:
                logger.debug(f"User with school ID {school_id} found.")
            else:
                logger.debug(f"User with school ID {school_id} not found.")
            return user
        except Exception as e:
            logger.error(f"Error checking if user exists by school ID {school_id}: {e}")
            raise ServerError()
    
    async def update_user():
        pass 
    
    async def delete_user():
        pass
