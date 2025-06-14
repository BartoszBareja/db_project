from fastapi import FastAPI, Request, Form, Depends, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Cookie
from app.database import database

from app.database import database
from app.models import User  # Upewnij się, że masz SQLAlchemy model User

import os

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
