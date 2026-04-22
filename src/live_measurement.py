import cv2
from dotenv import dotenv_values

from config.standards import STANDARD_WIDTH_CM, STANDARD_HEIGHT_CM, TOLERANCE_CM
from src.camera import get_camera
from src.processor import detect_shape, get_measurements, preprocess_frame, get_valid_contours
from src.overlay import draw_overlay, draw_info, draw_warning
from src.detector import load_model, detect_object

env = dotenv_values(".env")

# ─────────────────────────────────────────────
# CALIBRATION CONSTANT
# IMPORTANT: Calibrate this value before running
# pixels_per_cm = pixels_of_reference / actual_cm
PIXELS_PER_CM = 37.5  # ← Adjust this after calibration

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

        # ─── Preprocessing + Segmentation + Contours ─────
        binary = preprocess_frame(frame)
        valid_contours = get_valid_contours(binary)

        # ─── YOLO every 10 frames ─────────────────────────
        if frame_count % 10 == 0:
            yolo_label = detect_object(model, frame)

        # ─── Draw camera info and YOLO label ──────────────
        draw_info(display, camera_type, yolo_label)

        # ─── Per contour: shape, measure, overlay ─────────
        for contour in valid_contours:
            shape = detect_shape(contour)
            if shape == "Unknown":
                continue

            width_px, height_px, _ = get_measurements(contour, shape)

            width_cm = width_px / PIXELS_PER_CM
            height_cm = height_px / PIXELS_PER_CM

            if cv2.contourArea(contour) < 1500:
                draw_warning(display, "Low confidence")
                continue

            # Smooth measurements
            width_cm = 0.7 * prev_width + 0.3 * width_cm
            height_cm = 0.7 * prev_height + 0.3 * height_cm
            prev_width = width_cm
            prev_height = height_cm

            accepted = (
                abs(width_cm - STANDARD_WIDTH_CM) <= TOLERANCE_CM
                and abs(height_cm - STANDARD_HEIGHT_CM) <= TOLERANCE_CM
            )

            draw_overlay(display, contour, shape, width_cm, height_cm, yolo_label, accepted)

        cv2.imshow("Live Measurement System", display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("⏹️ Stopped by user")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_live()
