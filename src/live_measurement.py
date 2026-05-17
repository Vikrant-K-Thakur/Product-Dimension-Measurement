import cv2
from dotenv import dotenv_values

from config.standards import PRODUCT_STANDARDS
from src.camera import get_camera
from src.processor import preprocess_frame, get_valid_contours
from src.overlay import draw_overlay, draw_info, draw_warning
from src.detector import load_model, detect_object
from src.dimension_store import save_dimension, compare_dimension, load_dimensions

env = dotenv_values(".env")

# ─────────────────────────────────────────────
# CALIBRATION CONSTANT
# IMPORTANT: Calibrate this value before running
# pixels_per_cm = pixels_of_reference / actual_cm
PIXELS_PER_CM = 40.0  # ← Adjust this after calibration

if PIXELS_PER_CM <= 0:
    raise ValueError("Invalid calibration value: PIXELS_PER_CM must be > 0")
# ─────────────────────────────────────────────


def show_menu():
    print("\n" + "═" * 45)
    print("   📦 PRODUCT DIMENSION MEASUREMENT SYSTEM")
    print("═" * 45)
    print("  1️⃣  Option 1 — Save object dimensions")
    print("       Place object → system measures →")
    print("       Press S to save dimensions")
    print()
    print("  2️⃣  Option 2 — Compare object dimensions")
    print("       Place object → system compares with")
    print("       saved data → ACCEPTED / REJECTED")
    print()
    print("  3️⃣  Option 3 — Quit")
    print("═" * 45)
    print("  Enter 1, 2 or 3: ", end="")
    choice = input().strip()
    print("═" * 45)
    return choice


def get_stable_measurement(cap, camera_type, model, samples=20):
    """
    Collect multiple readings and return the median
    for accurate stable measurement before saving
    """
    width_readings  = []
    height_readings = []
    label_readings  = []
    frame_count     = 0
    yolo_label      = "Unknown"
    yolo_bbox       = None

    print("   Collecting stable readings...", end="", flush=True)

    while len(width_readings) < samples:
        ret, frame = cap.read()
        if not ret:
            break

        if camera_type == "DroidCam":
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        frame_count += 1

        # Run YOLO every 5 frames during sampling
        if frame_count % 5 == 0:
            yolo_label, yolo_bbox = detect_object(model, frame)

        if yolo_bbox and yolo_label != "Unknown":
            x, y, w, h = yolo_bbox
            width_readings.append(w / PIXELS_PER_CM)
            height_readings.append(h / PIXELS_PER_CM)
            label_readings.append(yolo_label)
            print(".", end="", flush=True)

        cv2.waitKey(1)

    print(" Done!")

    if not width_readings:
        return None, None, None

    # Use median for accuracy — removes outliers
    width_readings.sort()
    height_readings.sort()
    mid = len(width_readings) // 2
    stable_width  = width_readings[mid]
    stable_height = height_readings[mid]

    # Most common label
    stable_label = max(set(label_readings), key=label_readings.count)

    return stable_label, stable_width, stable_height


def run_save_mode(cap, camera_type, model):
    """Option 1 — Measure and save object dimensions"""
    print("\n  MODE: SAVE DIMENSIONS")
    print("  • Show object in front of camera")
    print("  • Press S to capture stable measurement and save")
    print("  • Press Q to quit\n")

    frame_count = 0
    yolo_label  = "Unknown"
    yolo_bbox   = None
    prev_width  = None  # None so EMA starts from first real reading
    prev_height = None
    width_cm    = 0
    height_cm   = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("  Camera disconnected")
            break

        if camera_type == "DroidCam":
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        display = frame.copy()
        frame_count += 1

        # YOLO every 10 frames
        if frame_count % 10 == 0:
            yolo_label, yolo_bbox = detect_object(model, frame)

        draw_info(display, camera_type, yolo_label)

        cv2.putText(display, "MODE: SAVE  |  Press S to save",
            (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

        if yolo_bbox:
            x, y, w, h = yolo_bbox

            raw_width  = w / PIXELS_PER_CM
            raw_height = h / PIXELS_PER_CM

            # EMA — start from first real reading, not from 0
            if prev_width is None:
                prev_width  = raw_width
                prev_height = raw_height

            width_cm  = 0.6 * prev_width  + 0.4 * raw_width
            height_cm = 0.6 * prev_height + 0.4 * raw_height
            prev_width  = width_cm
            prev_height = height_cm

            shape = "Rectangle" if abs(w - h) > 10 else "Square"

            cv2.rectangle(display, (x, y), (x + w, y + h), (255, 150, 0), 2)

            texts = [
                f"Shape : {shape}",
                f"W     : {width_cm:.2f} cm",
                f"H     : {height_cm:.2f} cm",
                f"Object: {yolo_label}",
                f"Press S to SAVE",
            ]
            text_y = max(y - 10, 130)
            for i, text in enumerate(texts):
                cv2.putText(display, text,
                    (x, text_y + i * 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 150, 0), 2)
        else:
            draw_warning(display, "No object detected — show object to camera")

        cv2.imshow("Save Mode — Product Dimension", display)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == ord('Q'):
            print("   Exited save mode")
            break

        elif key == ord('s') or key == ord('S'):
            if yolo_label == "Unknown" or not yolo_bbox:
                print("⚠️  No object detected. Show object clearly first.")
            else:
                # Collect stable readings before saving
                stable_label, stable_w, stable_h = get_stable_measurement(
                    cap, camera_type, model
                )
                if stable_w is None:
                    print("⚠️  Could not get stable reading. Try again.")
                else:
                    save_dimension(stable_label, stable_w, stable_h)

    cv2.destroyAllWindows()


def run_compare_mode(cap, camera_type, model):
    """Option 2 — Compare object dimensions with saved data"""
    saved = load_dimensions()

    if not saved:
        print("\n⚠️  No saved dimensions found!")
        print("   Please run Option 1 first to save dimensions.")
        return

    print("\n📌 MODE: COMPARE DIMENSIONS")
    print(f"  • Saved objects: {', '.join(saved.keys())}")
    print("  • Show object → auto compares with saved data")
    print("  • Press Q to quit\n")

    frame_count  = 0
    yolo_label   = "Unknown"
    yolo_bbox    = None
    prev_width   = None  # None so EMA starts from first real reading
    prev_height  = None
    width_cm     = 0
    height_cm    = 0
    last_label   = None
    last_accepted = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("  Camera disconnected")
            break

        if camera_type == "DroidCam":
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        display = frame.copy()
        frame_count += 1

        # YOLO every 10 frames
        if frame_count % 10 == 0:
            yolo_label, yolo_bbox = detect_object(model, frame)

        draw_info(display, camera_type, yolo_label)

        # Mode label on screen
        cv2.putText(display, "MODE: COMPARE  |  Press Q to quit",
            (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

        if yolo_bbox:
            x, y, w, h = yolo_bbox

            raw_width  = w / PIXELS_PER_CM
            raw_height = h / PIXELS_PER_CM

            # EMA — start from first real reading, not from 0
            if prev_width is None:
                prev_width  = raw_width
                prev_height = raw_height

            width_cm  = 0.6 * prev_width  + 0.4 * raw_width
            height_cm = 0.6 * prev_height + 0.4 * raw_height
            prev_width  = width_cm
            prev_height = height_cm

            shape = "Rectangle" if abs(w - h) > 10 else "Square"

            # Compare with saved dimensions
            accepted, info = compare_dimension(yolo_label, width_cm, height_cm)

            if accepted is None:
                # No saved data for this object
                draw_overlay(display, yolo_bbox, shape, width_cm, height_cm, yolo_label, False)
                draw_warning(display, f"No saved data for '{yolo_label}' — run Option 1 first")
            else:
                draw_overlay(display, yolo_bbox, shape, width_cm, height_cm, yolo_label, accepted)

                # Print to terminal only when result changes
                if yolo_label != last_label or accepted != last_accepted:
                    last_label   = yolo_label
                    last_accepted = accepted
                    status = "ACCEPTED " if accepted else "REJECTED "
                    print(f"\n{'─' * 45}")
                    print(f"  Object   : {yolo_label}")
                    print(f"  Measured W : {width_cm:.2f} cm  (saved: {info['saved_width']} cm)")
                    print(f"  Measured H : {height_cm:.2f} cm  (saved: {info['saved_height']} cm)")
                    print(f"  Diff W   : {info['width_diff']} cm")
                    print(f"  Diff H   : {info['height_diff']} cm")
                    print(f"  Tolerance: ±{info['tolerance']} cm")
                    print(f"  Result   : {status}")
                    print(f"{'─' * 45}")
        else:
            draw_warning(display, "No object detected — show object to camera")

        cv2.imshow("Compare Mode — Product Dimension", display)

        if cv2.waitKey(1) & 0xFF in [ord('q'), ord('Q')]:
            print("   Exited compare mode")
            break

    cv2.destroyAllWindows()


def run_live():
    cap, camera_type = get_camera()
    model = load_model()

    while True:
        choice = show_menu()

        if choice == "1":
            run_save_mode(cap, camera_type, model)
        elif choice == "2":
            run_compare_mode(cap, camera_type, model)
        elif choice == "3":
            print("\n Thank You!")
            break
        else:
            print(" Invalid choice. Please enter 1, 2 or 3.")

    cap.release()


if __name__ == "__main__":
    run_live()
