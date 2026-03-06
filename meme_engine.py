import os
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np


class MemeEngine:
    """
    Manages and pre-renders the 8 monkey meme variants.

    Variant → PNG mapping:
      idle_monkey       → monkey.png   (default / blank stare)
      thinking_monkey   → thinking.png (right hand on lips)
      evil_plan_monkey  → evil.png     (both hands together, head forward)
      idea_monkey       → idea.png     (one finger raised up)
      nerd_monkey       → nerd.png     (hand on chin / reading)
      neuron_activation → neuron.png   (leaning forward)
      wink_monkey       → wink.png     (finger near lips, right side)
      scared_monkey     → scared.png   (hands on chest, upright)
    """

    def __init__(self, base_image_path="assets/monkey.png"):
        self.base_image_path = base_image_path
        if not os.path.exists(base_image_path):
            raise FileNotFoundError(f"Base image not found at {base_image_path}")

        self.base_image = Image.open(base_image_path).convert("RGBA")
        self.width, self.height = self.base_image.size

        try:
            self.font = ImageFont.truetype("arial.ttf", 40)
        except Exception:
            self.font = ImageFont.load_default()

        # ── 8 variants ────────────────────────────────────────────────────────
        self.variants = {
            "idle_monkey":       {"image": "monkey.png",   "caption": ""},
            "thinking_monkey":   {"image": "thinking.png", "caption": "hmmm..."},
            "evil_plan_monkey":  {"image": "evil.png",     "caption": "mwahahaha..."},
            "idea_monkey":       {"image": "idea.png",     "caption": "I got an idea!"},
            "nerd_monkey":       {"image": "nerd.png",     "caption": "ERM... ACTUALLY"},
            "neuron_activation": {"image": "neuron.png",   "caption": "NEURON ACTIVATION"},
            "wink_monkey":       {"image": "wink.png",     "caption": ";)"},
            "scared_monkey":     {"image": "scared.png",   "caption": "OH NO!!"},
        }

        # Pre-render all variants for high-performance playback
        self.meme_cache = {}
        self._pre_render_all()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _get_base_image(self, filename):
        path = os.path.join("assets", filename)
        if not os.path.exists(path):
            print(f"[MemeEngine] Warning: '{path}' not found – falling back to base image.")
            path = self.base_image_path
        return Image.open(path).convert("RGBA")

    def _add_caption(self, img, text):
        if not text:
            return img
        draw = ImageDraw.Draw(img)
        w, h = img.size
        font_size = max(20, int(w * 0.07))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (w - tw) // 2
        y = h - th - int(h * 0.05)

        # Thick black outline for readability
        for ox in range(-3, 4):
            for oy in range(-3, 4):
                if ox != 0 or oy != 0:
                    draw.text((x + ox, y + oy), text, font=font, fill="black")
        draw.text((x, y), text, font=font, fill="white")
        return img

    def _generate_meme(self, variant_name):
        v = self.variants[variant_name]
        img = self._get_base_image(v["image"])
        img = self._add_caption(img, v["caption"])
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGRA)

    def _pre_render_all(self):
        print(f"[MemeEngine] Pre-rendering {len(self.variants)} meme variants...")
        for name in self.variants:
            self.meme_cache[name] = self._generate_meme(name)
        print("[MemeEngine] Pre-rendering complete.")

    # ── Public API ────────────────────────────────────────────────────────────

    def get_meme(self, variant_name):
        return self.meme_cache.get(variant_name,
                                   self.meme_cache.get("idle_monkey"))

    def get_all_memes(self):
        return {name: self.get_meme(name) for name in self.variants}
