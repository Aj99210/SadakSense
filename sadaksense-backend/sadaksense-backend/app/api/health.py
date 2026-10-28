from fastapi import APIRouter
from app.ml import detector

router = APIRouter(prefix="/v1", tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok", "detector_ready": detector.is_ready(),
            "models": {"detector": "SadakVision (YOLO26)", "depth": "Depth Anything 3",
                       "segmenter": "SAM 3", "rqi": "LightGBM + formula baseline"}}
