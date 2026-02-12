from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class HackathonParticipantCreate(BaseModel):
    name: str
    email: EmailStr
    college: Optional[str] = None
    phone: Optional[str] = None


class HackathonParticipantResponse(BaseModel):
    id: int
    name: str
    email: str
    college: Optional[str]
    phone: Optional[str]
    imported_at: datetime

    class Config:
        from_attributes = True


class CheckInCreate(BaseModel):
    event_id: int
    email: str
    ticket_id: Optional[str] = None
    source: str  # 'qr', 'csv', 'manual'


class CheckInResponse(BaseModel):
    id: int
    event_id: int
    email: str
    ticket_id: Optional[str]
    source: str
    checked_in_at: datetime

    class Config:
        from_attributes = True


class CSVUploadResponse(BaseModel):
    message: str
    total_rows: int
    imported: int
    duplicates: int
    errors: int