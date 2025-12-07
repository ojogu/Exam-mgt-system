from fastapi import APIRouter, Depends
from src.v1.schema.user import CreateUser, UserResponse
from src.v1.service.user import UserService
from src.util.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.v1.model.user import Role_Enum
def get_user_service(db: AsyncSession = Depends(get_session)):
    return UserService(db=db)

auth_route = APIRouter(prefix="/auth")

@auth_route.post("/lecturer-register")
async def lecturer_register(user_data: CreateUser,
user_service:UserService = Depends(get_user_service)                      
):
    user_data.role = Role_Enum.LECTURER
    new_user = await user_service.create_user(user_data)
    validated_data = UserResponse.model_validate(new_user).model_dump()
    return validated_data

@auth_route.post("/student-register")
async def student_register(user_data: CreateUser,
user_service:UserService = Depends(get_user_service)                    
):
    user_data.role = Role_Enum.STUDENT
    new_user = await user_service.create_user(user_data) 
    validated_data = UserResponse.model_validate(new_user).model_dump()
    return validated_data

@auth_route.post("/lecturer-login")
def lecturer_login(user_data: CreateUser,
user_service:UserService = Depends(get_user_service)                   
):
    pass 

@auth_route.post("/student-register")
def student_login(user_data: CreateUser,
    user_service:UserService = Depends(get_user_service)
    ):
    pass 