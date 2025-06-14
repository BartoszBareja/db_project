# app/dependencies.py

from fastapi import Depends, HTTPException, status, Cookie
from jose import jwt, JWTError
from app.database import database
from app.models import User  # jeśli masz model User SQLAlchemy
from sqlalchemy.orm import Session
from app.database import SessionLocal  # jeśli masz SessionLocal (patrz punkt 2)

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

# Dependency do pobierania sesji DB (jeśli używasz SQLAlchemy ORM)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency do pobierania aktualnego użytkownika na podstawie ciasteczka
async def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Brak tokenu")
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nieprawidłowy token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nieprawidłowy token")

    # Pobierz usera z bazy - w zależności od tego czy używasz `database.fetch_one` czy ORM:
    # Przykład z ORM:
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Użytkownik nie znaleziony")

    return user
