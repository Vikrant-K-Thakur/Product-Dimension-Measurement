from ultralytics import YOLO


def load_model():
    print(" Loading YOLOv8...")
    model = YOLO("yolov8s.pt") 
    print(" YOLOv8 ready!")
    return model


def detect_object(model, frame):
    results = model(frame, verbose=False)
    if results and results[0].boxes:
        box = results[0].boxes[0]
        if float(box.conf[0]) < 0.4: 
            return "Unknown", None
        cls_id = int(box.cls[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = model.names[cls_id]
        return label, (x1, y1, x2 - x1, y2 - y1)
    return "Unknown", None
