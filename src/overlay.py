import cv2
import math


def draw_overlay(frame, bbox, shape, width_cm, height_cm, label, accepted):
    color = (0, 255, 0) if accepted else (0, 0, 255)
    x, y, w, h = bbox

    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    if shape == "Circle":
        area = math.pi * (width_cm / 2) ** 2
    else:
        area = width_cm * height_cm

    text_x = x
    text_y = max(y - 10, 120)

    status = "ACCEPTED" if accepted else "REJECTED"

    texts = [
        f"Shape : {shape}",
        f"W     : {width_cm:.2f} cm",
        f"H     : {height_cm:.2f} cm",
        f"Area  : {area:.2f} cm2",
        f"Object: {label}",
        f"Status: {status}",
    ]

    for i, text in enumerate(texts):
        cv2.putText(
            frame, text,
            (text_x, text_y + i * 22),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2
        )


def draw_info(frame, camera_type, yolo_label):
    cv2.putText(
        frame, f"Camera: {camera_type}  |  Press Q to quit",
        (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
    )
    cv2.putText(
        frame, f"Object: {yolo_label}",
        (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2
    )


def draw_warning(frame, message):
    cv2.putText(
        frame, message,
        (10, frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2
    )
