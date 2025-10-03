from fastapi import FastAPI
from app.db.database import engine, Base
from app.api.api import api_router
from app.db.init_db import init_database

# Инициализируем базу данных при старте приложения
init_database()

app = FastAPI(
    title="Online Store API",
    description="Backend for online store with products, categories, reviews and cart",
    version="1.0.0"
)

# Include API router
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Online Store API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}