from typing import Optional
import uuid
from src.v1.base.model import BaseModel
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String,  Enum as SqlEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from enum import StrEnum
# from .courses import Department


class Role_Enum(StrEnum):
    STUDENT = "student"
    LECTURER = "lecturer"
    
class Level_Enum(StrEnum):
    LEVEL_100 = "100"
    LEVEL_200 = "200"
    LEVEL_300 = "300"
    LEVEL_400 = "400"
    LEVEL_500 = "500"


class User(BaseModel):
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True, index=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False) 
    password: Mapped[str] = mapped_column(String, nullable=False) 
    school_id: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True) 
    # is_verified: Mapped[bool] = mapped_column(Boolean, default=False) #email verification, set to true
    role: Mapped[Role_Enum] = mapped_column(
        SqlEnum(Role_Enum, name="role_enum"),  nullable=False)
    
    level_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("levels.id"), nullable=True)
    level: Mapped[Optional["Level"]] = relationship("Level", uselist=False, backref=backref("user"))
    
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    department: Mapped[Optional["Department"]] = relationship("Department", uselist=False, backref=backref("user")) # type: ignore  # noqa: F821
    

class Level(BaseModel):
    level: Mapped[Level_Enum] = mapped_column(
        SqlEnum(Level_Enum, name="level_enum"),  nullable=False) 

    