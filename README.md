# Monkey Mirror 🐒

a lil side project i made to mess around with computer vision. basically your webcam watches your face + hands and swaps in a monkey reaction meme depending on what you're doing lol

---

## what it does

it tracks your body in real time and picks one of 8 monkey images based on your pose/expression

| what you do | what appears |
|-------------|-------------|
| just sitting there | 🐒 base monkey |
| right finger on lips | 🤔 thinking monkey |
| smile + hands pressed together | 😈 evil plan monkey |
| one finger pointed up | ☝️ idea monkey |
| hand on chin / pretending to read | 🤓 nerd monkey |
| lean toward the camera | 🧠 neuron activation |
| finger on the side of your lips | 😏 wink monkey |
| both hands on chest | 😱 scared monkey |

---

## stuff used

- **MediaPipe Holistic** — does all the heavy lifting (21-point hand tracking, 468-point face mesh, full body pose)
- **OpenCV** — grabs the webcam feed and handles frame processing
- **Pillow** — renders the meme images and draws captions on them
- **NumPy** — math for landmark distances and gesture logic
- **Tkinter** — the display window

---

## run it yourself

```bash
git clone https://github.com/M0izz/Moneky_Mirror.git
cd Moneky_Mirror

python -m venv .venv
.venv\Scripts\activate      # windows
# source .venv/bin/activate  # mac/linux

pip install -r requirements.txt
python main.py
```

press `q` to quit

---

## how the gesture detection works

uses MediaPipe's holistic model which gives you 3 sets of landmarks at once:
- **face mesh** (468 pts) → exact lip/chin/smile positions
- **hand tracking** (21 pts per hand) → individual fingertip positions  
- **body pose** (33 pts) → shoulder/elbow/wrist positions

smile detection specifically works by measuring mouth width vs height — if the ratio is above a threshold, you're smiling

---

made this mostly to learn how mediapipe works. turned out to be pretty fun
