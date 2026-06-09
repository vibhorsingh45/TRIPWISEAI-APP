# TripWise AI — Python FastAPI Backend

## Stack
- **FastAPI** + **Uvicorn** — async web framework
- **SQLAlchemy 2** + **PostgreSQL** (or SQLite for local dev)
- **Claude AI** (Anthropic) — trip planning & recommendations
- **Nominatim / OpenStreetMap** — free real-time geocoding
- **Unsplash API** — attraction images
- **JWT** — authentication

---

## Quick Start (local, SQLite)

```bash
cd tripwise-backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY and UNSPLASH_ACCESS_KEY

uvicorn main:app --reload
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## Quick Start (Docker + Postgres)

```bash
cp .env.example .env   # fill in API keys
docker-compose up --build
```

---

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login → JWT token |

### Trips
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/trips/plan` | **Main endpoint** — AI plan + live data |
| GET | `/api/trips/history` | User's past trips (auth required) |
| GET | `/api/trips/{id}` | Get saved trip by ID |
| DELETE | `/api/trips/{id}` | Delete trip (auth required) |

### Attractions
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/attractions/?destination=Jaipur` | Get attractions with images + coords |
| GET | `/api/attractions/image?name=Hawa Mahal&destination=Jaipur` | Single attraction image |

### Geocode
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/geocode/?place=Hawa Mahal, Jaipur` | Lat/lon for any place |
| GET | `/api/geocode/destination-map?destination=Manali` | Coords + OSM embed URL |

---

## Plan Trip — Request/Response

**POST /api/trips/plan**
```json
{
  "source_city": "Lucknow",
  "destination": "hills or beach",
  "budget": 30000,
  "travelers": 2,
  "days": 4,
  "travel_style": "Budget Explorer"
}
```

**Response includes:**
- `budget_breakdown` — transport / hotel / food / activities
- `destinations[3]` — each with `coords`, `heroImg`, `attractions[].img`, `attractions[].coords`
- `itinerary` — day-by-day activities
- `ai_tip` — budget optimization advice
- `trip_id` — saved DB record

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ | From console.anthropic.com |
| `UNSPLASH_ACCESS_KEY` | ✅ | From unsplash.com/developers |
| `SECRET_KEY` | ✅ | Random string for JWT signing |
| `DATABASE_URL` | Optional | Defaults to SQLite |

---

## Project Structure

```
tripwise-backend/
├── main.py                     # FastAPI app + router registration
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── app/
    ├── ai/
    │   └── ai_service.py       # Claude API + budget engine + geocoding + images
    ├── routes/
    │   ├── auth.py             # Register / Login
    │   ├── trips.py            # Plan / History / Get / Delete
    │   ├── attractions.py      # Attraction images + coords
    │   └── geocode.py          # Real-time location lookup
    ├── models/
    │   └── models.py           # SQLAlchemy ORM models
    ├── schemas/
    │   └── schemas.py          # Pydantic request/response schemas
    ├── database/
    │   └── db.py               # Engine + session + Base
    └── utils/
        └── auth_utils.py       # JWT encode/decode + password hashing
```
