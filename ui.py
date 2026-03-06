import cv2
import numpy as np

class UI:
    def __init__(self, window_name="MonkeyMirror AI"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        # Higher internal resolution for better quality
        self.width = 1920
        self.height = 1080

    def draw(self, webcam_frame, meme_frame):
        # Resize webcam frame to half width
        webcam_h, webcam_w = webcam_frame.shape[:2]
        target_webcam_w = self.width // 2
        target_webcam_h = self.height
        
        # Use better interpolation for higher quality
        webcam_resized = cv2.resize(webcam_frame, (target_webcam_w, target_webcam_h), interpolation=cv2.INTER_AREA)
        
        # Ensure meme frame matches size
        meme_resized = cv2.resize(meme_frame, (target_webcam_w, target_webcam_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Convert BGRA to BGR if necessary
        if meme_resized.shape[2] == 4:
            meme_resized = cv2.cvtColor(meme_resized, cv2.COLOR_BGRA2BGR)

        # Concatenate side by side
        combined = np.hstack((webcam_resized, meme_resized))
        
        # Add UI Overlays (Text) - Styled for premium look
        overlay_color = (0, 255, 255) # Cyan/Yellow
        cv2.putText(combined, "LIVE FEED", (40, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 4)
        cv2.putText(combined, "LIVE FEED", (40, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 0), 2)
        
        cv2.putText(combined, "MONKEY MIRROR", (target_webcam_w + 40, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 4)
        cv2.putText(combined, "MONKEY MIRROR", (target_webcam_w + 40, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, overlay_color, 2)

        cv2.imshow(self.window_name, combined)

    def should_exit(self):
        return cv2.waitKey(1) & 0xFF == ord('q')

    def close(self):
        cv2.destroyAllWindows()
