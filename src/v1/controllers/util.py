#shared servicde Dependency

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.util.db import get_session
from src.v1.auth.service import AccessTokenBearer
from src.v1.service.courses import CourseService, DeptService, LevelService
from src.v1.service.user import UserService

def get_course_service(db: AsyncSession = Depends(get_session)):
    return CourseService(db=db)

def get_level_service(db: AsyncSession = Depends(get_session)):
    return LevelService(db=db)

def get_dept_service(db: AsyncSession = Depends(get_session)):
    return DeptService(db=db)

def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)

def get_access_token():
    access_token_bearer = AccessTokenBearer()
    return access_token_bearer