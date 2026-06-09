from dotenv import load_dotenv
load_dotenv()
import os, json, httpx
from app.schemas.schemas import TripRequest

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL     = "https://openrouter.ai/api/v1/chat/completions"
UNSPLASH_KEY       = os.getenv("UNSPLASH_ACCESS_KEY", "")

def allocate_budget(budget: float, days: int, travelers: int) -> dict:
    per_person = budget / max(travelers, 1)
    if per_person < 5000:
        w = {"transport": 0.40, "hotel": 0.30, "food": 0.20, "activities": 0.10}
    elif per_person < 15000:
        w = {"transport": 0.30, "hotel": 0.35, "food": 0.22, "activities": 0.13}
    else:
        w = {"transport": 0.25, "hotel": 0.38, "food": 0.20, "activities": 0.17}
    return {k: round(budget * v) for k, v in w.items()}

async def get_ai_trip_plan(req: TripRequest) -> dict:
    budget_split = allocate_budget(req.budget, req.days, req.travelers)

    prompt = f"""You are TripWise AI, a premium Indian travel advisor.

User trip details:
- From: {req.source_city}
- Preference: {req.destination}
- Days: {req.days}
- Travelers: {req.travelers}
- Budget: ₹{req.budget:,.0f} total
- Style: {req.travel_style}

Suggested budget split:
Transport ₹{budget_split['transport']}, Hotel ₹{budget_split['hotel']}, Food ₹{budget_split['food']}, Activities ₹{budget_split['activities']}

Respond ONLY with a valid JSON object — no markdown, no extra text:
{{
  "budget_breakdown": {{"transport": <n>, "hotel": <n>, "food": <n>, "activities": <n>}},
  "destinations": [
    {{
      "name": "City, State/Country",
      "country": "Country",
      "budget": <n>,
      "reason": "2-sentence explanation",
      "best_season": "Month range",
      "language": "Primary language",
      "currency": "Name + symbol",
      "attractions": [
        {{"name": "...", "type": "Temple/Beach/Museum/etc", "desc": "1 sentence"}},
        {{"name": "...", "type": "...", "desc": "..."}},
        {{"name": "...", "type": "...", "desc": "..."}},
        {{"name": "...", "type": "...", "desc": "..."}}
      ]
    }},
    {{ "name": "2nd destination", "country": "...", "budget": 0, "reason": "...", "best_season": "...", "language": "...", "currency": "...", "attractions": [] }},
    {{ "name": "3rd destination", "country": "...", "budget": 0, "reason": "...", "best_season": "...", "language": "...", "currency": "...", "attractions": [] }}
  ],
  "top_destination": "...",
  "itinerary": [
    {{"day": 1, "activities": [{{"time":"Morning","activity":"..."}},{{"time":"Afternoon","activity":"..."}},{{"time":"Evening","activity":"..."}}]}},
    {{"day": 2, "activities": [{{"time":"Morning","activity":"..."}},{{"time":"Afternoon","activity":"..."}},{{"time":"Evening","activity":"..."}}]}},
    {{"day": 3, "activities": [{{"time":"Morning","activity":"..."}},{{"time":"Afternoon","activity":"..."}},{{"time":"Evening","activity":"..."}}]}},
    {{"day": 4, "activities": [{{"time":"Morning","activity":"..."}},{{"time":"Afternoon","activity":"..."}},{{"time":"Evening","activity":"..."}}]}}
  ],
  "ai_tip": "One smart budget tip."
}}"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "TripWise AI",
    }
    body = {
        "model": "openrouter/auto",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(OPENROUTER_URL, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()

    raw = data["choices"][0]["message"]["content"]
    clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    return json.loads(clean)

async def geocode_place(place: str) -> dict | None:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place, "format": "json", "limit": 1}
    headers = {"User-Agent": "TripWiseAI/1.0"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params, headers=headers)
        results = r.json()
    if results:
        return {"lat": float(results[0]["lat"]), "lon": float(results[0]["lon"]), "display_name": results[0]["display_name"]}
    return None

async def fetch_attraction_image(attraction: str, destination: str) -> str:
    fallback = "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80"
    if not UNSPLASH_KEY:
        return fallback
    query = f"{attraction} {destination} landmark"
    url = "https://api.unsplash.com/search/photos"
    params = {"query": query, "per_page": 1, "orientation": "landscape", "client_id": UNSPLASH_KEY}
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(url, params=params)
            d = r.json()
        return d["results"][0]["urls"]["regular"] if d.get("results") else fallback
    except Exception:
        return fallback
