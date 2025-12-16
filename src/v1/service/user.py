import uuid

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.util.log import setup_logger
from src.v1.auth.schema import Login
from src.v1.auth.service import password_hash, verify_password
from src.v1.base.exception import (
    AlreadyExistsError,
    AuthorizationError,
    InvalidEmailPassword,
    NotFoundError,
    ServerError,
)
from src.v1.model import Department, Level, Role_Enum, User
from src.v1.schema.user import CreateStudent, CreateUser, UserCourse
from src.v1.service.courses import CourseService

logger = setup_logger(__name__, "user_service.log")


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.course = CourseService(self.db)

    async def create_user(self, user_data: CreateUser | CreateStudent):
        try:
            # user_data = CreateUser(user_data)
            logger.info(
                f"Attempting to create user with email: {user_data.email} and school_id: {user_data.school_id}"
            )
            user = await self.check_if_user_exist_by_email(
                user_data.email
            ) or await self.check_if_user_exist_by_school_id(user_data.school_id)

            if user:
                logger.warning(f"User with ID {user.id} already exists.")
                raise AlreadyExistsError(f"User with ID {user.id} already exist")

            password = password_hash(user_data.password)
            user_data.password = password

            # seed department, fetch the department, link users to dept both lecturer and student(link level too)
            #
            stmt = await self.db.execute(
                select(Department).where(Department.name.ilike(user_data.department))
            )
            dept = stmt.scalar_one_or_none()
            if not dept:
                raise NotFoundError(f"{user_data.department} not found")

            # link student to level
            level = None
            if user_data.role == Role_Enum.STUDENT and user_data.level is not None:
                # seed the level in the db, query the level table based on student level, link to users
                stmt = await self.db.execute(
                    select(Level).where(Level.name == user_data.level)
                )
                level = stmt.scalar_one_or_none()
                if not level:
                    raise NotFoundError(f"{user_data.level} not found")

            new_user = User(
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                password=user_data.password,
                school_id=user_data.school_id,
                role=user_data.role,
                level=level,
                department=dept,
            )

            self.db.add(new_user)
            await self.db.refresh(new_user)
            await self.db.commit()
            logger.info(f"User {new_user.id} created successfully.")
            return new_user
        except AlreadyExistsError as e:
            logger.error(f"Failed to create user: {e}")
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            await self.db.rollback()
            raise ServerError()

    async def authenticate_user(self, user_data: Login):
        try:
            logger.info(
                f"Attempting to authenticate user with email={user_data.email} or school_id={user_data.school_id}"
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
                logger.warning(
                    f"Authentication failed: User with identifier '{identifier}' does not exist."
                )
                raise NotFoundError(
                    f"User with identifier '{identifier}' does not exist."
                )

            # verify password
            if not verify_password(user_data.password, user.password):
                logger.warning(
                    f"Authentication failed: Invalid password for user {user.id}."
                )
                raise InvalidEmailPassword()

            # do further authentication

            # prepare jwt payload
            jwt_payload = {"user_id": str(user.id), "role": user.role.value}
            logger.info(f"Authentication successful for user {user.id}.")
            return jwt_payload
        except SQLAlchemyError as e:
            logger.error(f"Database error during authentication: {e}")
            raise ServerError()
        # except Exception as e:
        #     logger.error(f"An unexpected error occurred during authentication: {e}")
        #     raise ServerError()

    async def fetch_all_lecturers(self):
        try:
            stmt = await self.db.execute(
                select(User)
                .options(selectinload(User.department))
                .where(User.role == Role_Enum.LECTURER)
            )
            lecturers = stmt.scalars().all()
            logger.info(f"Successfully fetched {len(lecturers)} lecturers.")
            return lecturers
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching all lecturers: {e}")
            raise ServerError()
        # except Exception as e:
        #     logger.error(f"An unexpected error occurred while fetching all lecturers: {e}")
        #     raise ServerError()

    async def fetch_all_students(self):
        try:
            stmt = await self.db.execute(
                select(User)
                .options(selectinload(User.department), selectinload(User.level))
                .where(User.role == Role_Enum.STUDENT)
            )
            students = stmt.scalars().all()
            logger.info(f"Successfully fetched {len(students)} students.")
            return students
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching all students: {e}")
            raise ServerError()
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while fetching all students: {e}"
            )
            raise ServerError()

    async def check_if_user_exist_by_email(self, email: str):
        try:
            logger.debug(f"Checking if user exists with email: {email}")
            stmt = await self.db.execute(
                select(User)
                .options(selectinload(User.department))
                .where(User.email.ilike(email))
            )
            user = stmt.scalar_one_or_none()
            if user:
                logger.debug(f"User with email {email} found.")
            else:
                logger.debug(f"User with email {email} not found.")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error checking if user exists by email {email}: {e}")
            raise ServerError()

    async def check_if_user_exist_by_id(self, id: uuid.UUID):
        try:
            logger.debug(f"Checking if user exists with id: {id}")
            stmt = await self.db.execute(
                select(User)
                .options(
                    selectinload(User.courses),
                    selectinload(User.department),
                    selectinload(User.level),
                    # selectinload(User.level),
                )
                .where(User.id == id)
            )
            user = stmt.scalar_one_or_none()
            if user:
                logger.debug(f"User with id {id} found.")
            else:
                logger.debug(f"User with id {id} not found.")
            return user
        except SQLAlchemyError as e:
            logger.error(
                f"Error checking if user exists by id {id}: {e}", exc_info=True
            )
            raise ServerError()

    async def check_if_user_exist_by_school_id(self, school_id: str):
        try:
            logger.debug(f"Checking if user exists with school ID: {school_id}")
            stmt = await self.db.execute(
                select(User).where(User.school_id.ilike(school_id))
            )
            user = stmt.scalar_one_or_none()
            if user:
                logger.debug(f"User with school ID {school_id} found.")
            else:
                logger.debug(f"User with school ID {school_id} not found.")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error checking if user exists by school ID {school_id}: {e}")
            raise ServerError()

    async def link_lecturer_to_course(self, user_data: UserCourse):
        try:
            logger.info(
                f"Attempting to link lecturer {user_data.user_id} to course {user_data.course_id}."
            )
            # lecturers and course must have the same department

            # check if role is lect
            user = await self.check_if_user_exist_by_id(user_data.user_id)
            if not user:
                logger.warning(f"User {user_data.user_id} not found.")
                raise NotFoundError()
            if user.role != Role_Enum.LECTURER:
                logger.warning(f"User {user.id} is not a lecturer.")
                raise AuthorizationError(
                    f"{user.id} does not have permission to link to course"
                )

            # check if both the course and user are in the same dept
            course = await self.course.check_course_dept(user_data.course_id)
            if not course:
                logger.warning(f"Course {user_data.course_id} not found.")
                raise NotFoundError()
            if course.department.id != user.department.id:
                logger.warning(
                    f"Course {course.code} and user {user.id} are not in the same department."
                )
                raise AuthorizationError(f"{user.id} cannot register this course")

            # add more checks if needed
            user.courses.append(course)
            self.db.add(user)
            await self.db.commit()
            logger.info(
                f"Successfully linked lecturer {user.first_name} to course {course.name}."
            )
            return True
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while linking lecturer {user_data.user_id} to course {user_data.course_id}: {e}",
                exc_info=True,
            )
            await self.db.rollback()
            raise ServerError()
        # except Exception as e:
        #     logger.error(f"An unexpected error occurred while linking lecturer {lect_id} to course {course_id.course_id}: {e}")
        #     await self.db.rollback()
        #     raise ServerError()

    # @staticmethod
    # async def d
    async def update_user():
        pass

    async def delete_user():
        pass
