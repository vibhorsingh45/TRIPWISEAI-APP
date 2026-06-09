from fastapi import APIRouter, Query, HTTPException
from app.ai.ai_service import geocode_place

router = APIRouter()

@router.get("/")
async def geocode(place: str = Query(..., description="Place name to geocode, e.g. Hawa Mahal, Jaipur")):
    result = await geocode_place(place)
    if not result:
        raise HTTPException(404, f"Could not geocode '{place}'")
    return result

@router.get("/destination-map")
async def destination_map(destination: str = Query(...)):
    """
    Returns main coordinates + a static OSM tile URL for embedding.
    """
    coords = await geocode_place(destination)
    if not coords:
        raise HTTPException(404, "Destination not found")

    lat, lon = coords["lat"], coords["lon"]
    zoom = 12
    osm_tile_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map={zoom}/{lat}/{lon}"

    return {
        "destination": destination,
        "coords": coords,
        "osm_url": osm_tile_url,
        "embed_url": f"https://www.openstreetmap.org/export/embed.html?bbox={lon-0.1},{lat-0.1},{lon+0.1},{lat+0.1}&layer=mapnik&marker={lat},{lon}"
    }
