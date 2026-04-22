import cv2
from dotenv import dotenv_values

env = dotenv_values(".env")


def get_camera():
    """Try DroidCam first, fallback to laptop camera"""
    droidcam_url = env.get("DROID_CAM_URL", "")
    if droidcam_url:
        print("🔍 Trying DroidCam...")
        cap = cv2.VideoCapture(droidcam_url)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                print("✅ DroidCam connected!")
                return cap, "DroidCam"
        cap.release()

    print("📷 Using laptop camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("❌ No camera available!")
    print("✅ Laptop camera connected!")
    return cap, "Laptop"
