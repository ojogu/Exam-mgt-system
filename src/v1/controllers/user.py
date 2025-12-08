from fastapi import APIRouter, Depends
from src.v1.schema.user import CreateUser, UserResponse
from src.v1.service.user import UserService
from src.util.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.v1.model.user import Role_Enum
from pydantic import EmailStr
def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)

user_route = APIRouter()

@user_route.get("/lecturer/{email}")
async def fetch_lecturer(
    email:EmailStr,
    user_service:UserService = Depends(get_user_service)                      
):
    user = await user_service.check_if_user_exist_by_email(email)
    validated_data = UserResponse.model_validate(user).model_dump()
    return validated_data