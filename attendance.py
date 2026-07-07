

import os
import csv
import pickle
from datetime import datetime

import cv2
import face_recognition

ENCODINGS_FILE = "encodings.pickle"
ATTENDANCE_FILE = "attendance.csv"
MATCH_TOLERANCE = 0.6  # lower = stricter matching. 0.6 is a good default.


def load_encodings():
    if not os.path.exists(ENCODINGS_FILE):
        print(f"'{ENCODINGS_FILE}' not found. Run encode_faces.py first.")
        exit()

    with open(ENCODINGS_FILE, "rb") as f:
        data = pickle.load(f)
    return data["encodings"], data["names"]


def already_marked_today(name):
    """Check if this person already has an attendance entry for today."""
    if not os.path.exists(ATTENDANCE_FILE):
        return False

    today = datetime.now().strftime("%Y-%m-%d")
    with open(ATTENDANCE_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2 and row[0] == name and row[1] == today:
                return True
    return False


def mark_attendance(name):
    """Append a new row: name, date, time."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    file_exists = os.path.exists(ATTENDANCE_FILE)
    with open(ATTENDANCE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Name", "Date", "Time"])
        writer.writerow([name, date_str, time_str])

    print(f"Attendance marked for {name} at {time_str}")


def run_attendance_system():
    known_encodings, known_names = load_encodings()
    print(f"Loaded {len(known_names)} known face(s): {known_names}")

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

            # Draw box and name on the frame
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(
                frame, name, (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
            )

            # Mark attendance if recognized and not already marked today
            if name != "Unknown" and not already_marked_today(name):
                mark_attendance(name)

        cv2.imshow("Face Attendance System - press q to quit", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_attendance_system()