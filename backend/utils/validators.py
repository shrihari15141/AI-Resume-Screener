from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class RegisterPayload(BaseModel):
    username: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginPayload(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class JobPayload(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=10)
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    education: list[str] = []
    experience: str | int | float | None = None
    certifications: list[str] = []
    location: str = ""
    employment_type: str = ""

