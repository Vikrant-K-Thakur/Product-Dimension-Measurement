import cv2
import math


def detect_shape(contour):
    perimeter = cv2.arcLength(contour, True)
    if perimeter == 0:
        return "Unknown"

    area = cv2.contourArea(contour)
    circularity = 4 * math.pi * area / (perimeter * perimeter)

    if circularity > 0.85:
        return "Circle"

    approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
    sides = len(approx)

    if sides == 4:
        x, y, w, h = cv2.boundingRect(approx)
        ratio = w / float(h)
        return "Square" if 0.9 <= ratio <= 1.1 else "Rectangle"

    return "Unknown"


def get_measurements(contour, shape):
    if shape == "Circle":
        (_, _), radius = cv2.minEnclosingCircle(contour)
        diameter_px = radius * 2
        return diameter_px, diameter_px, radius
    else:
        rect = cv2.minAreaRect(contour)
        (_, _), (w, h), _ = rect
        return max(w, h), min(w, h), None


def preprocess_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    _, binary = cv2.threshold(
        blurred, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return binary


def get_valid_contours(binary, min_area=1000):
    contours, _ = cv2.findContours(
        binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    return [c for c in contours if cv2.contourArea(c) > min_area]
