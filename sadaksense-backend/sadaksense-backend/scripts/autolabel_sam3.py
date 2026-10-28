"""Data engine: SAM 3 proposes masks for human review in CVAT."""
import pathlib
from PIL import Image
from app.ml.segmenter import ConceptSegmenter

seg = ConceptSegmenter()
for p in pathlib.Path("data/unlabelled").glob("*.jpg"):
    m = seg.mask(Image.open(p), "pothole")
    print(p.name, int(m.sum()))
