# 🐒 Monkey Mirror

A real-time AI-powered webcam app that detects your body language and facial expressions using **MediaPipe Holistic** and mirrors back the matching monkey meme — live.

---

## ✨ Features

- 🖐️ **21-point finger tracking** per hand — exact fingertip positions
- 😀 **468-point face mesh** — precise lip, chin, and smile detection
- 🏃 **33-point body pose** — shoulder, elbow, and wrist positions
- ⚡ **8 gesture-triggered monkey reactions** with smooth fade transitions
- 🎭 **Pre-rendered meme overlays** for high-performance real-time playback

---

## 🎭 Gesture Map

| Gesture | Trigger |
|---------|---------|
| 🪑 **Idle** (`monkey.png`) | Default — sitting still |
| 🤔 **Thinking** (`thinking.png`) | Right index finger near lips (center) |
| 😈 **Evil Plan** (`evil.png`) | Smiling + both hands pressed together |
| ☝️ **Idea** (`idea.png`) | One finger raised above shoulder |
| 🤓 **Nerd** (`nerd.png`) | Hand on chin OR both hands low (reading) |
| 🧠 **Neuron Activation** (`neuron.png`) | Leaning forward toward camera |
| 😏 **Wink** (`wink.png`) | Right finger near the right side of lips |
| 😱 **Scared** (`scared.png`) | Both hands on chest, upright posture |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A webcam

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/monkey-mirror.git
cd monkey-mirror

# Create & activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

Press **`q`** to quit.

---

## 📁 Project Structure

```
monkey-mirror/
├── assets/              # Monkey PNG images (8 variants)
│   ├── monkey.png       # Base image (idle)
│   ├── thinking.png
│   ├── evil.png
│   ├── idea.png
│   ├── nerd.png
│   ├── neuron.png
│   ├── wink.png
│   └── scared.png
├── hand_tracker.py      # MediaPipe Holistic gesture detection
├── meme_engine.py       # Meme variant renderer
├── overlay_engine.py    # Smooth fade engine
├── ui.py                # Tkinter display window
├── main.py              # Entry point
└── requirements.txt
```

---

## 🛠️ Built With

- [MediaPipe](https://mediapipe.dev/) — Holistic landmark detection
- [OpenCV](https://opencv.org/) — Camera capture & image processing
- [Pillow](https://pillow.readthedocs.io/) — Image rendering & captions
- [NumPy](https://numpy.org/) — Numeric operations

---

## 📄 License

MIT License — feel free to use, modify, and share!
