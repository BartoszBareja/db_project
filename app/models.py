from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Numeric, TIMESTAMP, ForeignKey, Boolean
import enum
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

Base = declarative_base()  # TYLKO RAZ

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    avaliable_languages = Column(String)
    description = Column(String)
    price = Column(Numeric(10, 2), nullable=False)
    version = Column(String(50), nullable=False)
    producer_id = Column(Integer, nullable=False)
    pegi_rating = Column(String(10))
    release_date = Column(DateTime, nullable=False)
    itch_link = Column(String(100))
    min_cpu = Column(String(50))
    min_gpu = Column(String(50))
    min_ram = Column(String(50))
    min_disk = Column(String(50))

class UserStatus(enum.Enum):
    online = "online"
    offline = "offline"

class Library(Base):
    __tablename__ = "library"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"), primary_key=True)
    purchase_date = Column(DateTime)
    is_owned = Column(Boolean, default=True)

    game = relationship("Game")
    user = relationship("User", back_populates="library_entries")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    profile_picture = Column(String(255), nullable=True)
    profile_description = Column(String(300), nullable=True)
    wallet_balance = Column(Numeric(10, 2), nullable=False, default=0)
    created_at = Column(TIMESTAMP, nullable=False)
    birth_date = Column(Date, nullable=False)
    country_id = Column(Integer, nullable=True)
    sum_points = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="offline")  # user_status jako string

    library_entries = relationship("Library", back_populates="user")

class UserUpdate(BaseModel):
    email: EmailStr
    profile_description: Optional[str] = None
    country_id: Optional[str] = None
    birth_date: Optional[date] = None
    status: Optional[str] = None

from sqlalchemy import DateTime, TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])