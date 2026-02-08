import cv2
import os
from dotenv import dotenv_values

env = dotenv_values(".env")

def grayscale_to_binary(
    input_path: str,
    output_path: str,
    threshold: int = 0
) -> None:

    image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {input_path}")

    if threshold == 0:
        # Automatic thresholding (Otsu)
        _, binary = cv2.threshold(
            image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
    else:
        # Manual thresholding
        _, binary = cv2.threshold(
            image, threshold, 255, cv2.THRESH_BINARY
        )

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    cv2.imwrite(output_path, binary)


def clean_binary_image(
    input_path: str,
    output_path: str,
    kernel_size: int = 3,
    iterations: int = 1
) -> None:

    image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {input_path}")

    # Ensure binary format
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (kernel_size, kernel_size)
    )

    # Opening: remove noise
    opened = cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        kernel,
        iterations=iterations
    )

    # Closing: fill gaps
    cleaned = cv2.morphologyEx(
        opened,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=iterations
    )

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    cv2.imwrite(output_path, cleaned)


if __name__ == "__main__":
    output_dir = env.get("OUTPUT_DIR")
    if not output_dir:
        raise ValueError("OUTPUT_DIR not found in .env")

    grayscale_path = os.path.join(output_dir, "product_blurred.jpg")
    binary_path = os.path.join(output_dir, "binary.jpg")
    cleaned_path = os.path.join(output_dir, "binary_cleaned.jpg")

    # Step 1: Segmentation (thresholding)
    grayscale_to_binary(
        input_path=grayscale_path,
        output_path=binary_path
    )

    # Step 2: Post-processing (morphology)
    clean_binary_image(
        input_path=binary_path,
        output_path=cleaned_path,
        kernel_size=3,
        iterations=1
    )
