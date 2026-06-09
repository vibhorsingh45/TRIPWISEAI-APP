from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from datetime import datetime

# ── Auth ──
class UserCreate(BaseModel):
    name:     str = Field(..., min_length=2, max_length=120)
    email:    EmailStr
    password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    id:    int
    name:  str
    email: str
    model_config = {"from_attributes": True}

class TokenOut(BaseModel):
    access_token:  str
    token_type:    str = "bearer"
    user:          UserOut

class LoginIn(BaseModel):
    email:    EmailStr
    password: str

# ── Trip planning ──
class TripRequest(BaseModel):
    source_city:  str  = Field(..., example="Lucknow")
    destination:  str  = Field(..., example="Beach or hills")
    budget:       float = Field(..., gt=0, example=30000)
    travelers:    int   = Field(default=2, ge=1, le=20)
    days:         int   = Field(default=4,  ge=1, le=30)
    travel_style: str   = Field(default="Budget Explorer")

class TripOut(BaseModel):
    id:              int
    destination:     str
    top_destination: Optional[str]
    budget:          float
    days:            int
    travelers:       int
    ai_result:       Optional[Any]
    created_at:      datetime
    model_config = {"from_attributes": True}

# ── Attractions ──
class AttractionQuery(BaseModel):
    destination: str = Field(..., example="Jaipur, Rajasthan")
    limit:       int = Field(default=6, ge=1, le=12)

# ── Geocode ──
class GeocodeQuery(BaseModel):
    place: str = Field(..., example="Hawa Mahal, Jaipur")
