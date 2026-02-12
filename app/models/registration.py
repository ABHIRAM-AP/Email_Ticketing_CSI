from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class RegistrationCreate(BaseModel):
    event_id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{9,14}$")
    college: str = Field(..., min_length=1, max_length=200)


class RegistrationResponse(BaseModel):
    id: int
    event_id: int
    name: str
    email: str
    phone: str
    college: str
    ticket_id: str
    qr_code_url: Optional[str]
    checked_in: bool = False
    checked_in_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    ticket_id: str
    event_name: str
    participant_name: str
    participant_email: str
    event_date: datetime
    qr_code_url: str