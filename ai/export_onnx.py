"""Exporta yolov8n.pt a ONNX para inferencia CPU en cloud (doc §3)."""

from ultralytics import YOLO

from config import MODEL_NAME

if __name__ == "__main__":
    model = YOLO(MODEL_NAME)
    out = model.export(format="onnx", simplify=True)
    print(f"Exportado: {out}")
