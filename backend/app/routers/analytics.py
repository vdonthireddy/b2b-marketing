from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.journey import Journey
from app.models.stage import Stage, StageGoal, StageTouchpoint, StageContent
from app.models.persona import Persona, JourneyPersona
from app.models.audit_log import AuditLog
from app.models.user import User
from app.middleware.auth import get_current_user
from app.middleware.rbac import require_viewer
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics for the current team."""
    team_id = current_user.team_id

    # Journey count
    journey_count = (await db.execute(
        select(func.count(Journey.id)).where(Journey.team_id == team_id)
    )).scalar() or 0

    # Persona count
    persona_count = (await db.execute(
        select(func.count(Persona.id)).where(Persona.team_id == team_id)
    )).scalar() or 0

    # Team member count
    member_count = (await db.execute(
        select(func.count(User.id)).where(User.team_id == team_id)
    )).scalar() or 0

    # Total stages across all journeys
    stage_count = (await db.execute(
        select(func.count(Stage.id)).join(Journey).where(Journey.team_id == team_id)
    )).scalar() or 0

    # Recent activity (last 7 days)
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_activity = (await db.execute(
        select(func.count(AuditLog.id)).where(
            AuditLog.team_id == team_id,
            AuditLog.created_at >= week_ago,
        )
    )).scalar() or 0

    return {
        "journey_count": journey_count,
        "persona_count": persona_count,
        "member_count": member_count,
        "stage_count": stage_count,
        "recent_activity_count": recent_activity,
    }


@router.get("/journey-completion")
async def get_journey_completion(
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    """Get completion metrics for all journeys."""
    team_id = current_user.team_id

    result = await db.execute(
        select(Journey).where(Journey.team_id == team_id)
    )
    journeys = result.scalars().all()

    metrics = []
    for j in journeys:
        total_stages = len(j.stages)
        stages_with_goals = sum(1 for s in j.stages if s.goals)
        stages_with_touchpoints = sum(1 for s in j.stages if s.touchpoints)
        stages_with_content = sum(1 for s in j.stages if s.content)

        completeness = 0
        if total_stages > 0:
            filled = stages_with_goals + stages_with_touchpoints + stages_with_content
            possible = total_stages * 3
            completeness = round((filled / possible) * 100)

        metrics.append({
            "journey_id": j.id,
            "journey_name": j.name,
            "total_stages": total_stages,
            "stages_with_goals": stages_with_goals,
            "stages_with_touchpoints": stages_with_touchpoints,
            "stages_with_content": stages_with_content,
            "completeness_pct": completeness,
            "has_personas": len(j.personas) > 0,
        })

    return {"journeys": metrics}


@router.get("/activity")
async def get_activity_feed(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    """Get recent activity feed for the team."""
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.team_id == current_user.team_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()

    # Fetch user names
    user_ids = list(set(log.user_id for log in logs))
    users_result = await db.execute(select(User).where(User.id.in_(user_ids)))
    user_map = {u.id: u.name for u in users_result.scalars().all()}

    return {
        "activities": [
            {
                "id": log.id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": log.details,
                "user_name": user_map.get(log.user_id, "Unknown"),
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]
    }
