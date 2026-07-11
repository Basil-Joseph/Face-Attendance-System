

import os
import pickle
import face_recognition

KNOWN_FACES_DIR = "known_faces"
ENCODINGS_FILE = "encodings.pickle"
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def encode_image(path, known_encodings, known_names, name):
    """Load one image, find a face, and append its encoding if found."""
    image = face_recognition.load_image_file(path)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        print(f"  No face found in {os.path.basename(path)}, skipping.")
        return False

    # Use the first face found in the image
    known_encodings.append(encodings[0])
    known_names.append(name)
    return True


def encode_known_faces():
    known_encodings = []
    known_names = []
    per_person_count = {}

    if not os.path.exists(KNOWN_FACES_DIR):
        print(f"Folder '{KNOWN_FACES_DIR}' not found. Create it and add photos first.")
        return

    entries = os.listdir(KNOWN_FACES_DIR)

    if not entries:
        print(f"'{KNOWN_FACES_DIR}' is empty. Add photos or per-person folders.")
        return

    for entry in entries:
        entry_path = os.path.join(KNOWN_FACES_DIR, entry)

        if os.path.isdir(entry_path):
            # --- Structure 1: folder per person, multiple photos ---
            name = entry
            photo_files = [
                f for f in os.listdir(entry_path)
                if f.lower().endswith(IMAGE_EXTENSIONS)
            ]

            if not photo_files:
                print(f"No photos found in known_faces/{name}/, skipping.")
                continue

            print(f"Processing '{name}' ({len(photo_files)} photo(s)) ...")
            count_before = len(known_names)
            for photo_file in photo_files:
                photo_path = os.path.join(entry_path, photo_file)
                encode_image(photo_path, known_encodings, known_names, name)
            added = len(known_names) - count_before
            per_person_count[name] = per_person_count.get(name, 0) + added
            if added:
                print(f"  Encoded {added}/{len(photo_files)} photo(s) for '{name}'")

        elif entry.lower().endswith(IMAGE_EXTENSIONS):
            # --- Structure 2: flat single photo per person ---
            name = os.path.splitext(entry)[0]  # "basil.jpg" -> "basil"
            print(f"Processing {entry} ...")
            success = encode_image(entry_path, known_encodings, known_names, name)
            if success:
                per_person_count[name] = per_person_count.get(name, 0) + 1
                print(f"  Encoded successfully as '{name}'")

    if not known_names:
        print("\nNo faces were encoded. Check that your photos contain visible faces.")
        return

    # Save everything to a pickle file
    data = {"encodings": known_encodings, "names": known_names}
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(data, f)

    print(f"\nDone! Encoded {len(known_names)} face image(s) across "
          f"{len(per_person_count)} person(s):")
    for name, count in per_person_count.items():
        note = "" if count > 1 else "  (consider adding more photos for better accuracy)"
        print(f"  - {name}: {count} photo(s){note}")
    print(f"\nSaved to '{ENCODINGS_FILE}'.")


if __name__ == "__main__":
    encode_known_faces()