"""Fine-tune YOLO26 on RDD2022 (+ local data). Classes: D00, D10, D20, D40."""
from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO("yolo26s.pt")
    model.train(data="data/rdd2022.yaml", epochs=120, imgsz=960, batch=16, device=0,
                project="runs", name="sadakvision", cos_lr=True, close_mosaic=15)
    model.export(format="onnx", dynamic=True)
