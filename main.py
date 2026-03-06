import cv2
import time
from collections import Counter
from meme_engine import MemeEngine
from hand_tracker import HandTracker
from overlay_engine import OverlayEngine
from ui import UI


def main():
    try:
        meme_engine = MemeEngine()
    except FileNotFoundError as e:
        print(e)
        return

    tracker = HandTracker()
    overlay = OverlayEngine(fade_duration=0.3)
    ui = UI()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print("couldn't open webcam")
        return

    prev_time = time.time()
    current_meme_name = "idle_monkey"
    fps = 0.0
    gesture_history = []

    print("running... press q to quit")

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)

        frame = tracker.find_pose(frame)
        landmarks = tracker.get_landmarks()

        detected = tracker.detect_gesture(landmarks)

        # smooth over last 5 frames to avoid flickering
        gesture_history.append(detected)
        if len(gesture_history) > 5:
            gesture_history.pop(0)

        new_meme_name = Counter(gesture_history).most_common(1)[0][0]

        if new_meme_name != current_meme_name:
            print(f"gesture: {new_meme_name}")
            meme_img = meme_engine.get_meme(new_meme_name)
            overlay.set_meme(meme_img)
            current_meme_name = new_meme_name

        meme_frame = overlay.get_current_frame(640, 720)

        fps_text = f"FPS: {fps:.1f}"
        status_text = current_meme_name.replace('_', ' ').upper()
        cv2.putText(frame, fps_text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, status_text, (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        ui.draw(frame, meme_frame)

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        if ui.should_exit():
            break

    cap.release()
    ui.close()


if __name__ == "__main__":
    main()
