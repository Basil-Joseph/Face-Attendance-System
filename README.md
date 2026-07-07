# 🎥 Face Attendance System

A beginner-friendly, Python-based attendance system that recognizes faces
via webcam and logs attendance automatically — built with **OpenCV** and
**face_recognition**.

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-learning%20project-yellow)

---

## ⚠️ Privacy Notice

This project works with **face photos and attendance logs of real
people**. Before using or sharing this repo.

---

## 🧠 How It Works

1. **Enroll** — add one clear photo per person to `known_faces/`
2. **Encode** — `encode_faces.py` converts each photo into a 128-number
   face "fingerprint" and saves it to `encodings.pickle`
3. **Recognize & log** — `attendance.py` opens your webcam, matches
   faces against known encodings in real time, and logs the first
   recognition of the day to `attendance.csv`

---

## 📦 Setup

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/face-attendance-system.git
cd face-attendance-system
```

### 2. Create a virtual environment (Python 3.12 recommended)

`face_recognition` depends on `dlib`, which has inconsistent support
for the newest Python releases. **Python 3.12** is the most reliable
choice on Windows as of writing.

```bash
py -3.12 -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install `dlib` (Windows only)

`dlib` usually needs a precompiled wheel on Windows since building it
from source requires CMake + a C++ compiler.

```bash
pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.99-cp312-cp312-win_amd64.whl
```
(macOS/Linux users can usually just `pip install dlib` directly.)

### 5. Add your known faces
```
known_faces/
├── alice.jpg
├── bob.jpg
```
See `known_faces/README.md` for details. **Do not commit these photos.**

### 6. Generate encodings
```bash
python encode_faces.py
```

### 7. Run the attendance system
```bash
python attendance.py
```
- Green box = recognized, name shown
- Red box = unrecognized ("Unknown")
- Press **q** to quit
- First recognition each day → logged to `attendance.csv`

---

## 🗂 Project Structure

| File/Folder | Purpose |
|---|---|
| `known_faces/` | Reference photos (gitignored — local only) |
| `encode_faces.py` | Builds face encodings from `known_faces/` |
| `attendance.py` | Live webcam recognition + attendance logging |
| `encodings.pickle` | Generated encoding database (gitignored) |
| `attendance.csv` | Generated attendance log (gitignored) |
| `requirements.txt` | Pinned Python dependencies |

---

## 🐞 Troubleshooting

Common issues encountered during setup, and fixes:

| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'cv2'` | Make sure your venv is activated and `pip install opencv-python` was run inside it, not globally |
| `dlib` wheel install fails | Use a precompiled wheel matching your exact Python version (see step 4) |
| `Please install face_recognition_models` | `pip install face_recognition_models` |
| `ModuleNotFoundError: No module named 'pkg_resources'` | `pip install "setuptools<81"` |
| `RuntimeError: Unsupported image type, must be 8bit gray or RGB image` | Your numpy version is likely incompatible with the compiled dlib wheel — run `pip install "numpy<2"` |
| Recognizes one photo but not other poses of the same person | Add 2–4 reference photos per person (different angles/lighting) instead of just one, and/or raise `MATCH_TOLERANCE` slightly in `attendance.py` |

---

## 🔧 Tuning Recognition Accuracy

In `attendance.py`:
```python
MATCH_TOLERANCE = 0.6
```
- Lower (e.g. `0.5`) = stricter matching, fewer false positives, more false "Unknown"s
- Higher (e.g. `0.65–0.7`) = more lenient, better with pose/lighting variation, but higher false-match risk

---

## 🚀 Possible Extensions

- Multiple reference photos per person for better accuracy
- SQLite instead of CSV for attendance storage
- Check-in **and** check-out timestamps
- Simple GUI (Tkinter or a web dashboard)
- Export attendance reports (daily/weekly/monthly)

---

## 📄 License

MIT — free to use and modify for personal/educational purposes.