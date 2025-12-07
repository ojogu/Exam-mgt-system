from typing import Optional
from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
from src.v1.model.user import Role_Enum


class UserBaseSchema(BaseModel):
    email: Optional[str] = None
    first_name: str
    last_name: str
    school_id: str
    role: Role_Enum


class CreateUser(UserBaseSchema):
    password: str


class UserResponse(UserBaseSchema):
    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
