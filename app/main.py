from fastapi import FastAPI, Request, Form, Depends, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Cookie
from app.database import database

from app.database import database
from app.models import User  # Upewnij się, że masz SQLAlchemy model User

import os

from fastapi import Form, Request, Depends, APIRouter, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User


SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Middleware do odczytu tokenu z ciasteczka
@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    token = request.cookies.get("access_token")
    request.state.user = None
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                query = "SELECT * FROM users WHERE username = :username"
                user = await database.fetch_one(query, values={"username": username})
                request.state.user = user
        except JWTError:
            pass
    response = await call_next(request)
    return response

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request, access_token: str = Cookie(default=None)):
    query_carousel = "SELECT id, title FROM games ORDER BY id ASC LIMIT 6"
    carousel_games = await database.fetch_all(query_carousel)

    current_user = None
    if access_token:
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                record = await database.fetch_one(
                    "SELECT id, username FROM users WHERE username = :username",
                    {"username": username}
                )
                current_user = dict(record) if record else None
        except JWTError:
            pass  # Nieprawidłowy token – ignorujemy

    return templates.TemplateResponse("index.html", {
        "request": request,
        "carousel_games": carousel_games,
        "current_user": current_user
    })

@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    birth_date: str = Form(...)
):
    try:
        parsed_birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
    except ValueError:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Nieprawidłowy format daty urodzenia."
        })

    existing = await database.fetch_one("SELECT id FROM users WHERE username = :username OR email = :email", {
        "username": username, "email": email
    })
    if existing:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Użytkownik o takim loginie lub emailu już istnieje."
        })

    hashed = pwd_context.hash(password)

    query = """
    INSERT INTO users (username, email, password_hash, birth_date, wallet_balance, sum_points, status, created_at)
    VALUES (:username, :email, :password_hash, :birth_date, 0, 0, 'offline', :created_at)
    """
    await database.execute(query, {
        "username": username,
        "email": email,
        "password_hash": hashed,
        "birth_date": parsed_birth_date,
        "created_at": datetime.utcnow()
    })
    return RedirectResponse("/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    user = await database.fetch_one("SELECT * FROM users WHERE username = :username", {"username": username})
    if not user or not pwd_context.verify(password, user["password_hash"]):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Nieprawidłowy login lub hasło."
        })

    # Tworzymy token JWT
    data = {"sub": user["username"]}
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    response = RedirectResponse("/", status_code=302)
    response.set_cookie("access_token", token, httponly=True)
    response.set_cookie("user_id", user["id"])
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    return response

@app.get("/game/{game_id}", response_class=HTMLResponse)
async def game_detail(request: Request, game_id: int):
    query = """
        SELECT g.*, p.name AS producer_name, p.id AS producer_id
        FROM games g
        JOIN producers p ON g.producer_id = p.id
        WHERE g.id = :game_id
    """
    game = await database.fetch_one(query, values={"game_id": game_id})

    if not game:
        return HTMLResponse("<h1>Gra nie istnieje.</h1>", status_code=404)

    achievements_query = """
        SELECT id, name, description, points
        FROM achievements
        WHERE game_id = :game_id
    """
    achievements = await database.fetch_all(achievements_query, values={"game_id": game_id})

    return templates.TemplateResponse("game.html", {
        "request": request,
        "game": game,
        "achievements": achievements,
        "user": request.state.user
    })

@app.post("/game/{game_id}/add_to_library")
async def add_to_library(game_id: int, access_token: Optional[str] = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Nie jesteś zalogowany")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token")

    user = await database.fetch_one("SELECT id FROM users WHERE username = :username", {"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie znaleziony")

    # Sprawdź, czy gra już jest w bibliotece
    exists = await database.fetch_one(
        "SELECT 1 FROM library WHERE user_id = :user_id AND game_id = :game_id",
        {"user_id": user["id"], "game_id": game_id}
    )
    if exists:
        return {"message": "Gra jest już w bibliotece"}

    # Dodaj do biblioteki
    await database.execute(
        """
        INSERT INTO library (user_id, game_id, purchase_date, is_owned)
        VALUES (:user_id, :game_id, :purchase_date, true)
        """,
        {"user_id": user["id"], "game_id": game_id, "purchase_date": datetime.utcnow()}
    )

    return {"message": "Dodano do biblioteki"}

@app.post("/game/{game_id}/add_to_wishlist")
async def add_to_wishlist(game_id: int, access_token: Optional[str] = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Nie jesteś zalogowany")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token")

    user = await database.fetch_one("SELECT id FROM users WHERE username = :username", {"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie znaleziony")

    # Sprawdź, czy gra już jest w wishlist
    exists = await database.fetch_one(
        "SELECT 1 FROM wishlist WHERE user_id = :user_id AND game_id = :game_id",
        {"user_id": user["id"], "game_id": game_id}
    )
    if exists:
        return {"message": "Gra jest już na liście życzeń"}

    # Dodaj do wishlist
    await database.execute(
        """
        INSERT INTO wishlist (user_id, game_id, added_at)
        VALUES (:user_id, :game_id, :added_at)
        """,
        {"user_id": user["id"], "game_id": game_id, "added_at": datetime.utcnow()}
    )

    return {"message": "Dodano do listy życzeń"}

@app.get("/producer/{producer_id}", response_class=HTMLResponse)
async def producer_detail(request: Request, producer_id: int):
    producer_query = """
        SELECT p.*, c.name AS country_name
        FROM producers p
        JOIN countries c ON p.country_id = c.id
        WHERE p.id = :producer_id
    """
    producer = await database.fetch_one(producer_query, values={"producer_id": producer_id})

    if not producer:
        return HTMLResponse("<h1>Producent nie istnieje.</h1>", status_code=404)

    games_query = "SELECT id, title FROM games WHERE producer_id = :producer_id"
    games = await database.fetch_all(games_query, values={"producer_id": producer_id})

    return templates.TemplateResponse("producer.html", {
        "request": request,
        "producer": producer,
        "games": games,
        "user": request.state.user
    })

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/friends", response_class=HTMLResponse)
async def friends_page(request: Request, access_token: str = Cookie(default=None)):
    current_user = None
    if access_token:
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                user_record = await database.fetch_one("SELECT id, username FROM users WHERE username = :username", {"username": username})
                if user_record:
                    current_user = dict(user_record)
        except jwt.PyJWTError:
            pass

    if not current_user:
        return RedirectResponse("/login", status_code=302)

    # Szukamy znajomych
    query = """
    SELECT u.id, u.username, f.friends_since
    FROM friends f
    JOIN users u ON u.id = CASE WHEN f.user1_id = :user_id THEN f.user2_id ELSE f.user1_id END
    WHERE f.user1_id = :user_id OR f.user2_id = :user_id
    ORDER BY f.friends_since DESC
    """
    friends = await database.fetch_all(query, {"user_id": current_user["id"]})

    return templates.TemplateResponse("friends.html", {
        "request": request,
        "current_user": current_user,
        "friends": friends
    })

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from .dependencies import get_db, get_current_user  # przykładowo
from .models import Library

router = APIRouter()

@app.get("/library", response_class=HTMLResponse)
async def user_library(request: Request, access_token: str = Cookie(None)):
    if not access_token:
        return RedirectResponse("/login", status_code=302)
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        return RedirectResponse("/login", status_code=302)

    user = await database.fetch_one("SELECT * FROM users WHERE username = :username", {"username": username})
    if not user:
        return RedirectResponse("/login", status_code=302)

    query = """
    SELECT g.*
    FROM library l
    JOIN games g ON l.game_id = g.id
    WHERE l.user_id = :user_id AND l.is_owned = true
    """
    games = await database.fetch_all(query, {"user_id": user["id"]})

    return templates.TemplateResponse("library.html", {
        "request": request,
        "games": games,
        "current_user": user,
        "time": int(datetime.utcnow().timestamp())
    })

async def get_user_achievements(user_id: int):
    query = """
    SELECT a.id, a.name, a.description, a.points, a.game_id
    FROM achievements a
    JOIN library l ON l.game_id = a.game_id
    WHERE l.user_id = :user_id AND l.is_owned = true
    """
    achievements = await database.fetch_all(query, {"user_id": user_id})
    return achievements

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, access_token: str = Cookie(None)):
    if not access_token:
        return RedirectResponse("/login", status_code=302)

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        return RedirectResponse("/login", status_code=302)

    user = await database.fetch_one("SELECT * FROM users WHERE username = :username", {"username": username})
    if not user:
        return RedirectResponse("/login", status_code=302)

    wishlist_query = """
    SELECT g.id, g.title
    FROM wishlist w
    JOIN games g ON w.game_id = g.id
    WHERE w.user_id = :user_id
    ORDER BY w.added_at DESC
    """
    wishlist = await database.fetch_all(wishlist_query, {"user_id": user["id"]})

    achievements = await get_user_achievements(user["id"])

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "wishlist": wishlist,
        "achievements": achievements,
    })


@app.get("/profile/edit")
async def edit_profile_get(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("edit_profile.html", {"request": request, "user": current_user})

@app.post("/profile/edit")
async def edit_profile_post(
    request: Request,
    email: Optional[str] = Form(None),
    profile_description: Optional[str] = Form(None),
    country_id: Optional[int] = Form(None),
    birth_date: Optional[str] = Form(None),
    status_user: Optional[str] = Form(None),
    access_token: Optional[str] = Cookie(None),
):
    if not access_token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        return RedirectResponse(url="/login", status_code=302)

    user = await database.fetch_one("SELECT * FROM users WHERE username = :username", {"username": username})
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    birth_date_obj = None
    if birth_date:
        try:
            from datetime import datetime
            birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
        except ValueError:
            birth_date_obj = None

    # Budujemy dynamiczne dane do update (pomijamy None)
    update_data = {}
    if email is not None:
        update_data["email"] = email
    if profile_description is not None:
        update_data["profile_description"] = profile_description
    if country_id is not None:
        update_data["country_id"] = country_id
    if birth_date_obj is not None:
        update_data["birth_date"] = birth_date_obj
    if status_user is not None:
        update_data["status"] = status_user

    if update_data:
        set_clause = ", ".join(f"{k} = :{k}" for k in update_data.keys())
        update_data["user_id"] = user["id"]

        query = f"UPDATE users SET {set_clause} WHERE id = :user_id"
        await database.execute(query, update_data)

    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)