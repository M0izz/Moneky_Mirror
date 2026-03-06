import cv2
import time
from meme_engine import MemeEngine
from hand_tracker import HandTracker
from overlay_engine import OverlayEngine
from ui import UI

def main():
    # Initialize components
    try:
        meme_engine = MemeEngine()
    except FileNotFoundError as e:
        print(e)
        return

    tracker = HandTracker()
    overlay = OverlayEngine(fade_duration=0.3)
    ui = UI()

    # Capture webcam with higher resolution
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    prev_time = time.time()
    current_meme_name = "idle_monkey"
    fps = 0.0
    main.gesture_history = []

    print("MonkeyMirror AI Running... Press 'q' to quit.")

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)

        # 1. Track Pose
        frame = tracker.find_pose(frame)
        landmarks = tracker.get_landmarks()

        # 2. Detect Gesture and Determine Meme
        detected_gesture = tracker.detect_gesture(landmarks)
        
        # Gesture Smoothing: Use the most frequent gesture in the last 5 frames
        main.gesture_history.append(detected_gesture)
        if len(main.gesture_history) > 5:
            main.gesture_history.pop(0)
            
        from collections import Counter
        counts = Counter(main.gesture_history)
        new_meme_name = counts.most_common(1)[0][0]

        # (Roast mode removed – all reactions driven by gestures only)
        
        # 3. Update Overlay
        if new_meme_name != current_meme_name:
            print(f"DEBUG: Detected Gesture -> {new_meme_name}")
            meme_img = meme_engine.get_meme(new_meme_name)
            overlay.set_meme(meme_img)
            current_meme_name = new_meme_name

        # 4. Get Current Meme Frame (with fading)
        meme_frame = overlay.get_current_frame(640, 720)

        # 5. Draw UI
        # Add FPS and Status to the webcam frame before drawing
        fps_text = f"FPS: {fps:.1f}"
        status_text = f"STATUS: {current_meme_name.replace('_', ' ').upper()}"
        cv2.putText(frame, fps_text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, status_text, (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        ui.draw(frame, meme_frame)

        # Calculate and display FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        # (Optional: print FPS to console or overlay on UI)
        # print(f"FPS: {fps:.2f}")

        # Check for exit
        if ui.should_exit():
            break

    cap.release()
    ui.close()

if __name__ == "__main__":
    main()
