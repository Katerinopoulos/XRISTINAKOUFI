from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    role = Column(String(20), default="GUEST")
    is_approved = Column(Boolean, default=False)
    
    organized_events = relationship("Event", back_populates="organizer")
    bookings = relationship("Booking", back_populates="user")

class Event(Base):
    __tablename__ = "events"
    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    event_type = Column(String(100))
    venue = Column(String(255))
    address = Column(String(255))
    city = Column(String(100))
    country = Column(String(100))
    capacity = Column(Integer, nullable=False)
    description = Column(String(1000))
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    status = Column(String(50), default="PUBLISHED")
    organizer_id = Column(Integer, ForeignKey("users.id"))
    
    organizer = relationship("User", back_populates="organized_events")
    ticket_types = relationship("TicketType", back_populates="event")

class TicketType(Base):
    __tablename__ = "ticket_types"
    id = Column(String(50), primary_key=True, index=True)
    event_id = Column(String(50), ForeignKey("events.id"))
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    available = Column(Integer, nullable=False)

    event = relationship("Event", back_populates="ticket_types")
    bookings = relationship("Booking", back_populates="ticket_type")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ticket_type_id = Column(String(50), ForeignKey("ticket_types.id"))
    quantity = Column(Integer, nullable=False)
    booking_date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    ticket_type = relationship("TicketType", back_populates="bookings")