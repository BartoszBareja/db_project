from databases import Database

DATABASE_URL = "postgresql://postgres:test@localhost:5432/not_steam"

database = Database(DATABASE_URL)
