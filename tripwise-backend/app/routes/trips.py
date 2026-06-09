from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database.db import get_db
from app.models.models import Trip
from app.schemas.schemas import TripRequest, TripOut
from app.ai.ai_service import get_ai_trip_plan, geocode_place, fetch_attraction_image
from app.utils.auth_utils import get_current_user_id
import asyncio

router = APIRouter()

async def enrich_destinations(destinations: list) -> list:
    """Add real coordinates + attraction images to each destination."""
    enriched = []
    for dest in destinations:
        # Geocode the destination city
        coords = await geocode_place(dest.get("name", ""))

        # Hero image for the destination
        hero_img = await fetch_attraction_image(dest.get("name", ""), "")

        # Enrich each attraction with coords + image
        attractions = []
        for attr in dest.get("attractions", []):
            img, attr_coords = await asyncio.gather(
                fetch_attraction_image(attr["name"], dest["name"]),
                geocode_place(f"{attr['name']}, {dest['name']}")
            )
            attractions.append({**attr, "img": img, "coords": attr_coords})

        enriched.append({
            **dest,
            "heroImg": hero_img,
            "coords": coords,
            "attractions": attractions
        })
    return enriched

@router.post("/plan", status_code=200)
async def plan_trip(body: TripRequest, db: Session = Depends(get_db)):
    """
    Main planning endpoint — calls Claude AI, enriches with
    real geocoordinates and attraction photos, saves to DB.
    """
    try:
        ai_result = await get_ai_trip_plan(body)
    except Exception as e:
        raise HTTPException(502, f"AI service error: {str(e)}")

    # Enrich destinations with live data
    ai_result["destinations"] = await enrich_destinations(ai_result.get("destinations", []))

    # Persist (no auth required — guest trips also saved)
    trip = Trip(
        source_city=body.source_city,
        destination=body.destination,
        budget=body.budget,
        travelers=body.travelers,
        days=body.days,
        travel_style=body.travel_style,
        top_destination=ai_result.get("top_destination"),
        ai_result=ai_result,
    )
    db.add(trip); db.commit(); db.refresh(trip)

    return {"trip_id": trip.id, **ai_result}

@router.get("/history", response_model=list[TripOut])
def trip_history(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return db.query(Trip).filter(Trip.user_id == user_id).order_by(Trip.created_at.desc()).limit(20).all()

@router.get("/{trip_id}", response_model=TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    return trip

@router.delete("/{trip_id}", status_code=204)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found or not yours")
    db.delete(trip); db.commit()
