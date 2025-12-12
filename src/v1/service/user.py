from sqlalchemy.ext.asyncio import AsyncSession
from src.v1.model import  Level_Enum, Role_Enum
from src.v1.model import User, Level, Department, Course
from sqlalchemy import select, cast, String
from sqlalchemy.orm import selectinload
from src.v1.schema.user import CreateUser, CreateStudent
from src.v1.base.exception import (
    NotFoundError, 
    AlreadyExistsError,
    ServerError,
    InvalidEmailPassword
)
from src.v1.auth.service import verify_password, password_hash
from src.util.log import setup_logger
from src.v1.auth.schema import Login
logger = setup_logger(__name__, "user_service.log")

class UserService():
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_user(self, user_data:CreateUser|CreateStudent): 
        try:
            # user_data = CreateUser(user_data)
            logger.info(f"Attempting to create user with email: {user_data.email} and school_id: {user_data.school_id}")
            user = await self.check_if_user_exist_by_email(user_data.email) or await self.check_if_user_exist_by_school_id(user_data.school_id)
            
            if user:
                logger.warning(f"User with ID {user.id} already exists.")
                raise AlreadyExistsError(f"User with ID {user.id} already exist")
            
            password = password_hash(user_data.password)
            user_data.password = password
            
            #seed department, fetch the department, link users to dept both lecturer and student(link level too)
            #
            stmt = await self.db.execute(
                select(Department).where(
                    Department.name.ilike(user_data.department)
                )
            )
            dept = stmt.scalar_one_or_none()
            if not dept: 
                raise NotFoundError(f"{user_data.department} not found")
            
            #link student to level
            level = None
            if user_data.role == Role_Enum.STUDENT and user_data.level is not None:
                #seed the level in the db, query the level table based on student level, link to users
                stmt = await self.db.execute (select(Level).where(
                    Level.name == user_data.level
                ))
                level = stmt.scalar_one_or_none()
                if not level: 
                    raise NotFoundError(f"{user_data.level} not found")
                
                
         
            new_user = User(
                email=user_data.email,
                first_name = user_data.first_name,
                last_name = user_data.last_name,
                password = user_data.password,
                school_id = user_data.school_id,
                role = user_data.role,
                level=level,
                department=dept
            )
            
            self.db.add(new_user)
            await self.db.commit()
            logger.info(f"User {new_user.id} created successfully.")
            return new_user
        except AlreadyExistsError as e:
            logger.error(f"Failed to create user: {e}")
            raise e
        # except Exception as e:
        #     logger.error(f"Error creating user: {e}")
            await self.db.rollback()
            raise ServerError()
        
         
        
    async def authenticate_user(self, user_data:Login):
        logger.info(
            f"checking user with email={user_data.email} or school_id={user_data.school_id}"
        )

        user = None

        # Try email first if provided
        if user_data.email:
            user = await self.check_if_user_exist_by_email(user_data.email)
            # logger.debug(f"user found: {user.email}")

        # If not found yet, try school_id
        if not user and user_data.school_id:
            logger.debug("user not found with email, using school id")
            user = await self.check_if_user_exist_by_school_id(user_data.school_id)
            # logger.debug(f"user found with school id: {user.school_id}")

        # Handle not found
        if not user:
            identifier = user_data.email or user_data.school_id
            logger.error(f"User with identifier '{identifier}' does not exist.")
            raise NotFoundError(f"User with identifier '{identifier}' does not exist.")

        
        #verify password
        if not verify_password(user_data.password, user.password):
            raise InvalidEmailPassword()
        
        #do further authentication
        
        #prepare jwt payload
        jwt_payload = {
            "user_id": str(user.id),
            "role": user.role.value
        }
        return jwt_payload
        
    async def fetch_all_lecturers(self):
        stmt = await self.db.execute(
                select(User).options(selectinload(User.department)).where(
                    User.role == Role_Enum.LECTURER
                )
        ) 
        lec = stmt.scalars().all()
        return lec
    
    async def fetch_all_students(self):
        stmt = await self.db.execute(
                select(User).options(selectinload(User.department)).where(
                    User.role == Role_Enum.STUDENT
                )
        ) 
        stud = stmt.scalars().all()
        return stud
    
    async def check_if_user_exist_by_email(self, email:str):
        try:
            logger.debug(f"Checking if user exists with email: {email}")
            stmt = await self.db.execute(
                select(User).options(selectinload(User.department)).where(
                    User.email.ilike(email)
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
                    User.school_id.ilike(school_id)
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
