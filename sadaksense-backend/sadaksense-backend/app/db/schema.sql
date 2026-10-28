CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE segments (
  id BIGSERIAL PRIMARY KEY,
  osm_way_id BIGINT,
  name TEXT, district TEXT, road_type TEXT,
  length_km DOUBLE PRECISION,
  h3_index TEXT,
  geom geometry(LineString, 4326) NOT NULL
);
CREATE INDEX segments_geom_gix ON segments USING GIST (geom);
CREATE INDEX segments_h3_ix ON segments (h3_index);

CREATE TABLE detections (
  id BIGSERIAL PRIMARY KEY,
  segment_id BIGINT REFERENCES segments(id),
  cls TEXT NOT NULL, confidence REAL, area_px REAL, depth_m REAL,
  track_id BIGINT, frame_url TEXT,
  captured_at TIMESTAMPTZ DEFAULT now(),
  geom geometry(Point, 4326)
);
CREATE INDEX detections_seg_ix ON detections (segment_id, captured_at DESC);

CREATE TABLE segment_state (
  segment_id BIGINT PRIMARY KEY REFERENCES segments(id),
  rqi REAL, speed_kmh REAL, potholes INT, last_scan TIMESTAMPTZ
);
