# known_faces/

Put reference photos here — **one clear, front-facing photo per person**,
named after them:

```
known_faces/
├── alice.jpg
├── bob.jpg
└── priya.jpg
```

⚠️ **This folder is intentionally excluded from git via `.gitignore`.**
Face photos are personal/biometric data and should never be committed to
a public (or even private) GitHub repo. Keep them local only.

If you fork or clone this project, you'll need to add your own photos
here before running `encode_faces.py`.