from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.ml.forecast import SegmentCovariates, failure_risk, project_rqi
from app.schemas import ForecastRequest

router = APIRouter(prefix="/v1", tags=["forecast"])


@router.post("/forecast")
async def forecast(req: ForecastRequest, db: AsyncSession = Depends(get_session)):
    rows = (await db.execute(text(
        "SELECT s.id, st.rqi FROM segments s JOIN segment_state st ON st.segment_id = s.id WHERE st.rqi IS NOT NULL"))).all()
    out = []
    for sid, rqi in rows:
        if sid == req.closed_segment_id:
            continue
        cov = SegmentCovariates(rqi=rqi, age_years=8, aadt=20000, heavy_share=0.15, drainage=0.5,
                                rainfall=req.rainfall, days_since_repair=400)
        p, lo, hi = project_rqi(cov, req.horizon_days, req.load_multiplier)
        out.append({"segment_id": sid, "rqi": p, "lower": lo, "upper": hi, "risk": failure_risk(p, lo)})
    return out
