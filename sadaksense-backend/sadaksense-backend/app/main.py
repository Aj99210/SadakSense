from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analyze, complaints, forecast, health, plan, reconstruct3d, segments

app = FastAPI(title="SadakSense API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

for r in (health, analyze, complaints, segments, reconstruct3d, forecast, plan):
    app.include_router(r.router)
