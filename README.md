# 📦 Product Dimension Measurement System

A real-time AI-enhanced product measurement and inspection system built using Python, OpenCV, and YOLOv8.

---

## 🎯 What It Does

- Opens camera (Laptop or DroidCam mobile app)
- Detects objects in real time
- Identifies shape — Circle, Square, Rectangle
- Measures dimensions in real-world units (cm)
- Displays measurements directly on live video
- Detects object type using YOLOv8
- Compares with standard values and shows **ACCEPTED ✅** or **REJECTED ❌**

---

## 🗂️ Project Structure

```
Product_Dimension_Measurement/
├── config/
│   └── standards.py        ← Standard dimensions and tolerance values
├── data/
│   ├── input/              ← Captured images (ignored by git)
│   └── output/             ← Processed images (ignored by git)
├── src/
│   ├── camera.py           ← Camera connection (DroidCam / Laptop)
│   ├── detector.py         ← YOLOv8 object detection
│   ├── processor.py        ← Preprocessing, segmentation, shape detection
│   ├── overlay.py          ← Drawing bounding boxes and text on screen
│   └── live_measurement.py ← Main pipeline (entry point)
├── .env                    ← Your local config (not pushed to GitHub)
├── .env.example            ← Template for .env
├── requirements.txt        ← Python dependencies
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/Product_Dimension_Measurement.git
cd Product_Dimension_Measurement
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup environment variables
```bash
cp .env.example .env
```
Then open `.env` and update the values:
```
DROID_CAM_URL=http://YOUR_PHONE_IP:4747/video
```

### 4. Download YOLOv8 model
The model downloads automatically on first run. Or manually:
```bash
pip install ultralytics
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

---

## ▶️ How to Run

From the project root directory:
```bash
python -m src.live_measurement
```

### Controls
| Key | Action |
|-----|--------|
| `Q` | Quit the system |

---

## 📷 Camera Support

### Laptop Camera
Used automatically if DroidCam is not available.

### DroidCam (Mobile Camera)
1. Install **DroidCam** app on your phone
2. Connect phone and PC to the **same WiFi**
3. Update `DROID_CAM_URL` in `.env` with your phone's IP
4. Run the system — it will try DroidCam first, fallback to laptop camera

---

## 📐 Calibration

Before accurate measurements, calibrate `PIXELS_PER_CM` in `src/live_measurement.py`:

1. Place a known object (e.g. ruler) in front of camera
2. Count how many pixels it spans
3. Calculate: `PIXELS_PER_CM = pixels / actual_cm`
4. Update line in `live_measurement.py`:
```python
PIXELS_PER_CM = 37.5  # ← change this value
```

---

## 📊 Standard Dimensions

Edit `config/standards.py` to set your product's expected dimensions:
```python
STANDARD_WIDTH_CM  = 10.0   # expected width
STANDARD_HEIGHT_CM = 5.0    # expected height
TOLERANCE_CM       = 0.5    # allowed ± error
```

---

## 🧰 Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Core language |
| OpenCV | Image processing and camera |
| YOLOv8 (Ultralytics) | Object detection |
| python-dotenv | Environment variable management |
| NumPy | Numerical operations |

---

## 📋 Requirements

```
opencv-python
python-dotenv
ultralytics
numpy
```

---

## 🚀 Output Example

On live video screen:
```
Shape  : Rectangle
W      : 10.20 cm
H      : 5.10 cm
Area   : 52.02 cm2
Object : bottle
Status : ACCEPTED
```

---
