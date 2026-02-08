import os
from dotenv import dotenv_values

from src.image_capture import capture_image
from src.preprocessing import convert_to_grayscale, apply_gaussian_blur
from src.segmentation import grayscale_to_binary, clean_binary_image
from src.contour_analysis import detect_largest_contour
from src.calibration import calibrate
from src.measurement import measure_dimensions
from src.comparison import compare_dimensions


def main():

    print("\n🚀 STARTING PRODUCT DIMENSION MEASUREMENT SYSTEM\n")

    env = dotenv_values(".env")

    input_dir = env.get("INPUT_DIR")
    output_dir = env.get("OUTPUT_DIR")

    if not input_dir or not output_dir:
        raise ValueError("INPUT_DIR or OUTPUT_DIR missing in .env")

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # STEP 1 — Capture Image
    print("📸 Capturing image...")
    capture_image()

    product_image = os.path.join(input_dir, "product.jpg")
    
    # Safety check: Ensure image was captured
    if not os.path.exists(product_image):
        raise FileNotFoundError("Image capture failed.")
    
    blurred_image = os.path.join(output_dir, "product_blurred.jpg")
    binary_image = os.path.join(output_dir, "binary.jpg")
    cleaned_binary = os.path.join(output_dir, "binary_cleaned.jpg")
    contour_output = os.path.join(output_dir, "contour_box.jpg")

    # STEP 2 — Preprocessing
    print("🧠 Preprocessing image...")

    gray = convert_to_grayscale(product_image)
    blurred = apply_gaussian_blur(gray)

    import cv2
    cv2.imwrite(blurred_image, blurred)

    # STEP 3 — Segmentation
    print("✂️ Segmenting product...")

    grayscale_to_binary(blurred_image, binary_image)
    clean_binary_image(binary_image, cleaned_binary)

    # STEP 4 — Contour Detection
    print("📦 Detecting product contour...")

    x, y, w, h = detect_largest_contour(
        cleaned_binary,
        product_image,
        contour_output
    )

    print(f"Detected Width (pixels): {w}")
    print(f"Detected Height (pixels): {h}")

    # STEP 5 — Calibration
    print("\n📏 Performing calibration...")

    REFERENCE_SIZE_CM = 5.0   # change if using different reference object

    pixels_per_cm = calibrate(
        cleaned_binary,
        REFERENCE_SIZE_CM
    )

    # STEP 6 — Measurement
    print("\n📐 Measuring product dimensions...")

    width_cm, height_cm = measure_dimensions(
        w,
        h,
        pixels_per_cm
    )

    # STEP 7 — Comparison
    print("\n📊 Comparing with standard dimensions...\n")

    compare_dimensions(width_cm, height_cm)

    print("\n✅ PROCESS COMPLETED SUCCESSFULLY!")
    print(f"📁 Check output images in: {output_dir}\n")


if __name__ == "__main__":
    main()
