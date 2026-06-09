from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(120), nullable=False)
    email         = Column(String(200), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)
    trips         = relationship("Trip", back_populates="user", cascade="all, delete")

class Trip(Base):
    __tablename__ = "trips"
    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=True)
    source_city     = Column(String(120))
    destination     = Column(String(200))
    budget          = Column(Float)
    travelers       = Column(Integer, default=1)
    days            = Column(Integer, default=4)
    travel_style    = Column(String(80))
    top_destination = Column(String(200))
    ai_result       = Column(JSON)           # full AI JSON stored
    created_at      = Column(DateTime, default=datetime.utcnow)
    user            = relationship("User", back_populates="trips")
    hotels          = relationship("Hotel", back_populates="trip", cascade="all, delete")
    flights         = relationship("Flight", back_populates="trip", cascade="all, delete")
    itineraries     = relationship("SavedItinerary", back_populates="trip", cascade="all, delete")

class Hotel(Base):
    __tablename__ = "hotels"
    id         = Column(Integer, primary_key=True, index=True)
    trip_id    = Column(Integer, ForeignKey("trips.id"))
    hotel_name = Column(String(200))
    price      = Column(Float)
    rating     = Column(Float)
    trip       = relationship("Trip", back_populates="hotels")

class Flight(Base):
    __tablename__ = "flights"
    id         = Column(Integer, primary_key=True, index=True)
    trip_id    = Column(Integer, ForeignKey("trips.id"))
    airline    = Column(String(120))
    price      = Column(Float)
    duration   = Column(String(40))
    trip       = relationship("Trip", back_populates="flights")

class SavedItinerary(Base):
    __tablename__ = "saved_itineraries"
    id         = Column(Integer, primary_key=True, index=True)
    trip_id    = Column(Integer, ForeignKey("trips.id"))
    content    = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    trip       = relationship("Trip", back_populates="itineraries")
