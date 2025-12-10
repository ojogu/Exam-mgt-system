from sqlalchemy.ext.asyncio import AsyncSession
from src.v1.model import  Level_Enum, Role_Enum
from src.v1.model import User, Level, Department, Course
from sqlalchemy import select
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


class CoursesService():
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def fetch_all_level(self):
        try:
            stmt = await self.db.execute(
                select(Level)
            )
            all_levels = stmt.scalars().all() #a list of Level objects: [Level(), Level(), ...]
            #Use .all() (without .scalars()) to get a list of tuple rows, where each tuple contains the columns selected. Since you are selecting the entire Level entity, each tuple will contain a single Level object.
            logger.info("Successfully fetched all levels.")
            return all_levels
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching all levels: {e}")
            raise ServerError()
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching all levels: {e}")
            raise ServerError()
        

    #return dept
    #return courses for a dept
    #return level 
    

# class LevelService():
#     def __init__(self):
#         pass
    
#     def fetch_all_level():
#         pass
