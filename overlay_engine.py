import cv2
import numpy as np
import time

class OverlayEngine:
    def __init__(self, fade_duration=0.5):
        self.fade_duration = fade_duration
        self.current_meme = None
        self.target_meme = None
        self.fade_start_time = 0
        self.alpha = 1.0
        self.is_fading = False

    def set_meme(self, meme_img):
        # meme_img is already a CV2 format (BGRA) numpy array from MemeEngine
        meme_cv = meme_img.copy()
        
        if self.current_meme is None:
            self.current_meme = meme_cv
            self.alpha = 1.0
            return

        if np.array_equal(self.target_meme, meme_cv):
            return

        self.target_meme = meme_cv
        self.fade_start_time = time.time()
        self.is_fading = True

    def get_current_frame(self, width, height):
        if self.current_meme is None:
            return np.zeros((height, width, 4), dtype=np.uint8)

        if self.is_fading:
            elapsed = time.time() - self.fade_start_time
            if elapsed >= self.fade_duration:
                self.current_meme = self.target_meme
                self.target_meme = None
                self.is_fading = False
                self.alpha = 1.0
            else:
                self.alpha = elapsed / self.fade_duration
                # Blend current and target
                current_resized = cv2.resize(self.current_meme, (width, height))
                target_resized = cv2.resize(self.target_meme, (width, height))
                blended = cv2.addWeighted(current_resized, 1.0 - self.alpha, target_resized, self.alpha, 0)
                return blended

        return cv2.resize(self.current_meme, (width, height))
