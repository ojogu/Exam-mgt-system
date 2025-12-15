from datetime import datetime
from fastapi import APIRouter, Depends, status
from src.v1.schema.user import CreateUser, UserResponse, CreateStudent
from src.v1.service.user import UserService
from src.util.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.v1.model.user import Role_Enum
from src.util.response import success_response
from src.v1.controllers.util import get_user_service
from .schema import Login
from .service import auth_service, RefreshTokenBearer, AccessTokenBearer
from src.util.config import config

# def get_user_service(db: AsyncSession = Depends(get_session)):
#     return UserService(db=db)

auth_router = APIRouter(prefix="/auth")

@auth_router.post("/lecturer-register")
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



@auth_router.post("/student-register")
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


@auth_router.post("/login")
async def login(user_data: Login,
user_service:UserService = Depends(get_user_service)                   
):
    # tokens = []
    user = await user_service.authenticate_user(user_data)
    access_token = auth_service.create_access_token(user)
    
    refresh_token = auth_service.create_access_token(
        user_data = user,
        expiry = config.refresh_token_expiry,
        refresh = True
        
    )
    data = ( 
        {"access_token": access_token,
         "refresh_token": refresh_token,
         "token_type": "Bearer",
         "expires_in": config.access_token_expiry,
         "user_data": {
             "user_id": user["user_id"],
             "role": user["role"]
         }
        }
    )
    
    return success_response(
        message="Tokens Successfully Generated",
        status_code=status.HTTP_200_OK,
        data=data
    )
     

@auth_router.get("/refresh-token")
async def get_new_access_token(token_details:dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"] 
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = auth_service.create_access_token(
            user_data=token_details["user"]
        )
        return success_response(
        message="Refresh Token Successfully Generated",
        status_code=status.HTTP_200_OK,
        data=new_access_token
    )
        

