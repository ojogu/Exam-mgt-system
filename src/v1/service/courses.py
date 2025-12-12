from sqlalchemy.ext.asyncio import AsyncSession
from src.v1.model import  Level_Enum, Role_Enum
from src.v1.model import User, Level, Department, Course
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from src.v1.schema.user import CreateUser
from src.v1.base.exception import (
    NotFoundError, 
    AlreadyExistsError,
    ServerError
)
from src.util.log import setup_logger
logger = setup_logger(__name__, "courses_service.log")

#link courses to dept and level, have an endpoint where student/lecturers register courses based on level. 
#seed courses for 100l, lecturers register courses to teach, student register courses only based on their level and department 


class LevelService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_all_level(self):
        try:
            stmt = await self.db.execute(
                select(Level)
            )
            all_levels = stmt.scalars().all()  # a list of Level objects: [Level(), Level(), ...]
            # Use .all() (without .scalars()) to get a list of tuple rows, where each tuple contains the columns selected. Since you are selecting the entire Level entity, each tuple will contain a single Level object.
            logger.info("Successfully fetched all levels.")
            return all_levels
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching all levels: {e}")
            raise ServerError()
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching all levels: {e}")
            raise ServerError()

    async def fetch_all_courses_for_a_level(self):
        stmt = await self.db.execute(
            select(Course).options(selectinload(Course.level))
        )
        course = stmt.scalars().all()
        return course

    async def check_if_course_exist_for_a_level(self, level_id: int, course_identifier: str):
        try:
            stmt = await self.db.execute(
                select(Course).options(selectinload(Course.level)).where(
                    Course.level_id == level_id
                ).where(
                    or_(Course.code.ilike(course_identifier), Course.name.ilike(course_identifier))
                )
            )
            course = stmt.scalar_one_or_none()
            if course:
                logger.info(f"Course {course.name}, {course.code} found for Level {course.level.name}.")
            else:
                logger.info(f"Course {course_identifier} not found for level {level_id}.")
            return course
        except SQLAlchemyError as e:
            logger.error(f"Database error while checking course existence for level {level_id} by identifier {course_identifier}: {e}")
            raise ServerError()
        except Exception as e:
            logger.error(f"An unexpected error occurred while checking course existence for level {level_id} by identifier {course_identifier}: {e}")
            raise ServerError()


class DeptService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_all_courses_for_a_dept(self):
        stmt = await self.db.execute(
            select(Course).options(selectinload(Course.department))
        )
        course = stmt.scalars().all()
        return course

    async def check_if_course_exist_for_a_dept_by_course_code(self, dept_id: int, course_code: str):
        try:
            stmt = await self.db.execute(
                select(Course).options(selectinload(Course.department)).where(
                    Course.department_id == dept_id
                ).where(
                    Course.code.ilike(course_code)
                )
            )
            course = stmt.scalar_one_or_none()
            if course:
                logger.info(f"Course {course.name}, {course.code} found for Dept {course.department.name}.")
            else:
                logger.info(f"Course {course_code} not found for dept {dept_id}.")
            return course
        except SQLAlchemyError as e:
            logger.error(f"Database error while checking course existence for dept {dept_id} by code {course_code}: {e}")
            raise ServerError()
        except Exception as e:
            logger.error(f"An unexpected error occurred while checking course existence for dept {dept_id} by code {course_code}: {e}")
            raise ServerError()

    async def check_if_course_exist_for_a_dept_by_course_name(self, dept_id: int, course_name: str):
        try:
            stmt = await self.db.execute(
                select(Course).options(selectinload(Course.department)).where(
                    Course.department_id == dept_id
                ).where(
                    Course.name.ilike(course_name)
                )
            )
            course = stmt.scalar_one_or_none()
            if course:
                logger.info(f"Course {course.name}, {course.code} found for Dept {course.department.name}.")
            else:
                logger.info(f"Course {course_name} not found for dept {dept_id}.")
            return course
        except SQLAlchemyError as e:
            logger.error(f"Database error while checking course existence for dept {dept_id} by name {course_name}: {e}")
            raise ServerError()
        except Exception as e:
            logger.error(f"An unexpected error occurred while checking course existence for dept {dept_id} by name {course_name}: {e}")
            raise ServerError()


class CourseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_course(self, course_data):
        # ideally, only admin can create course (later update)
        # check if the course exist and dept and level
        pass
    # return dept
    # return courses for a dept
    # return level
