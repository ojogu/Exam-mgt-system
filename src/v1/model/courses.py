import uuid
from src.v1.base.model import BaseModel
# from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String,  Enum as SqlEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

# from .user import user_course_association


class Department(BaseModel):
    name:Mapped[str] = mapped_column(String, nullable=False) 
     


class Course(BaseModel):
    name:Mapped[str] = mapped_column(String, nullable=False)
    code:Mapped[str] = mapped_column(String, nullable=False, unique=True)
    department_id:Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), nullable=False)
    department:Mapped["Department"] = relationship("Department", backref="courses")
    level_id:Mapped[uuid.UUID] = mapped_column(ForeignKey("levels.id"), nullable=False)
    level:Mapped["Level"] = relationship("Level", backref=backref("courses")) # type: ignore  # noqa: F821
    # users: Mapped[List["User"]] = relationship("User", secondary=user_course_association, back_populates="courses")
