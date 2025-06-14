from pydantic import BaseModel, EmailStr
from datetime import date

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    birth_date: date

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True
