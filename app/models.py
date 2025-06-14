from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Numeric, TIMESTAMP, ForeignKey, Enum, DateTime as PgEnum
import enum

Base = declarative_base()

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

Base = declarative_base()


class UserStatus(enum.Enum):
    online = "online"
    offline = "offline"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    profile_picture = Column(String(255))
    profile_description = Column(String(300))
    wallet_balance = Column(Numeric(10, 2), nullable=False, default=0)
    created_at = Column(TIMESTAMP, nullable=False)
    birth_date = Column(Date, nullable=False)
    country_id = Column(Integer)
    sum_points = Column(Integer, nullable=False, default=0)
    status = Column(PgEnum(UserStatus), nullable=False, default=UserStatus.offline)
