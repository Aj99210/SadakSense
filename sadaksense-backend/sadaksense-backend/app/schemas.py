from enum import Enum
from pydantic import BaseModel, Field


class DamageClass(str, Enum):
    longitudinal = "D00"   # longitudinal crack
    transverse = "D10"     # transverse crack
    alligator = "D20"      # alligator crack
    pothole = "D40"        # pothole


class Detection(BaseModel):
    cls: DamageClass
    confidence: float = Field(ge=0, le=1)
    bbox: tuple[float, float, float, float]  # x1, y1, x2, y2 in pixels
    area_px: float
    track_id: int | None = None
    depth_m: float | None = None             # pothole depth from SadakDepth, if available


class AnalyzeResult(BaseModel):
    rqi: float = Field(ge=0, le=10)
    condition: str
    est_speed_kmh: float
    congestion: str
    damage_counts: dict[str, int]
    surface_composition: dict[str, float]   # intact / minor_wear / cracking / damaged (shares)
    drivers: list[dict]                     # SHAP-style contributions
    evidence_url: str | None = None
    lat: float | None = None
    lng: float | None = None


class ComplaintRequest(BaseModel):
    result: AnalyzeResult
    address: str
    city: str
    state: str
    pin_code: str
    road_type: str = "Municipal Road"
    damage_since: str = "1-3 months"
    complainant_name: str
    contact: str | None = None
    email: str | None = None


class ComplaintResponse(BaseModel):
    reference: str
    recipient: str
    portal_url: str
    letter: str


class ForecastRequest(BaseModel):
    horizon_days: int = 30
    rainfall: float = Field(0.12, ge=0, le=1)
    load_multiplier: float = Field(1.0, ge=0.5, le=3.0)
    closed_segment_id: int | None = None


class PlanRequest(BaseModel):
    budget_inr: float
    horizon_days: int = 30
    max_roads: int = 32


class RepairItem(BaseModel):
    segment_id: int
    treatment: str
    cost_inr: float
    risk_removed: float
    reason: str


class PlanResponse(BaseModel):
    items: list[RepairItem]
    spent_inr: float
    budget_inr: float
