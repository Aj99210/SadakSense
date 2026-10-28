"""SadakVision: YOLO26 damage detector with SAHI sliced inference for thin cracks."""
import os
from functools import lru_cache

from app.config import settings
from app.schemas import Detection, DamageClass

NAMES = {0: DamageClass.longitudinal, 1: DamageClass.transverse, 2: DamageClass.alligator, 3: DamageClass.pothole}


@lru_cache(maxsize=1)
def _model():
    from sahi import AutoDetectionModel
    return AutoDetectionModel.from_pretrained(
        model_type="ultralytics", model_path=settings.detector_weights,
        confidence_threshold=settings.conf_threshold, device=settings.device)


def detect(image_bgr):
    from sahi.predict import get_sliced_prediction
    result = get_sliced_prediction(
        image_bgr, _model(),
        slice_height=settings.slice_size, slice_width=settings.slice_size,
        overlap_height_ratio=0.2, overlap_width_ratio=0.2,
        postprocess_type="NMM")          # merge duplicates across tile borders
    out = []
    for p in result.object_prediction_list:
        x1, y1, x2, y2 = p.bbox.to_xyxy()
        out.append(Detection(cls=NAMES[p.category.id], confidence=float(p.score.value),
                             bbox=(x1, y1, x2, y2), area_px=float((x2 - x1) * (y2 - y1))))
    return out


def is_ready() -> bool:
    return os.path.exists(settings.detector_weights)
