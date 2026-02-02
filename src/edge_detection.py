import cv2
import os
from dotenv import dotenv_values

env = dotenv_values("../.env")

def detect_edges(
    input_path: str,
    output_path: str,
    low_threshold: int = 50,
    high_threshold: int = 150
) -> None:

    image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Image not found: {input_path}")

    # Canny Edge Detection
    edges = cv2.Canny(
        image,
        low_threshold,
        high_threshold
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, edges)

if __name__ == "__main__":
    output_dir = env.get("OUTPUT_DIR")
    if not output_dir:
        raise ValueError("OUTPUT_DIR missing in .env")

    input_image = os.path.join(output_dir, "binary_cleaned.jpg")
    # input_image = os.path.join(output_dir, "product_blurred.jpg")
    output_image = os.path.join(output_dir, "edges.jpg")

    detect_edges(input_image, output_image)

    print(f"✅ Edge image saved at: {output_image}")
