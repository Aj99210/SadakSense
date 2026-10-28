from geoalchemy2 import Geometry
from sqlalchemy import BigInteger, Float, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SegmentRow(Base):
    __tablename__ = "segments"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    district: Mapped[str] = mapped_column(String)
    road_type: Mapped[str] = mapped_column(String)
    length_km: Mapped[float] = mapped_column(Float)
    h3_index: Mapped[str] = mapped_column(String, index=True)
    geom = mapped_column(Geometry("LINESTRING", srid=4326))


class DetectionRow(Base):
    __tablename__ = "detections"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id"))
    cls: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float)
    area_px: Mapped[float] = mapped_column(Float)
    captured_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    geom = mapped_column(Geometry("POINT", srid=4326))


class SegmentState(Base):
    __tablename__ = "segment_state"
    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id"), primary_key=True)
    rqi: Mapped[float | None] = mapped_column(Float)
    speed_kmh: Mapped[float | None] = mapped_column(Float)
    potholes: Mapped[int | None] = mapped_column(Integer)
