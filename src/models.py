from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    profile_picture: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    favorite_planets: Mapped[list["FavoritePlanet"]] = relationship("FavoritePlanet", back_populates="user", cascade="all, delete-orphan")
    favorite_characters: Mapped[list["FavoriteCharacter"]] = relationship("FavoriteCharacter", back_populates="user", cascade="all, delete-orphan")


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "bio": self.bio,
            "profile_picture": self.profile_picture,
            "created_at": self.created_at.isoformat()
            # do not serialize the password, its a security breach
        }
    
class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    population: Mapped[int] = mapped_column(Integer, nullable=True)
    climate: Mapped[str] = mapped_column(String(100), nullable=True)
    terrain: Mapped[str] = mapped_column(String(100), nullable=True)
    diameter: Mapped[int] = mapped_column(Integer, nullable=True)
    orbital_period: Mapped[int] = mapped_column(Integer, nullable=True)
    rotation_period: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    favorite_users: Mapped[list["FavoritePlanet"]] = relationship("FavoritePlanet", back_populates="planet", cascade="all, delete-orphan")
    characters: Mapped[list["Character"]] = relationship("Character", back_populates="homeworld")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "climate": self.climate,
            "terrain": self.terrain,
            "diameter": self.diameter,
            "orbital_period": self.orbital_period,
            "rotation_period": self.rotation_period,
            "created_at": self.created_at.isoformat()
        }
    
class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=True)
    weight: Mapped[int] = mapped_column(Integer, nullable=True)
    hair_color: Mapped[str] = mapped_column(String(50), nullable=True)
    skin_color: Mapped[str] = mapped_column(String(50), nullable=True)
    eye_color: Mapped[str] = mapped_column(String(50), nullable=True)
    birth_year: Mapped[str] = mapped_column(String(20), nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    homeworld_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    homeworld: Mapped["Planet"] = relationship("Planet", foreign_keys=[homeworld_id], back_populates="characters")
    favorite_users: Mapped[list["FavoriteCharacter"]] = relationship("FavoriteCharacter", back_populates="character", cascade="all, delete-orphan")

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "weight": self.weight,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "homeworld_id": self.homeworld_id,
            "homeworld": self.homeworld.serialize() if self.homeworld else None,
            "created_at": self.created_at.isoformat()
        }
    
class FavoritePlanet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped["User"] = relationship("User", back_populates="favorite_planets")
    planet: Mapped["Planet"] = relationship("Planet", back_populates="favorite_users")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "created_at": self.created_at.isoformat(),
            "user": self.user.serialize() if self.user else None,
            "planet": self.planet.serialize() if self.planet else None
        }
    
class FavoriteCharacter(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped["User"] = relationship("User", back_populates="favorite_characters")
    character: Mapped["Character"] = relationship("Character", back_populates="favorite_users")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "created_at": self.created_at.isoformat(),
            "user": self.user.serialize() if self.user else None,
            "character": self.character.serialize() if self.character else None
        }