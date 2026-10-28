import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rqi import segment_state
from app.db.session import get_session

router = APIRouter(prefix="/v1", tags=["segments"])

_Q = text("""
SELECT s.id, s.name, s.district, st.rqi, st.speed_kmh, st.potholes, st.last_scan,
       ST_AsGeoJSON(s.geom)::json AS geometry
FROM segments s LEFT JOIN segment_state st ON st.segment_id = s.id
WHERE (CAST(:district AS text) IS NULL OR s.district = :district)
  AND (CAST(:use_bbox AS boolean) = false OR s.geom && ST_MakeEnvelope(:w, :s, :e, :n, 4326))
LIMIT :limit
""")


@router.get("/segments")
async def list_segments(district: Optional[str] = None, bbox: Optional[str] = Query(None, description="w,s,e,n"),
                        limit: int = 5000, db: AsyncSession = Depends(get_session)):
    w = s = e = n = 0.0
    if bbox:
        w, s, e, n = map(float, bbox.split(","))
    rows = (await db.execute(_Q, dict(district=district, use_bbox=bool(bbox), w=w, s=s, e=e, n=n, limit=limit))).mappings().all()
    return [{**r, "state": segment_state(r["rqi"])} for r in rows]


@router.get("/segments/{segment_id}")
async def get_segment(segment_id: int, db: AsyncSession = Depends(get_session)):
    r = (await db.execute(text("SELECT * FROM segment_state WHERE segment_id=:i"), {"i": segment_id})).mappings().first()
    return {**(r or {}), "state": segment_state(r["rqi"] if r else None)}


@router.get("/segments/{segment_id}/trend")
async def trend(segment_id: int, days: int = 7, db: AsyncSession = Depends(get_session)):
    rows = (await db.execute(text(
        "SELECT date_trunc('day', captured_at) d, avg(confidence) c, count(*) n FROM detections "
        "WHERE segment_id=:i AND captured_at > now() - make_interval(days => :d) GROUP BY 1 ORDER BY 1"),
        {"i": segment_id, "d": days})).mappings().all()
    return {"segment_id": segment_id, "points": [dict(r) for r in rows]}


@router.get("/alerts/stream")
async def alerts_stream():
    import redis.asyncio as aioredis
    from app.config import settings

    async def gen():
        r = aioredis.from_url(settings.redis_url)
        pubsub = r.pubsub()
        await pubsub.subscribe("alerts")
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=15)
            yield f"data: {msg['data'].decode()}\n\n" if msg else ": keepalive\n\n"
            await asyncio.sleep(0)

    return StreamingResponse(gen(), media_type="text/event-stream")
