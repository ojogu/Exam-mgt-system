from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict
from src.v1.model.user import Role_Enum, Level_Enum

class LevelResponse(BaseModel):
    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    name: Level_Enum
    
    model_config = ConfigDict(from_attributes=True)
    
    