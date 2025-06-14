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
    query = "SELECT * FROM games WHERE id = :game_id"
    game = await database.fetch_one(query, values={"game_id": game_id})

    if not game:
        return HTMLResponse("<h1>Gra nie istnieje.</h1>", status_code=404)

    return templates.TemplateResponse("game.html", {
        "request": request,
        "game": game
    })

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()