import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Request, Form, Depends, Response, HTTPException, Cookie, Query, WebSocket, \
    WebSocketDisconnect, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import database, SessionLocal, get_db
from app.models import User, Message, Game, Library

# Configuration
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Initialize components
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# WebSocket connections storage
connections = {}


# Middleware
@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    """Middleware to read token from cookie and add user to request state"""
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


# Helper functions
async def get_current_user(access_token: Optional[str] = Cookie(None)):
    """Get current user from JWT token"""
    if not access_token:
        return None

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username:
            user_record = await database.fetch_one(
                "SELECT * FROM users WHERE username = :username",
                {"username": username}
            )
            return dict(user_record) if user_record else None
    except JWTError:
        return None

async def get_optional_user(access_token: Optional[str] = Cookie(None)):
    if not access_token:
        return None
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
        user = await database.fetch_one(
            "SELECT * FROM users WHERE username = :username",
            {"username": username}
        )
        return dict(user) if user else None
    except JWTError:
        return None

async def get_user_achievements(user_id: int):
    """Get user achievements based on owned games"""
    query = """
    SELECT a.id, a.name, a.description, a.points, a.game_id
    FROM achievements a
    JOIN library l ON l.game_id = a.game_id
    WHERE l.user_id = :user_id AND l.is_owned = true
    """
    achievements = await database.fetch_all(query, {"user_id": user_id})
    return achievements


# Routes - Authentication
@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    """Display registration form"""
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
async def register_post(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        birth_date: str = Form(...)
):
    """Handle user registration"""
    try:
        parsed_birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
    except ValueError:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Nieprawidłowy format daty urodzenia."
        })

    # Check if user already exists
    existing = await database.fetch_one(
        "SELECT id FROM users WHERE username = :username OR email = :email",
        {"username": username, "email": email}
    )
    if existing:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Użytkownik o takim loginie lub emailu już istnieje."
        })

    # Create new user
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
    """Display login form"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login_post(
        request: Request,
        response: Response,
        username: str = Form(...),
        password: str = Form(...)
):
    """Handle user login"""
    user = await database.fetch_one(
        "SELECT * FROM users WHERE username = :username",
        {"username": username}
    )

    if not user or not pwd_context.verify(password, user["password_hash"]):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Nieprawidłowy login lub hasło."
        })

    # Create JWT token
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
    """Handle user logout"""
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    return response


# Routes - Main Pages
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request, access_token: str = Cookie(default=None)):
    """Display homepage with game carousels and genres"""
    # Get 6 games for carousel with thumbnails
    query_carousel = """
        SELECT g.id, g.title, i.filename
        FROM games g
        LEFT JOIN images i ON g.id = i.game_id AND i.is_thumbnail = TRUE
        ORDER BY g.id ASC
        LIMIT 6
    """
    carousel_games = await database.fetch_all(query_carousel)

    # Get 8 newest games with thumbnails
    query_new_games = """
        SELECT g.id, g.title, i.filename
        FROM games g
        LEFT JOIN images i ON g.id = i.game_id AND i.is_thumbnail = TRUE
        ORDER BY g.release_date DESC
        LIMIT 8
    """
    new_games = await database.fetch_all(query_new_games)

    # Get genres with sample game and thumbnail
    query_genres = """
        SELECT gen.id AS genre_id, gen.name AS genre_name, g.id AS game_id, 
               g.title AS game_title, i.filename AS image_filename
        FROM genres gen
        JOIN game_genres gg ON gen.id = gg.genre_id
        JOIN games g ON gg.game_id = g.id
        LEFT JOIN images i ON g.id = i.game_id AND i.is_thumbnail = TRUE
        WHERE g.release_date = (
            SELECT MIN(g2.release_date)
            FROM game_genres gg2
            JOIN games g2 ON gg2.game_id = g2.id
            WHERE gg2.genre_id = gen.id
        )
        ORDER BY gen.name
    """
    genres_with_game = await database.fetch_all(query_genres)

    # Get current user info
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
            pass

    return templates.TemplateResponse("index.html", {
        "request": request,
        "carousel_games": carousel_games,
        "new_games": new_games,
        "genres_with_game": genres_with_game,
        "current_user": current_user
    })


@app.get("/genre/{genre_id}", response_class=HTMLResponse)
async def genre_page(request: Request, genre_id: int, current_user: Optional[dict] = Depends(get_optional_user)):
    """Display games by genre"""
    genre = await database.fetch_one("SELECT * FROM genres WHERE id = :id", {"id": genre_id})
    if not genre:
        raise HTTPException(status_code=404, detail="Gatunek nie znaleziony")

    games = await database.fetch_all("""
        SELECT g.id, g.title, i.filename AS thumbnail_filename
        FROM games g
        JOIN game_genres gg ON gg.game_id = g.id
        LEFT JOIN images i ON i.game_id = g.id AND i.is_thumbnail = TRUE
        WHERE gg.genre_id = :genre_id
        ORDER BY g.title ASC
    """, {"genre_id": genre_id})

    return templates.TemplateResponse("genre.html", {
        "request": request,
        "genre": genre,
        "games": games,
        "current_user": current_user
    })



# Routes - Game Management
from fastapi import HTTPException  # dodaj ten import, jeśli go nie ma

@app.get("/game/{game_id}", response_class=HTMLResponse, )
async def game_detail(request: Request, game_id: int,  current_user: Optional[dict] = Depends(get_optional_user)):
    """Display game details"""

    # Pobierz dane gry z producentem
    query = """
        SELECT g.*, p.name AS producer_name, p.id AS producer_id
        FROM games g
        JOIN producers p ON g.producer_id = p.id
        WHERE g.id = :game_id
    """
    game = await database.fetch_one(query, values={"game_id": game_id})
    if not game:
        raise HTTPException(status_code=404, detail="Gra nie została znaleziona.")

    # Pobierz gatunki gry
    genres_query = """
        SELECT gen.name
        FROM genres gen
        JOIN game_genres gg ON gen.id = gg.genre_id
        WHERE gg.game_id = :game_id
    """
    genres = await database.fetch_all(genres_query, values={"game_id": game_id})
    genre_list = [g["name"] for g in genres]

    # Pobierz osiągnięcia
    achievements_query = """
        SELECT id, name, description, points
        FROM achievements
        WHERE game_id = :game_id
    """
    achievements = await database.fetch_all(achievements_query, values={"game_id": game_id})

    # Pobierz oceny i recenzje
    ratings_query = """
        SELECT r.rating, r.description, r.rated_at, u.username, u.id AS user_id
        FROM game_ratings r
        JOIN users u ON r.user_id = u.id
        WHERE r.game_id = :game_id
        ORDER BY r.rated_at DESC
    """
    ratings = await database.fetch_all(ratings_query, values={"game_id": game_id})

    # Pobierz zalogowanego użytkownika
    user = request.state.user

    library_friends = []
    wishlist_friends = []

    if user:
        # Pobierz ID znajomych
        friends_query = """
            SELECT 
                CASE 
                    WHEN f.user1_id = :user_id THEN f.user2_id
                    ELSE f.user1_id
                END AS friend_id
            FROM friends f
            WHERE f.user1_id = :user_id OR f.user2_id = :user_id
        """
        friends = await database.fetch_all(friends_query, values={"user_id": user.id})
        friends_ids = [f["friend_id"] for f in friends]

        if friends_ids:
            # Znajomi z grą w bibliotece
            library_query = """
                SELECT u.username
                FROM library l
                JOIN users u ON l.user_id = u.id
                WHERE l.game_id = :game_id AND l.user_id = ANY(:friend_ids)
            """
            library_friends = await database.fetch_all(
                library_query, values={"game_id": game_id, "friend_ids": friends_ids}
            )

            # Znajomi z grą na liście życzeń
            wishlist_query = """
                SELECT u.username
                FROM wishlist w
                JOIN users u ON w.user_id = u.id
                WHERE w.game_id = :game_id AND w.user_id = ANY(:friend_ids)
            """
            wishlist_friends = await database.fetch_all(
                wishlist_query, values={"game_id": game_id, "friend_ids": friends_ids}
            )

    return templates.TemplateResponse("game.html", {
        "request": request,
        "game": game,
        "achievements": achievements,
        "ratings": ratings,
        "genres": genre_list,
        "user": user,
        "current_user": current_user,
        "library_friends": [f["username"] for f in library_friends] if library_friends else [],
        "wishlist_friends": [f["username"] for f in wishlist_friends] if wishlist_friends else []
    })

@app.post("/game/{game_id}/add_to_library")
async def add_to_library(game_id: int, access_token: Optional[str] = Cookie(None)):
    """Add game to user library"""
    if not access_token:
        raise HTTPException(status_code=401, detail="Nie jesteś zalogowany")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token")

    user = await database.fetch_one(
        "SELECT id FROM users WHERE username = :username",
        {"username": username}
    )
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie znaleziony")

    # Check if game already in library
    exists = await database.fetch_one(
        "SELECT 1 FROM library WHERE user_id = :user_id AND game_id = :game_id",
        {"user_id": user["id"], "game_id": game_id}
    )
    if exists:
        return {"message": "Gra jest już w bibliotece"}

    # Add to library
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
    """Add game to user wishlist"""
    if not access_token:
        raise HTTPException(status_code=401, detail="Nie jesteś zalogowany")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token")

    user = await database.fetch_one(
        "SELECT id FROM users WHERE username = :username",
        {"username": username}
    )
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie znaleziony")

    # Check if game already in wishlist
    exists = await database.fetch_one(
        "SELECT 1 FROM wishlist WHERE user_id = :user_id AND game_id = :game_id",
        {"user_id": user["id"], "game_id": game_id}
    )
    if exists:
        return {"message": "Gra jest już na liście życzeń"}

    # Add to wishlist
    await database.execute(
        """
        INSERT INTO wishlist (user_id, game_id, added_at)
        VALUES (:user_id, :game_id, :added_at)
        """,
        {"user_id": user["id"], "game_id": game_id, "added_at": datetime.utcnow()}
    )

    return {"message": "Dodano do listy życzeń"}


# Routes - User Management
@app.get("/library", response_class=HTMLResponse)
async def user_library(request: Request, access_token: str = Cookie(None)):
    """Display user's game library"""
    if not access_token:
        return RedirectResponse("/login", status_code=302)

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        return RedirectResponse("/login", status_code=302)

    user = await database.fetch_one(
        "SELECT * FROM users WHERE username = :username",
        {"username": username}
    )
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


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(
        request: Request,
        username: Optional[str] = Query(None),
        current_user: dict = Depends(get_current_user)
):
    """Display user profile"""
    if username:
        user = await database.fetch_one(
            "SELECT * FROM users WHERE username = :username",
            {"username": username}
        )
        if not user:
            return HTMLResponse("<h1>Użytkownik nie istnieje.</h1>", status_code=404)
    else:
        if not current_user:
            return RedirectResponse("/login", status_code=302)
        user = current_user

    # Get user's wishlist
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
        "current_user": current_user,
    })

@app.get("/profile/{user_id}", response_class=HTMLResponse)
async def user_profile_page(
    request: Request,
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    user = await database.fetch_one("SELECT * FROM users WHERE id = :id", {"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie istnieje.")

    # Pobierz znajomych użytkownika
    friends_query = """
    SELECT u.id, u.username
    FROM friends f
    JOIN users u ON (u.id = CASE WHEN f.user1_id = :user_id THEN f.user2_id ELSE f.user1_id END)
    WHERE :user_id IN (f.user1_id, f.user2_id)
    """
    friends = await database.fetch_all(friends_query, {"user_id": user_id})

    # Sprawdź, czy current_user jest już znajomym z user_id
    is_friend_query = """
    SELECT 1 FROM friends
    WHERE 
        (user1_id = :current_id AND user2_id = :target_id)
        OR 
        (user1_id = :target_id AND user2_id = :current_id)
    """
    is_friend = await database.fetch_one(is_friend_query, {
        "current_id": current_user["id"],
        "target_id": user_id
    })

    wishlist_query = """
    SELECT g.id, g.title
    FROM wishlist w
    JOIN games g ON w.game_id = g.id
    WHERE w.user_id = :user_id
    ORDER BY w.added_at DESC
    """
    wishlist = await database.fetch_all(wishlist_query, {"user_id": user_id})
    achievements = await get_user_achievements(user_id)

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "friends": friends,
        "wishlist": wishlist,
        "achievements": achievements,
        "current_user": current_user,
        "is_friend": bool(is_friend)
    })

@app.post("/friends/add/{user_id}")
async def add_friend(user_id: int, current_user: dict = Depends(get_current_user)):
    existing = await database.fetch_one("""
        SELECT 1 FROM friends
        WHERE 
            (user1_id = :uid1 AND user2_id = :uid2)
            OR
            (user1_id = :uid2 AND user2_id = :uid1)
    """, {"uid1": current_user["id"], "uid2": user_id})

    if existing:
        raise HTTPException(status_code=400, detail="Już jesteście znajomymi")

    await database.execute("""
        INSERT INTO friends (user1_id, user2_id, friends_since)
        VALUES (:uid1, :uid2, NOW())
    """, {"uid1": current_user["id"], "uid2": user_id})

    return RedirectResponse(url=f"/profile/{user_id}", status_code=303)


@app.get("/profile/edit")
async def edit_profile_get(request: Request, current_user: User = Depends(get_current_user)):
    """Display profile edit form"""
    return templates.TemplateResponse("edit_profile.html", {
        "request": request,
        "user": current_user
    })


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
    """Handle profile edit submission"""
    if not access_token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        return RedirectResponse(url="/login", status_code=302)

    user = await database.fetch_one(
        "SELECT * FROM users WHERE username = :username",
        {"username": username}
    )
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Parse birth date
    birth_date_obj = None
    if birth_date:
        try:
            birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
        except ValueError:
            birth_date_obj = None

    # Build dynamic update data (skip None values)
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

    # Update user data if there are changes
    if update_data:
        set_clause = ", ".join(f"{k} = :{k}" for k in update_data.keys())
        update_data["user_id"] = user["id"]

        query = f"UPDATE users SET {set_clause} WHERE id = :user_id"
        await database.execute(query, update_data)

    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/friends", response_class=HTMLResponse)
async def friends_page(request: Request, access_token: str = Cookie(default=None)):
    """Display user's friends list"""
    current_user = None
    if access_token:
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                user_record = await database.fetch_one(
                    "SELECT id, username FROM users WHERE username = :username",
                    {"username": username}
                )
                if user_record:
                    current_user = dict(user_record)
        except jwt.PyJWTError:
            pass

    if not current_user:
        return RedirectResponse("/login", status_code=302)

    # Get friends
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


# Routes - Producer
@app.get("/producer/{producer_id}", response_class=HTMLResponse)
async def producer_detail(request: Request, producer_id: int,  current_user: Optional[dict] = Depends(get_optional_user)):
    """Display producer details"""
    producer_query = """
        SELECT p.*, c.name AS country_name
        FROM producers p
        LEFT JOIN countries c ON p.country_id = c.id
        WHERE p.id = :producer_id
    """
    producer = await database.fetch_one(producer_query, values={"producer_id": producer_id})

    if not producer:
        return HTMLResponse("<h1>Producent nie znaleziony.</h1>", status_code=404)

    # Get producer's games
    games_query = """
        SELECT id, title
        FROM games
        WHERE producer_id = :producer_id
    """
    games = await database.fetch_all(games_query, values={"producer_id": producer_id})

    # Get producer ratings
    ratings_query = """
        SELECT r.rating, r.description, r.rated_at, u.username, u.id AS user_id
        FROM producer_ratings r
        JOIN users u ON r.user_id = u.id
        WHERE r.producer_id = :producer_id
        ORDER BY r.rated_at DESC
    """
    ratings = await database.fetch_all(ratings_query, values={"producer_id": producer_id})

    return templates.TemplateResponse("producer.html", {
        "request": request,
        "producer": producer,
        "games": games,
        "ratings": ratings,
        "user": request.state.user,
        "current_user": current_user
    })


# Routes - Search
@app.get("/search")
def search(q: str, db: Session = Depends(get_db)):
    """Search for games and users"""
    query = f"%{q.lower()}%"
    games = db.query(Game).filter(Game.title.ilike(query)).limit(5).all()
    users = db.query(User).filter(User.username.ilike(query)).limit(5).all()

    return JSONResponse({
        "games": [{"id": g.id, "title": g.title} for g in games],
        "users": [{"id": u.id, "username": u.username} for u in users],
    })


# Routes - Chat/WebSocket
@app.websocket("/ws/chat/{user_id}/{friend_id}")
async def chat_ws(websocket: WebSocket, user_id: int, friend_id: int):
    """Handle WebSocket chat connection"""
    await websocket.accept()

    # Store connection
    connections.setdefault(user_id, {})
    connections[user_id][friend_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()

            # Save message to database
            db: Session = SessionLocal()
            message = Message(sender_id=user_id, receiver_id=friend_id, content=data)
            db.add(message)
            db.commit()
            db.close()

            # Send to receiver if online
            if friend_id in connections and user_id in connections[friend_id]:
                await connections[friend_id][user_id].send_text(f"Friend: {data}")

            # Confirmation to sender
            await websocket.send_text(f"You: {data}")

    except WebSocketDisconnect:
        # Remove connection on disconnect
        if user_id in connections and friend_id in connections[user_id]:
            del connections[user_id][friend_id]


@app.get("/chat/history/{user_id}/{friend_id}")
def get_chat_history(user_id: int, friend_id: int, db: Session = Depends(get_db)):
    """Get chat history between two users"""
    messages = db.query(Message).filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == friend_id)) |
        ((Message.sender_id == friend_id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp).all()

    history = []
    for msg in messages:
        history.append({
            "sender": "Ty" if msg.sender_id == user_id else "Znajomy",
            "sender_id": msg.sender_id,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
        })

    return JSONResponse(content=history)


# Event handlers
@app.on_event("startup")
async def startup():
    """Connect to database on startup"""
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    """Disconnect from database on shutdown"""
    await database.disconnect()

from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Obsługa 404 - nie znaleziono strony
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return HTMLResponse(str(exc.detail), status_code=exc.status_code)

# Obsługa błędów walidacji (np. złe typy w URL)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return templates.TemplateResponse("error.html", {"request": request, "detail": str(exc)}, status_code=400)

# Możesz też dodać globalny fallback
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("error.html", {"request": request, "detail": str(exc)}, status_code=500)
