from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    PRE_EVENT = "pre_event"
    HACKATHON_DAY = "hackathon_day"


class EventCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    event_type: EventType
    event_date: datetime
    capacity: int = Field(..., gt=0)
    registration_open: bool = True


class EventResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    event_type: str
    event_date: datetime
    capacity: int
    registration_open: bool
    registered_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True