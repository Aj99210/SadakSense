"""SadakDepth: Depth Anything 3 metric depth + RANSAC ground plane -> pothole depth/volume."""
import numpy as np


class DepthEstimator:
    def __init__(self, model_id: str = "depth-anything/DA3METRIC-LARGE", device: str = "cuda"):
        from depth_anything_3.api import DepthAnything3
        self.model = DepthAnything3.from_pretrained(model_id).to(device)

    def depth_m(self, image_path: str, focal_px: float) -> np.ndarray:
        pred = self.model.inference([image_path])
        return focal_px * pred.depth[0] / 300.0     # metric conversion for the DA3 metric checkpoint


def backproject(depth: np.ndarray, focal_px: float) -> np.ndarray:
    h, w = depth.shape
    ys, xs = np.mgrid[0:h, 0:w]
    x = (xs - w / 2) * depth / focal_px
    y = (ys - h / 2) * depth / focal_px
    return np.stack([x, y, depth], axis=-1).reshape(-1, 3)


def fit_plane_ransac(points: np.ndarray, iters: int = 300, tol: float = 0.02, seed: int = 0):
    rng = np.random.default_rng(seed)
    best, best_inl = None, 0
    for _ in range(iters):
        s = points[rng.choice(len(points), 3, replace=False)]
        n = np.cross(s[1] - s[0], s[2] - s[0])
        if np.linalg.norm(n) < 1e-9:
            continue
        n = n / np.linalg.norm(n)
        d = -n @ s[0]
        inl = int((np.abs(points @ n + d) < tol).sum())
        if inl > best_inl:
            best, best_inl = (n, d), inl
    return best


def pothole_depth_and_volume(points_in_mask: np.ndarray, plane, pixel_area_m2: float):
    """Depth = 95th percentile distance from the road plane; volume = sum(depth * pixel footprint)."""
    n, d = plane
    dist = np.abs(points_in_mask @ n + d)
    return float(np.percentile(dist, 95)), float(dist.sum() * pixel_area_m2)
