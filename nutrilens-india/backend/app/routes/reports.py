from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models.client import Client, ClientStatus
from app.models.meal_log import MealLog
from app.models.report import ChallengeReport
from app.services.compliance_engine import calculate_compliance
from app.services.food_pattern_engine import aggregate_patterns
from app.services.report_engine import build_report
from app.services.eligibility_engine import calculate_eligibility, BAND_LABELS

router = APIRouter(prefix="/reports", tags=["Reports"])

PASS_THRESHOLD = 85.0


@router.post("/generate/{client_id}")
async def generate_report(client_id: str, db: AsyncSession = Depends(get_db)):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")

    if not client.audit_completed:
        raise HTTPException(403, "Lifestyle Audit must be completed before generating a report")

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
    compliance_pct = compliance["compliance_pct"]
    completed_days = compliance["completed_days"]

    # Determine qualification status
    if compliance_pct >= PASS_THRESHOLD:
        qualification_status = "QUALIFIED"
    elif client.challenge_cycle == 1:
        qualification_status = "SECOND_CHANCE"
    else:
        qualification_status = "LOCKED"

    pattern_data = aggregate_patterns(logs)
    food_pattern_pct = pattern_data.get("percentages", {})

    # Eligibility score (kept for admin reference, not shown to user)
    eligibility = calculate_eligibility(
        compliance_pct=compliance_pct,
        protein_pct=food_pattern_pct.get("PROTEIN_PRESENT", 0),
        avg_daily_fiber=0,
        avg_daily_calories=0,
        submitted_days=completed_days,
        submitted_meals=compliance["submitted_meals"],
    )

    report_data = build_report(
        client_name=client.name,
        compliance_pct=compliance_pct,
        completed_days=completed_days,
        food_pattern_pct=food_pattern_pct,
        qualification_status=qualification_status,
        eligibility_score=eligibility["eligibility_score"],
        eligibility_band=eligibility["eligibility_band"],
    )

    # Upsert report
    cr = await db.get(ChallengeReport, client_id)
    if not cr:
        cr = ChallengeReport(client_id=client_id)
        db.add(cr)
    cr.compliance_score = compliance_pct
    cr.completed_days = completed_days
    cr.qualification_status = qualification_status
    cr.eligibility_score = eligibility["eligibility_score"]
    cr.eligibility_band = eligibility["eligibility_band"]
    cr.food_observations = report_data["food_observations"]
    cr.strengths = report_data["strengths"]
    cr.improvement_areas = report_data["improvement_areas"]
    cr.action_plan = report_data["action_plan"]
    cr.wholesome_plate_tips = report_data["wholesome_plate_tips"]
    cr.food_pattern_summary = food_pattern_pct

    # Update client status
    if qualification_status == "QUALIFIED":
        client.status = ClientStatus.QUALIFIED
    elif qualification_status == "SECOND_CHANCE" and client.challenge_cycle == 1:
        client.status = ClientStatus.SECOND_CHANCE
        client.challenge_cycle = 2
    elif qualification_status == "LOCKED":
        client.status = ClientStatus.LOCKED

    await db.commit()

    return {
        **report_data,
        "band_label": BAND_LABELS.get(eligibility["eligibility_band"], ""),
        "food_pattern_data": pattern_data,
    }


@router.get("/{client_id}")
async def get_report(client_id: str, db: AsyncSession = Depends(get_db)):
    cr = await db.get(ChallengeReport, client_id)
    if not cr:
        raise HTTPException(404, "No report found. Complete 6+ days with all 3 meals, then generate your report.")

    client = await db.get(Client, client_id)

    return {
        "client_name": client.name if client else "Unknown",
        "compliance_score": cr.compliance_score,
        "completed_days": cr.completed_days,
        "qualification_status": cr.qualification_status,
        "eligibility_band": cr.eligibility_band,
        "band_label": BAND_LABELS.get(cr.eligibility_band or "", ""),
        "food_observations": cr.food_observations or [],
        "strengths": cr.strengths or [],
        "improvement_areas": cr.improvement_areas or [],
        "action_plan": cr.action_plan or [],
        "wholesome_plate_tips": cr.wholesome_plate_tips or [],
        "food_pattern_summary": cr.food_pattern_summary or {},
        "generated_at": cr.generated_at,
    }
