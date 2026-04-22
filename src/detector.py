from ultralytics import YOLO


def load_model():
    print("🤖 Loading YOLOv8...")
    model = YOLO("yolov8n.pt")
    print("✅ YOLOv8 ready!")
    return model


def detect_object(model, frame):
    results = model(frame, verbose=False)
    if results and results[0].boxes:
        cls_id = int(results[0].boxes.cls[0])
        return model.names[cls_id]
    return "Unknown"
