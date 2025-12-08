from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator, ValidationError, EmailStr
import uuid
from datetime import datetime
from src.v1.model.user import Role_Enum, Level_Enum

class DepartmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    class Config:
        from_attributes = True 
        
class UserBaseSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    school_id: str
    role: Optional[Role_Enum] = None
    department:str
    level: Optional[Level_Enum] = None # Make level optional

    @model_validator(mode='after')
    def validate_student_level(self) -> 'UserBaseSchema':
        if self.role == Role_Enum.STUDENT and self.level is None:
            raise ValidationError("Level must be provided for students.")
        return self


class CreateUser(UserBaseSchema):
    password: str


class UserResponse(UserBaseSchema):
    department:DepartmentResponse
    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
