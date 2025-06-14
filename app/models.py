from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base

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
