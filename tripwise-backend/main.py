from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.db import engine, Base
from app.routes import trips, attractions, auth, geocode

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="TripWise AI",
    description="AI-powered travel planning backend",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/api/auth",        tags=["Auth"])
app.include_router(trips.router,       prefix="/api/trips",       tags=["Trips"])
app.include_router(attractions.router, prefix="/api/attractions", tags=["Attractions"])
app.include_router(geocode.router,     prefix="/api/geocode",     tags=["Geocode"])

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "TripWise AI backend is running 🚀"}
