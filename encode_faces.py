

import os
import pickle
import face_recognition

KNOWN_FACES_DIR = "known_faces"
ENCODINGS_FILE = "encodings.pickle"


def encode_known_faces():
    known_encodings = []
    known_names = []

    if not os.path.exists(KNOWN_FACES_DIR):
        print(f"Folder '{KNOWN_FACES_DIR}' not found. Create it and add photos first.")
        return

    image_files = [
        f for f in os.listdir(KNOWN_FACES_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not image_files:
        print(f"No images found in '{KNOWN_FACES_DIR}'. Add one photo per person.")
        return

    for filename in image_files:
        name = os.path.splitext(filename)[0]  # "basil.jpg" -> "basil"
        path = os.path.join(KNOWN_FACES_DIR, filename)

        print(f"Processing {filename} ...")
        image = face_recognition.load_image_file(path)

        # Detect face(s) and get their encodings
        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:
            print(f"  No face found in {filename}, skipping.")
            continue

        # Use the first face found in the image
        known_encodings.append(encodings[0])
        known_names.append(name)
        print(f"  Encoded successfully as '{name}'")

    # Save everything to a pickle file
    data = {"encodings": known_encodings, "names": known_names}
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(data, f)

    print(f"\nDone! Encoded {len(known_names)} face(s).")
    print(f"Saved to '{ENCODINGS_FILE}'.")


if __name__ == "__main__":
    encode_known_faces()