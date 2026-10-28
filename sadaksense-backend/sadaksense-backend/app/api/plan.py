from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.ml.forecast import SegmentCovariates, failure_risk, project_rqi
from app.schemas import PlanRequest, PlanResponse, RepairItem
from app.services.planner import Candidate, solve

router = APIRouter(prefix="/v1", tags=["plan"])


@router.post("/plan", response_model=PlanResponse)
async def plan(req: PlanRequest, db: AsyncSession = Depends(get_session)):
    rows = (await db.execute(text(
        "SELECT s.id, s.length_km, st.rqi FROM segments s JOIN segment_state st ON st.segment_id=s.id "
        "WHERE st.rqi IS NOT NULL"))).all()
    cands = []
    for sid, length, rqi in rows:
        p, lo, _ = project_rqi(SegmentCovariates(rqi, 8, 20000, .15, .5, .12, 400), req.horizon_days)
        cands.append(Candidate(sid, length or 1.0, failure_risk(p, lo), structural=rqi < 3.5))
    chosen = solve(cands, req.budget_inr, req.max_roads)
    items = [RepairItem(segment_id=i, treatment=t, cost_inr=c, risk_removed=round(r, 3),
                        reason="Structural damage: resurfacing lasts longest." if t == "resurface" else "Best value for budget.")
             for i, t, c, r in chosen]
    return PlanResponse(items=items, spent_inr=sum(i.cost_inr for i in items), budget_inr=req.budget_inr)


@router.get("/segments/{segment_id}/explain")
async def explain(segment_id: int, db: AsyncSession = Depends(get_session)):
    rows = (await db.execute(text(
        "SELECT cls, confidence, area_px, frame_url FROM detections WHERE segment_id=:i ORDER BY captured_at DESC LIMIT 20"),
        {"i": segment_id})).mappings().all()
    return {"segment_id": segment_id, "findings": [dict(r) for r in rows]}
