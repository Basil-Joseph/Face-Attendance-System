

import os
import csv
import pickle
from datetime import datetime

import cv2
import face_recognition

ENCODINGS_FILE = "encodings.pickle"
ATTENDANCE_FILE = "attendance.csv"
MATCH_TOLERANCE = 0.6  # lower = stricter matching. 0.6 is a good default.

# Minimum minutes that must pass after check-in before a check-out can be
# recorded. This prevents check-out from firing seconds after check-in due
# to consecutive camera frames recognizing the same person.
CHECKOUT_MIN_GAP_MINUTES = 5

CSV_HEADER = ["Name", "Date", "CheckIn", "CheckOut"]


def load_encodings():
    if not os.path.exists(ENCODINGS_FILE):
        print(f"'{ENCODINGS_FILE}' not found. Run encode_faces.py first.")
        exit()

    with open(ENCODINGS_FILE, "rb") as f:
        data = pickle.load(f)
    return data["encodings"], data["names"]


def read_attendance_rows():
    """Read all attendance rows (excluding header) as a list of dicts."""
    if not os.path.exists(ATTENDANCE_FILE):
        return []

    with open(ATTENDANCE_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_attendance_rows(rows):
    """Overwrite the CSV file with the given rows (list of dicts)."""
    with open(ATTENDANCE_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writeheader()
        writer.writerows(rows)


def get_today_status(name, rows):
    """
    Look for today's row for this person.
    Returns one of: "not_checked_in", "checked_in", "checked_out"
    and the matching row (or None).
    """
    today = datetime.now().strftime("%Y-%m-%d")

    for row in rows:
        if row["Name"] == name and row["Date"] == today:
            if row.get("CheckOut"):
                return "checked_out", row
            return "checked_in", row

    return "not_checked_in", None


def minutes_since(time_str):
    """Return minutes elapsed since a HH:MM:SS time string (today)."""
    checkin_time = datetime.strptime(time_str, "%H:%M:%S").time()
    now = datetime.now()
    checkin_dt = now.replace(
        hour=checkin_time.hour, minute=checkin_time.minute,
        second=checkin_time.second, microsecond=0
    )
    return (now - checkin_dt).total_seconds() / 60


def mark_checkin(name, rows):
    """Add a new row with today's check-in time."""
    now = datetime.now()
    new_row = {
        "Name": name,
        "Date": now.strftime("%Y-%m-%d"),
        "CheckIn": now.strftime("%H:%M:%S"),
        "CheckOut": "",
    }
    rows.append(new_row)
    write_attendance_rows(rows)
    print(f"Checked IN: {name} at {new_row['CheckIn']}")


def mark_checkout(name, row, rows):
    """Update today's existing row with a check-out time."""
    now = datetime.now()
    row["CheckOut"] = now.strftime("%H:%M:%S")
    write_attendance_rows(rows)
    print(f"Checked OUT: {name} at {row['CheckOut']}")


def process_recognition(name):
    """
    Decide whether to check this person in, check them out, or do
    nothing (already checked out, or still within cooldown window).
    Returns a short status string to display on screen.
    """
    rows = read_attendance_rows()
    status, row = get_today_status(name, rows)

    if status == "not_checked_in":
        mark_checkin(name, rows)
        return "Checked In"

    if status == "checked_in":
        gap = minutes_since(row["CheckIn"])
        if gap >= CHECKOUT_MIN_GAP_MINUTES:
            mark_checkout(name, row, rows)
            return "Checked Out"
        return f"In ({row['CheckIn']})"

    return f"In {row['CheckIn']} / Out {row['CheckOut']}"


def run_attendance_system():
    known_encodings, known_names = load_encodings()
    print(f"Loaded {len(known_names)} known face(s): {sorted(set(known_names))}")

    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("Could not access webcam. Check your camera connection/permissions.")
        return

    print("Starting camera... press 'q' to quit.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Resize frame for faster processing (optional but helps speed)
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Find faces in this frame
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(
                known_encodings, face_encoding, tolerance=MATCH_TOLERANCE
            )
            name = "Unknown"
            status_label = ""

            # Find the closest match
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = face_distances.argmin()
                if matches[best_match_index]:
                    name = known_names[best_match_index]

            # Scale face location back up (since frame was resized to 0.25x)
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Handle check-in / check-out logic for recognized faces
            if name != "Unknown":
                status_label = process_recognition(name)

            # Draw box and label on the frame
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            label = f"{name} - {status_label}" if status_label else name
            cv2.putText(
                frame, label, (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
            )

        cv2.imshow("Face Attendance System - press q to quit", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_attendance_system()