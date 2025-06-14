from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import database

app = FastAPI()

# Montujemy folder statyczny
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Ustawiamy szablony
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    query_carousel = "SELECT id, title FROM games ORDER BY id ASC LIMIT 6"
    carousel_games = await database.fetch_all(query_carousel)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "carousel_games": carousel_games
    })


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

    # Pobierz achievementy
    achievements_query = """
        SELECT id, name, description, points
        FROM achievements
        WHERE game_id = :game_id
    """
    achievements = await database.fetch_all(achievements_query, values={"game_id": game_id})

    return templates.TemplateResponse("game.html", {
        "request": request,
        "game": game,
        "achievements": achievements
    })


@app.get("/producer/{producer_id}", response_class=HTMLResponse)
async def producer_detail(request: Request, producer_id: int):
    # Pobierz producenta
    producer_query = """
        SELECT p.*, c.name AS country_name
        FROM producers p
        JOIN countries c ON p.country_id = c.id
        WHERE p.id = :producer_id
    """
    producer = await database.fetch_one(producer_query, values={"producer_id": producer_id})

    if not producer:
        return HTMLResponse("<h1>Producent nie istnieje.</h1>", status_code=404)

    # Pobierz gry tego producenta
    games_query = "SELECT id, title FROM games WHERE producer_id = :producer_id"
    games = await database.fetch_all(games_query, values={"producer_id": producer_id})

    return templates.TemplateResponse("producer.html", {
        "request": request,
        "producer": producer,
        "games": games
    })

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()