import cv2
import numpy as np

def measure_dimensions(width_pixels, height_pixels, pixels_per_cm):
    if pixels_per_cm <= 0:
        raise ValueError("Invalid pixels_per_cm value")

    width_cm = width_pixels / pixels_per_cm
    height_cm = height_pixels / pixels_per_cm

    print("📐 MEASUREMENT RESULTS")
    print(f"Width  (pixels): {width_pixels}")
    print(f"Height (pixels): {height_pixels}")
    print(f"Width  (cm)    : {width_cm:.2f}")
    print(f"Height (cm)    : {height_cm:.2f}")

    return width_cm, height_cm


if __name__ == "__main__":
    # Example values (from contour_analysis.py and calibration.py)
    WIDTH_PIXELS = 412
    HEIGHT_PIXELS = 198
    PIXELS_PER_CM = 37.5

    measure_dimensions(WIDTH_PIXELS, HEIGHT_PIXELS, PIXELS_PER_CM)
