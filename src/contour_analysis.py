import cv2
import os
from dotenv import dotenv_values

env = dotenv_values("../.env")


def detect_largest_contour(binary_path, original_path, output_path):
    # Read binary image (for contour detection)
    binary = cv2.imread(binary_path, cv2.IMREAD_GRAYSCALE)
    if binary is None:
        raise FileNotFoundError(f"Binary image not found: {binary_path}")

    # Read original image (for visualization)
    original = cv2.imread(original_path)
    if original is None:
        raise FileNotFoundError(f"Original image not found: {original_path}")

    # Find contours on binary image
    contours, _ = cv2.findContours(
        binary,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        raise ValueError("No contours detected")

    # Select largest contour
    largest_contour = max(contours, key=cv2.contourArea)

    # Bounding box
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Draw bounding box on original image
    cv2.rectangle(
        original,
        (x, y),
        (x + w, y + h),
        (0, 255, 0),
        2
    )

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save output
    cv2.imwrite(output_path, original)

    return x, y, w, h


if __name__ == "__main__":
    output_dir = env.get("OUTPUT_DIR")
    if not output_dir:
        raise ValueError("OUTPUT_DIR missing in .env")

    binary_image = os.path.join(output_dir, "binary_cleaned.jpg")
    original_image = os.path.join(output_dir, "product.png")
    output_image = os.path.join(output_dir, "contour_box.jpg")

    x, y, w, h = detect_largest_contour(
        binary_image,
        original_image,
        output_image
    )

    print("✅ Bounding box detected")
    print(f"Width (pixels) : {w}")
    print(f"Height (pixels): {h}")
    print(f"Saved at: {output_image}")
