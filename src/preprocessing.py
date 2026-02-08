import cv2
import os
from dotenv import dotenv_values

env = dotenv_values(".env")

def convert_to_grayscale(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found")

    # cv2.imwrite(input_path, gray_image)
    # cv2.imshow("Grayscale Image", gray_image)

    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def apply_gaussian_blur(gray_image, kernel_size=(5, 5)):
    return cv2.GaussianBlur(gray_image, kernel_size, 0)


if __name__ == "__main__":
    input_path = os.path.join(env["OUTPUT_DIR"], "product.jpg")
    output_path = os.path.join(env["OUTPUT_DIR"], "product_blurred.jpg")

    gray = convert_to_grayscale(input_path)
    blurred = apply_gaussian_blur(gray)

    cv2.imwrite(output_path, blurred)
    print(f"✅ Blurred grayscale image saved at: {output_path}")
