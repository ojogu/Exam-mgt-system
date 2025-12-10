from fastapi import APIRouter, Depends, status
from src.v1.schema.courses import LevelResponse
from src.v1.service.courses import CoursesService
from src.util.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.v1.model.user import Role_Enum
from pydantic import EmailStr
from src.util.response import success_response
from src.util.log import setup_logger
logger = setup_logger(__name__, "courses_route.log")

def get_course_service(db: AsyncSession = Depends(get_session)):
    return CoursesService(db=db)

courses_router = APIRouter()
@courses_router.get("/levels")
async def fetch_levels(course_service: CoursesService = Depends(get_course_service)):
    levels = await course_service.fetch_all_level()
    logger.info(levels)
    lev = []
    for level in levels:
        # logger.info(f"loop: {level}")
        level_value = LevelResponse.model_validate(level).model_dump()
        # logger.info(level_value)
        lev.append(level_value)
    return success_response(
        status_code=status.HTTP_200_OK,
        data=lev
    )

    
    
