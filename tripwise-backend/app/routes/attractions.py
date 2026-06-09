from fastapi import APIRouter, Query
from app.ai.ai_service import geocode_place, fetch_attraction_image
import asyncio, httpx

router = APIRouter()

# Hardcoded well-known attractions per destination for fast lookup
KNOWN_ATTRACTIONS: dict[str, list[dict]] = {
    "jaipur": [
        {"name": "Hawa Mahal", "type": "Palace"},
        {"name": "Amber Fort", "type": "Fort"},
        {"name": "City Palace Jaipur", "type": "Palace"},
        {"name": "Jantar Mantar Jaipur", "type": "Observatory"},
        {"name": "Nahargarh Fort", "type": "Fort"},
        {"name": "Jal Mahal", "type": "Palace"},
    ],
    "manali": [
        {"name": "Rohtang Pass", "type": "Mountain Pass"},
        {"name": "Solang Valley", "type": "Valley"},
        {"name": "Hadimba Temple", "type": "Temple"},
        {"name": "Old Manali", "type": "Village"},
        {"name": "Beas River", "type": "River"},
    ],
    "goa": [
        {"name": "Baga Beach", "type": "Beach"},
        {"name": "Dudhsagar Falls", "type": "Waterfall"},
        {"name": "Basilica of Bom Jesus", "type": "Church"},
        {"name": "Fort Aguada", "type": "Fort"},
        {"name": "Anjuna Flea Market", "type": "Market"},
    ],
    "kerala": [
        {"name": "Alleppey Backwaters", "type": "Backwaters"},
        {"name": "Munnar Tea Gardens", "type": "Plantation"},
        {"name": "Kovalam Beach", "type": "Beach"},
        {"name": "Periyar Wildlife Sanctuary", "type": "Wildlife"},
    ],
}

@router.get("/")
async def get_attractions(
    destination: str = Query(..., description="e.g. Jaipur, Rajasthan"),
    limit: int = Query(default=6, ge=1, le=12)
):
    key = destination.lower().split(",")[0].strip()
    base_list = KNOWN_ATTRACTIONS.get(key, [])[:limit]

    # If not in hardcoded list, try to get attractions via Nominatim nearby query
    if not base_list:
        return {"destination": destination, "attractions": [], "message": "No cached attractions — use AI plan endpoint"}

    # Enrich with coords + images in parallel
    async def enrich(attr):
        full_name = f"{attr['name']}, {destination}"
        img, coords = await asyncio.gather(
            fetch_attraction_image(attr["name"], destination),
            geocode_place(full_name)
        )
        return {**attr, "img": img, "coords": coords}

    enriched = await asyncio.gather(*[enrich(a) for a in base_list])
    return {"destination": destination, "attractions": list(enriched)}

@router.get("/image")
async def attraction_image(
    name: str = Query(...),
    destination: str = Query(default="")
):
    img = await fetch_attraction_image(name, destination)
    return {"name": name, "img": img}
