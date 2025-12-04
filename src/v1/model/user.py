from typing import Optional
from src.v1.base.model import BaseModel
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String,  Enum as SqlEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from enum import StrEnum


class Role(StrEnum):
    STUDENT = "student"
    LECTURER = "lecturer"
    
class Level(StrEnum):
    STUDENT = "student"
    LECTURER = "lecturer"


class User(BaseModel):
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True) 
    password: Mapped[Optional[str]] = mapped_column(String, nullable=True) 
    role: Mapped[Role] = mapped_column(
        SqlEnum(Role, name="role_enum"),  nullable=False)

class Level(BaseModel):
    pass 