import cv2
from dotenv import dotenv_values

from config.standards import PRODUCT_STANDARDS
from src.camera import get_camera
from src.processor import preprocess_frame, get_valid_contours
from src.overlay import draw_overlay, draw_info, draw_warning
from src.detector import load_model, detect_object

env = dotenv_values(".env")

# ─────────────────────────────────────────────
# CALIBRATION CONSTANT
# IMPORTANT: Calibrate this value before running
# pixels_per_cm = pixels_of_reference / actual_cm
PIXELS_PER_CM = 40.0  # ← Calibrated: 600px = 15cm

if PIXELS_PER_CM <= 0:
    raise ValueError("Invalid calibration value: PIXELS_PER_CM must be > 0")
# ─────────────────────────────────────────────


def run_live():
    cap, camera_type = get_camera()
    model = load_model()

    print(f"\n🎥 Live feed started ({camera_type})")
    print("• Press 'Q' to quit\n")

    frame_count = 0
    yolo_label = "Unknown"
    yolo_bbox = None
    prev_width = 0
    prev_height = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Camera disconnected")
            break

        if camera_type == "DroidCam":
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        display = frame.copy()
        frame_count += 1

        # ─── YOLO every 10 frames ─────────────────────────
        if frame_count % 10 == 0:
            yolo_label, yolo_bbox = detect_object(model, frame)

        # ─── Draw camera info and YOLO label ──────────────
        draw_info(display, camera_type, yolo_label)

        # ─── Use YOLO bbox for measurement and overlay ────
        if yolo_bbox:
            x, y, w, h = yolo_bbox
            width_cm = w / PIXELS_PER_CM
            height_cm = h / PIXELS_PER_CM

            # Smooth measurements
            width_cm = 0.7 * prev_width + 0.3 * width_cm
            height_cm = 0.7 * prev_height + 0.3 * height_cm
            prev_width = width_cm
            prev_height = height_cm

            shape = "Rectangle" if abs(w - h) > 10 else "Square"

            std = PRODUCT_STANDARDS.get(yolo_label.lower())
            if std:
                tol = std["tolerance"]
                accepted = (
                    abs(width_cm - std["width"]) <= tol
                    and abs(height_cm - std["height"]) <= tol
                )
            else:
                accepted = False  # unknown object = rejected

            draw_overlay(display, yolo_bbox, shape, width_cm, height_cm, yolo_label, accepted)
        else:
            draw_warning(display, "No object detected")

        cv2.imshow("Live Measurement System", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("⏹️ Stopped by user")
            break
        elif key == ord('s'):
            cv2.imwrite("calibration.png", display)
            print("📸 Saved calibration.png")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_live()
