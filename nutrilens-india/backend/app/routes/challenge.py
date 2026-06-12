import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.config import settings
from app.models.client import Client
from app.models.meal_log import MealLog, MealType
from app.services.compliance_engine import calculate_compliance
from app.services.food_pattern_engine import classify_meal

router = APIRouter(prefix="/challenge", tags=["Challenge"])

VALID_MEAL_TYPES = {m.value for m in MealType}
REQUIRED_TYPES = {"BREAKFAST", "LUNCH", "DINNER"}


async def _save_image(file: UploadFile) -> str:
    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "meal.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(settings.upload_dir, filename)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    return f"/uploads/{filename}"


@router.post("/submit-meal")
async def submit_meal(
    client_id: str = Form(...),
    day_number: int = Form(...),
    meal_type: str = Form(...),
    meal_text: str = Form(...),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Submit a meal for the challenge. Both image and text are mandatory."""
    meal_type_upper = meal_type.upper()
    if meal_type_upper not in VALID_MEAL_TYPES:
        raise HTTPException(400, f"meal_type must be one of {sorted(VALID_MEAL_TYPES)}")
    if not 1 <= day_number <= 7:
        raise HTTPException(400, "day_number must be between 1 and 7")
    if not meal_text.strip():
        raise HTTPException(400, "meal_text is required")
    if not image or not image.filename:
        raise HTTPException(400, "A meal image is required")

    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    if not client.audit_completed:
        raise HTTPException(403, "Complete the Lifestyle Audit before submitting meals")

    image_url = await _save_image(image)
    pattern_tags = list(classify_meal(meal_text.strip()).keys())
    pattern_tags = [k for k, v in classify_meal(meal_text.strip()).items() if v]

    # Upsert: resubmitting same day+type overwrites
    result = await db.execute(
        select(MealLog).where(
            and_(
                MealLog.client_id == client_id,
                MealLog.day_number == day_number,
                MealLog.meal_type == meal_type_upper,
                MealLog.challenge_cycle == client.challenge_cycle,
            )
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.meal_text = meal_text.strip()
        existing.image_url = image_url
        existing.food_pattern_tags = pattern_tags
        await db.commit()
        return {
            "log_id": existing.id,
            "updated": True,
            "day": day_number,
            "meal_type": meal_type_upper,
            "image_url": image_url,
            "food_pattern_tags": pattern_tags,
        }

    log = MealLog(
        client_id=client_id,
        day_number=day_number,
        meal_type=meal_type_upper,
        meal_text=meal_text.strip(),
        image_url=image_url,
        food_pattern_tags=pattern_tags,
        challenge_cycle=client.challenge_cycle,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return {
        "log_id": log.id,
        "updated": False,
        "day": day_number,
        "meal_type": meal_type_upper,
        "image_url": image_url,
        "food_pattern_tags": pattern_tags,
    }


@router.get("/progress/{client_id}")
async def get_progress(client_id: str, db: AsyncSession = Depends(get_db)):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    result = await db.execute(
        select(MealLog).where(
            and_(
                MealLog.client_id == client_id,
                MealLog.challenge_cycle == client.challenge_cycle,
            )
        )
    )
    logs = result.scalars().all()
    compliance = calculate_compliance(logs)

    return {
        "client_id": client_id,
        "client_name": client.name,
        "client_status": client.status,
        "challenge_cycle": client.challenge_cycle,
        "audit_completed": client.audit_completed,
        **compliance,
    }


@router.get("/day/{client_id}/{day}")
async def get_day_meals(client_id: str, day: int, db: AsyncSession = Depends(get_db)):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    result = await db.execute(
        select(MealLog).where(
            and_(
                MealLog.client_id == client_id,
                MealLog.day_number == day,
                MealLog.challenge_cycle == client.challenge_cycle,
            )
        )
    )
    logs = result.scalars().all()
    submitted_types = {log.meal_type for log in logs}
    required_types = {"BREAKFAST", "LUNCH", "DINNER"}

    return {
        "day": day,
        "challenge_cycle": client.challenge_cycle,
        "is_complete": required_types.issubset(submitted_types),
        "meals": [
            {
                "meal_type": log.meal_type,
                "meal_text": log.meal_text,
                "image_url": log.image_url,
                "food_pattern_tags": log.food_pattern_tags or [],
                "submitted_at": log.submitted_at,
            }
            for log in sorted(logs, key=lambda x: x.meal_type)
        ],
    }
