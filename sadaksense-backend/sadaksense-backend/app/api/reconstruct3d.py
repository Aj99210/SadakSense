import uuid
from fastapi import APIRouter, BackgroundTasks, File, UploadFile

router = APIRouter(prefix="/v1", tags=["3d"])
JOBS = {}   # replaced by a Redis-backed job store in deployment


def _run(job_id: str, path: str):
    """GPU worker: depth -> back-projection -> ground plane. Mesh/splat export follows."""
    from app.ml.depth import DepthEstimator, backproject, fit_plane_ransac
    JOBS[job_id]["status"] = "depth"
    depth = DepthEstimator().depth_m(path, focal_px=1000.0)
    pts = backproject(depth, 1000.0)
    plane = fit_plane_ransac(pts[:: max(1, len(pts) // 20000)])
    JOBS[job_id].update(status="done", glb_url=f"/v1/scenes/{job_id}.glb", plane_normal=[float(v) for v in plane[0]])


@router.post("/reconstruct3d")
async def reconstruct(bg: BackgroundTasks, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    path = f"/tmp/{job_id}.jpg"
    with open(path, "wb") as f:
        f.write(await file.read())
    JOBS[job_id] = {"status": "queued"}
    bg.add_task(_run, job_id, path)
    return {"job_id": job_id}


@router.get("/jobs/{job_id}")
async def job(job_id: str):
    return JOBS.get(job_id, {"status": "unknown"})
