from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List

import models
import schemas
from database import engine, get_db

# 1. Δημιουργία πινάκων στη βάση
models.Base.metadata.create_all(bind=engine)

# 2. Αρχικοποίηση εφαρμογής
app = FastAPI(title="Event Management API")

# 3. Ρύθμιση CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Ρυθμίσεις Ασφαλείας
SECRET_KEY = "my_super_secret_key_for_this_app"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# --- ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ (UTILS) ---

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Μη έγκυρα διαπιστευτήρια",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "Το API λειτουργεί!"}

# --- ΧΡΗΣΤΕΣ & AUTH ---

@app.post("/users/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Το username υπάρχει ήδη.")
    
    new_user = models.User(
        username=user.username,
        password_hash=get_password_hash(user.password),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_approved=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/users/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Λάθος username ή password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- ΕΚΔΗΛΩΣΕΙΣ ---

@app.post("/events/", response_model=schemas.EventResponse)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_event = models.Event(
        id=event.id,
        title=event.title,
        event_type=event.event_type,
        venue=event.venue,
        address=event.address,
        city=event.city,
        country=event.country,
        capacity=event.capacity,
        description=event.description,
        start_datetime=event.start_datetime,
        end_datetime=event.end_datetime,
        organizer_id=current_user.id,
        status="PUBLISHED"
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

@app.get("/events/", response_model=List[schemas.EventResponse])
def get_all_events(db: Session = Depends(get_db)):
    return db.query(models.Event).all()

# --- ΕΙΣΙΤΗΡΙΑ ---

@app.post("/events/{event_id}/tickets", response_model=schemas.TicketTypeResponse)
def add_ticket_type(event_id: str, ticket: schemas.TicketTypeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.organizer_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Η εκδήλωση δεν βρέθηκε.")

    new_ticket = models.TicketType(
        id=ticket.id,
        event_id=event_id,
        name=ticket.name,
        price=ticket.price,
        quantity=ticket.quantity,
        available=ticket.quantity
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

# --- ΚΡΑΤΗΣΕΙΣ ---

@app.post("/bookings/", response_model=schemas.BookingResponse)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ticket = db.query(models.TicketType).filter(models.TicketType.id == booking.ticket_type_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ο τύπος εισιτηρίου δεν βρέθηκε.")
    if ticket.available < booking.quantity:
        raise HTTPException(status_code=400, detail="Δεν υπάρχουν αρκετά διαθέσιμα εισιτήρια.")
    
    ticket.available -= booking.quantity
    new_booking = models.Booking(
        user_id=current_user.id,
        ticket_type_id=ticket.id,
        quantity=booking.quantity
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

# Endpoint για να βλέπει ο χρήστης τις κρατήσεις του
@app.get("/bookings/", response_model=List[schemas.BookingResponse])
def get_my_bookings(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Booking).filter(models.Booking.user_id == current_user.id).all()