# known_faces/

Add reference photos here so the system can recognize people. **Two
structures are supported:**

## Option A (Recommended): folder per person, multiple photos

```
known_faces/
├── alice/
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── photo3.jpg
└── bob/
    ├── photo1.jpg
    └── photo2.jpg
```

Use **2-4 photos per person** with different angles, lighting, and
expressions. This significantly improves recognition accuracy compared
to a single photo — the system checks new faces against *all* stored
photos for that person and picks the closest match.

## Option B: single flat photo per person

```
known_faces/
├── alice.jpg
└── bob.jpg
```

Still works, but less accurate across different poses/lighting than
Option A. Good for quick testing.

You can mix both structures in the same `known_faces/` folder.

---

⚠️ **This folder is intentionally excluded from git via `.gitignore`.**
Face photos are personal/biometric data and should never be committed to
a public (or even private) GitHub repo. Keep them local only.

If you fork or clone this project, you'll need to add your own photos
here before running `encode_faces.py`.