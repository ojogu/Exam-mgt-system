from sqlalchemy.ext.asyncio import AsyncSession
from src.v1.model import  Level_Enum, Role_Enum
from src.v1.model import User, Level, Department, Course
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from src.v1.schema.courses import CreateCourse
from src.v1.base.exception import (
    NotFoundError, 
    AlreadyExistsError,
    ServerError
)
from src.util.log import setup_logger
import uuid
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

    async def check_if_course_exist_for_a_level_by_course_code(self, level_id: uuid.UUID, course_code: str):
        try:
            stmt = await self.db.execute(
                select(Course).options(selectinload(Course.level)).where(
                    Course.level_id == level_id
                ).where(
                    Course.code.ilike(course_code)
                )
            )
            course = stmt.scalar_one_or_none()
            if course:
                logger.info(f"Course {course.name}, {course.code} found for Level {course.level.name}.")
            else:
                logger.info(f"Course {course_code} not found for level {level_id}.")
            return course
        except SQLAlchemyError as e:
            logger.error(f"Database error while checking course existence for level {level_id} by code {course_code}: {e}")
            raise ServerError()
        # except Exception as e:
        #     logger.error(f"An unexpected error occurred while checking course existence for level {level_id} by code {course_code}: {e}")
        #     raise ServerError()

    async def check_if_course_exist_for_a_level_by_course_name(self, level_id: uuid.UUID, course_name: str):
        try:
            stmt = await self.db.execute(
                select(Course).options(selectinload(Course.level)).where(
                    Course.level_id == level_id
                ).where(
                    Course.name.ilike(course_name)
                )
            )
            course = stmt.scalar_one_or_none()
            if course:
                logger.info(f"Course {course.name}, {course.code} found for Level {course.level.name}.")
            else:
                logger.info(f"Course {course_name} not found for level {level_id}.")
            return course
        except SQLAlchemyError as e:
            logger.error(f"Database error while checking course existence for level {level_id} by name {course_name}: {e}")
            raise ServerError()
        except Exception as e:
            logger.error(f"An unexpected error occurred while checking course existence for level {level_id} by name {course_name}: {e}")
            raise ServerError()


class DeptService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_all_courses_for_a_dept(self, dept_id:uuid.UUID):
        stmt = await self.db.execute(
            select(Course).options(selectinload(Course.department)).where(
                Department.id == dept_id
            )
        )
        course = stmt.scalars().all()
        return course

    async def fetch_all_dept(self):
        stmt = await self.db.execute(
            select(Department)
        )
        department = stmt.scalars().all()
        return department
    
    async def create_dept(self):
        pass 
    
    async def check_if_dept_exist(self, dept_name:str):
        stmt = await self.db.execute(
            select(Department).where(
                Department.name.ilike(dept_name)
            )
        )
        department = stmt.scalar_one_or_none()
        return department
        
    async def check_if_course_exist_for_a_dept_by_course_code(self, dept_id: uuid.UUID, course_code: str):
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
        # except Exception as e:
        #     logger.error(f"An unexpected error occurred while checking course existence for dept {dept_id} by code {course_code}: {e}")
        #     raise ServerError()

    async def check_if_course_exist_for_a_dept_by_course_name(self, dept_id: uuid.UUID, course_name: str):
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
        # except Exception as e:
        #     logger.error(f"An unexpected error occurred while checking course existence for dept {dept_id} by name {course_name}: {e}")
        #     raise ServerError()


class CourseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.level = LevelService(self.db)
        self.dept = DeptService(self.db)

    async def create_course(self, course_data: CreateCourse):
        try:
            logger.info(f"Attempting to create course with name '{course_data.name}' and code '{course_data.code}' for department {course_data.department_id} and level {course_data.level_id}.")
            # ideally, only admin can create course (later update)
            # check if the course exist and dept and level
            course_exist_by_code_dept = await self.dept.check_if_course_exist_for_a_dept_by_course_code(course_data.department_id, course_data.code)
            course_exist_by_code_level = await self.level.check_if_course_exist_for_a_level_by_course_code(course_data.level_id, course_data.code)
            course_exist_by_name_dept = await self.dept.check_if_course_exist_for_a_dept_by_course_name(course_data.department_id, course_data.name)
            course_exist_by_name_level = await self.level.check_if_course_exist_for_a_level_by_course_name(course_data.level_id, course_data.name)

            course_exist = (course_exist_by_code_dept and course_exist_by_code_level) or (course_exist_by_name_dept and course_exist_by_name_level)

            if course_exist:
                logger.warning(f"Course creation failed: Course with name '{course_data.name}' or code '{course_data.code}' already exists for department {course_data.department_id} and level {course_data.level_id}.")
                raise AlreadyExistsError()

            new_course = Course(
                name=course_data.name,
                code=course_data.code,
                department_id=course_data.department_id,
                level_id=course_data.level_id
            )
            self.db.add(new_course)
            await self.db.commit()
            logger.info(f"Successfully created course '{new_course.name}' with code '{new_course.code}' for department {course_data.department_id} and level {course_data.level_id}.")
            return new_course
        except SQLAlchemyError as e:
            logger.error(f"Database error while creating course with name '{course_data.name}' and code '{course_data.code}': {e}")
            raise ServerError()
        # except Exception as e:
        #     logger.error(f"An unexpected error occurred while creating course with name '{course_data.name}' and code '{course_data.code}': {e}")
        #     raise ServerError()
            
        

    # return dept
    # return courses for a dept
    # return level
