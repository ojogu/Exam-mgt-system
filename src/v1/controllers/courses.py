from fastapi import APIRouter, Depends, status, Query
from src.v1.schema.courses import LevelResponse, DeptResponse, CreateCourse, CourseResponse
from src.v1.service.courses import CourseService, DeptService, LevelService
from src.util.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.util.response import success_response
from src.util.log import setup_logger
import uuid
logger = setup_logger(__name__, "courses_route.log")

def get_course_service(db: AsyncSession = Depends(get_session)):
    return CourseService(db=db)

def get_level_service(db: AsyncSession = Depends(get_session)):
    return LevelService(db=db)

def get_dept_service(db: AsyncSession = Depends(get_session)):
    return DeptService(db=db)

courses_router = APIRouter()
@courses_router.get("/levels")
async def fetch_levels(level_service: LevelService = Depends(get_level_service)):
    levels = await level_service.fetch_all_level()
    # logger.info(levels)
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


@courses_router.get("/departments")
async def fetch_all_department(dept_service: DeptService = Depends(get_dept_service)):
    departments = await dept_service.fetch_all_dept()
    dept = []
    
    for department in departments:
        dept_value = DeptResponse.model_validate(department).model_dump()
        dept.append(dept_value)
        
    return success_response(
        status_code=status.HTTP_200_OK,
        data=dept
    )
    
@courses_router.get("/departments/courses")
async def fetch_all_course_in_a_department(dept_id: uuid.UUID = Query(...), 
dept_service: DeptService = Depends(get_dept_service)):
    dept = []
    departments = await dept_service.fetch_all_courses_for_a_dept(dept_id)
    if not departments:
        dept = []
    
    for department in departments:
        # return department.to_dict()
        dept_value = CourseResponse.model_validate(department).model_dump(exclude={
        'level': {'created_at', 'updated_at'},
        "department": {'created_at', 'updated_at'}
    }
        )
        dept.append(dept_value)
        
    return success_response(
        status_code=status.HTTP_200_OK,
        data=dept
    )
    
    
@courses_router.post("/course")
async def create_course(course_data:CreateCourse,
course_service:CourseService = Depends(get_course_service)
):
    new_course = await course_service.create_course(course_data)  
    # return new_course.to_dict()  
    course = CourseResponse.model_validate(new_course).model_dump(exclude={
        'level': {'created_at', 'updated_at'},
        "department": {'created_at', 'updated_at'}
    })
    return success_response(
        status_code = status.HTTP_201_CREATED,
        data = course
    )
