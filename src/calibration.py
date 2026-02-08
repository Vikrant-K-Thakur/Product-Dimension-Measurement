import cv2
import os
from dotenv import dotenv_values

env = dotenv_values(".env")


def calibrate(binary_image_path, reference_size_cm):
    binary = cv2.imread(binary_image_path, cv2.IMREAD_GRAYSCALE)
    if binary is None:
        raise FileNotFoundError(f"Binary image not found: {binary_image_path}")

    contours, _ = cv2.findContours(
        binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        raise ValueError("No contours found for calibration")

    # Filter out noise - only keep contours larger than 500 pixels
    contours = [c for c in contours if cv2.contourArea(c) > 500]

    if not contours:
        raise ValueError("No valid reference contour found")

    # Get smallest valid contour as reference
    reference_contour = min(contours, key=cv2.contourArea)

    x, y, w, h = cv2.boundingRect(reference_contour)

    reference_pixels = max(w, h)

    pixels_per_cm = reference_pixels / reference_size_cm

    print("🔧 CALIBRATION RESULTS")
    print(f"Reference size (cm)   : {reference_size_cm}")
    print(f"Reference size (pixel): {reference_pixels}")
    print(f"Pixels per cm         : {pixels_per_cm:.2f}")

    return pixels_per_cm


if __name__ == "__main__":
    output_dir = env.get("OUTPUT_DIR")
    if not output_dir:
        raise ValueError("OUTPUT_DIR missing in .env")

    binary_image = os.path.join(output_dir, "binary_cleaned.jpg")

    REFERENCE_SIZE_CM = 5.0

    calibrate(binary_image, REFERENCE_SIZE_CM)
