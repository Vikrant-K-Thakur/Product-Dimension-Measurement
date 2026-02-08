import cv2
import os
import time
from dotenv import dotenv_values

env = dotenv_values(".env")

def try_droidcam():
    droidcam_url = env["DROID_CAM_URL"]
    cap = cv2.VideoCapture(droidcam_url)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            return cap
    
    cap.release()
    return None

def capture_image():
    input_dir = env["INPUT_DIR"]
    os.makedirs(input_dir, exist_ok=True)
    
    # Try DroidCam first
    print("Trying DroidCam...")
    cap = try_droidcam()
    camera_type = "DroidCam"
    
    # Fallback to PC camera
    if cap is None:
        print("📱 DroidCam not found, using PC camera...")
        cap = cv2.VideoCapture(0)
        camera_type = "PC Camera"
        
        if not cap.isOpened():
            print("❌ No camera available!")
            return False
    
    print(f"✅ {camera_type} connected!")
    print("\nControls:")
    print("• Press 'C' to capture image")
    print("• Press 'Q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Camera disconnected")
            break
        
        # Rotate frame if using DroidCam (portrait mode)
        if camera_type == "DroidCam":
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            # frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            # frame = cv2.rotate(frame, cv2.ROTATE_180)
        
        cv2.putText(
            frame,
            f"{camera_type} - Press 'C' to capture | 'Q' to quit",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )
        
        cv2.imshow("Product Image Capture", frame)
        cv2.setWindowProperty("Product Image Capture", cv2.WND_PROP_TOPMOST, 1)  # Keep window on top
        
        key = cv2.waitKey(1) & 0xFF
        
        # Debug: Print key presses
        if key != 255:  # 255 means no key pressed
            print(f"Key pressed: {key} ('{chr(key) if 32 <= key <= 126 else 'special'}')") 
        
        if key == ord('q') or key == ord('Q'):
            print("⏹️ Exited without saving")
            break
        elif key == ord('c') or key == ord('C'):
            filename = "product.jpg"
            filepath = os.path.join(input_dir, filename)
            success = cv2.imwrite(filepath, frame)
            if success:
                print(f"📸 Image saved to: {filepath}")
                break
            else:
                print("❌ Failed to save image!")
    
    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    capture_image()



