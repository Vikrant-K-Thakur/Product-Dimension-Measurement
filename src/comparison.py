import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.standards import (
    STANDARD_WIDTH_CM,
    STANDARD_HEIGHT_CM,
    TOLERANCE_CM
)

def calculate_match_percentage(measured, standard):
 
    difference = abs(measured - standard)
    match_percent = max(0, (1 - difference / standard) * 100)
    return match_percent


def compare_dimensions(measured_width, measured_height):

    width_match = calculate_match_percentage(
        measured_width, STANDARD_WIDTH_CM
    )

    height_match = calculate_match_percentage(
        measured_height, STANDARD_HEIGHT_CM
    )

    overall_match = (width_match + height_match) / 2

    print(f"Width Match  : {width_match:.0f}%")
    print(f"Height Match : {height_match:.0f}%")
    print(f"Overall Match: {overall_match:.0f}%")

    # Optional decision logic
    if (
        abs(measured_width - STANDARD_WIDTH_CM) <= TOLERANCE_CM
        and abs(measured_height - STANDARD_HEIGHT_CM) <= TOLERANCE_CM
    ):
        print("Result: PRODUCT ACCEPTED ✅")
    else:
        print("Result: PRODUCT REJECTED ❌")

    return width_match, height_match, overall_match


if __name__ == "__main__":
    MEASURED_WIDTH = 9.6
    MEASURED_HEIGHT = 5.1

    compare_dimensions(MEASURED_WIDTH, MEASURED_HEIGHT)
