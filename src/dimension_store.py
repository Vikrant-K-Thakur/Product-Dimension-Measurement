import json
import os

DIMENSIONS_FILE = "data/saved_dimensions.json"


def load_dimensions():
    """Load all saved dimensions from file"""
    if not os.path.exists(DIMENSIONS_FILE):
        return {}
    with open(DIMENSIONS_FILE, "r") as f:
        return json.load(f)


def save_dimension(label, width_cm, height_cm, tolerance=0.5):
    """Save or update dimension for a given object label"""
    os.makedirs(os.path.dirname(DIMENSIONS_FILE), exist_ok=True)
    data = load_dimensions()

    data[label.lower()] = {
        "width":     round(width_cm, 2),
        "height":    round(height_cm, 2),
        "tolerance": tolerance
    }

    with open(DIMENSIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"\n{'─' * 40}")
    print(f"     Saved: {label}")
    print(f"  W : {width_cm:.2f} cm")
    print(f"  H : {height_cm:.2f} cm")
    print(f"  Tolerance: ±{tolerance} cm")
    print(f"{'─' * 40}")


def compare_dimension(label, width_cm, height_cm):
    """Compare measured dimensions with saved dimensions"""
    data = load_dimensions()
    std = data.get(label.lower())

    if not std:
        return None, f"No saved data for '{label}'"

    w_diff = abs(width_cm - std["width"])
    h_diff = abs(height_cm - std["height"])
    tol    = std["tolerance"]

    accepted = w_diff <= tol and h_diff <= tol

    info = {
        "accepted":        accepted,
        "saved_width":     std["width"],
        "saved_height":    std["height"],
        "measured_width":  round(width_cm, 2),
        "measured_height": round(height_cm, 2),
        "width_diff":      round(w_diff, 2),
        "height_diff":     round(h_diff, 2),
        "tolerance":       tol
    }

    return accepted, info
