from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, ValidationError

class Login(BaseModel):
    email: Optional[EmailStr] = None
    school_id: Optional[str] = None
    password: str
    
    model_config = ConfigDict(from_attributes=True)
    @field_validator('email', 'school_id', mode='before')
    @classmethod
    def check_at_least_one_provided(cls, v, info):
        if info.data.get('email') is None and info.data.get('school_id') is None:
            raise ValidationError("Either email or school_id must be provided")
        return v
