from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- USERS ---
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = "GUEST"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_approved: bool
    class Config:
        from_attributes = True

# --- TICKETS ---
class TicketTypeCreate(BaseModel):
    id: str
    name: str
    price: float
    quantity: int

class TicketTypeResponse(TicketTypeCreate):
    event_id: str
    available: int
    class Config:
        from_attributes = True

# --- EVENTS ---
class EventCreate(BaseModel):
    id: str
    title: str
    event_type: str
    venue: str
    address: str
    city: str
    country: str
    capacity: int
    description: str
    start_datetime: datetime
    end_datetime: datetime

class EventResponse(EventCreate):
    status: str
    organizer_id: int
    ticket_types: List[TicketTypeResponse] = []
    class Config:
        from_attributes = True

# --- BOOKINGS ---
class BookingCreate(BaseModel):
    ticket_type_id: str
    quantity: int

class BookingResponse(BaseModel):
    id: int
    user_id: int
    ticket_type_id: str
    quantity: int
    booking_date: datetime
    class Config:
        from_attributes = True