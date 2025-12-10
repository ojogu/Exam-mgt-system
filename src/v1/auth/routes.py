from fastapi import APIRouter, Depends, status
from src.v1.schema.user import CreateUser, UserResponse, CreateStudent
from src.v1.service.user import UserService
from src.util.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.v1.model.user import Role_Enum
from src.util.response import success_response

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
    return success_response(
        message="Lecturer Created Successfully",
        status_code=status.HTTP_201_CREATED,
        data=validated_data
    )



@auth_route.post("/student-register")
async def student_register(user_data: CreateStudent,
user_service:UserService = Depends(get_user_service)                    
):      
    # user_data.role = Role_Enum.STUDENT
    new_user = await user_service.create_user(user_data) 
    validated_data = UserResponse.model_validate(new_user).model_dump()
    return success_response(
        message="Student Created Successfully",
        status_code=status.HTTP_201_CREATED,
        data=validated_data
    )


@auth_route.post("/lecturer-login")
def lecturer_login(user_data: CreateUser,
user_service:UserService = Depends(get_user_service)                   
):
    pass 

