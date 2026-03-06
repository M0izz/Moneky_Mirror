import cv2
import numpy as np

try:
    import mediapipe.python.solutions.holistic as mp_holistic
    import mediapipe.python.solutions.drawing_utils as mp_draw
    import mediapipe.python.solutions.drawing_styles as mp_styles
except ImportError:
    from mediapipe.python.solutions import holistic as mp_holistic
    from mediapipe.python.solutions import drawing_utils as mp_draw
    from mediapipe.python.solutions import drawing_styles as mp_styles


# hand landmark indices
WRIST      = 0
THUMB_TIP  = 4
INDEX_TIP  = 8
MIDDLE_TIP = 12
RING_TIP   = 16
PINKY_TIP  = 20
INDEX_MCP  = 5
PINKY_MCP  = 17

# face mesh landmark indices
FACE_NOSE_TIP    = 1
FACE_UPPER_LIP   = 13
FACE_LOWER_LIP   = 14
FACE_CHIN        = 152
FACE_FOREHEAD    = 10
FACE_LEFT_EYE    = 33
FACE_RIGHT_EYE   = 263
FACE_MOUTH_LEFT  = 61
FACE_MOUTH_RIGHT = 291


class HandTracker:
    def __init__(self, min_detection_confidence=0.6, min_tracking_confidence=0.6):
        self.holistic = mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            refine_face_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.mp_draw   = mp_draw
        self.mp_styles = mp_styles
        self._results  = None

    def find_pose(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_rgb.flags.writeable = False
        self._results = self.holistic.process(img_rgb)
        img_rgb.flags.writeable = True

        if draw and self._results is not None:
            r = self._results
            if r.pose_landmarks:
                self.mp_draw.draw_landmarks(
                    img, r.pose_landmarks,
                    mp_holistic.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_styles.get_default_pose_landmarks_style(),
                )
            if r.left_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, r.left_hand_landmarks,
                    mp_holistic.HAND_CONNECTIONS,
                    self.mp_styles.get_default_hand_landmarks_style(),
                    self.mp_styles.get_default_hand_connections_style(),
                )
            if r.right_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, r.right_hand_landmarks,
                    mp_holistic.HAND_CONNECTIONS,
                    self.mp_styles.get_default_hand_landmarks_style(),
                    self.mp_styles.get_default_hand_connections_style(),
                )
        return img

    def get_landmarks(self):
        out = {"pose": {}, "left_hand": {}, "right_hand": {}, "face": {}}
        if self._results is None:
            return out

        r = self._results

        if r.pose_landmarks:
            for i, lm in enumerate(r.pose_landmarks.landmark):
                out["pose"][i] = (lm.x, lm.y, lm.z, lm.visibility)

        if r.left_hand_landmarks:
            for i, lm in enumerate(r.left_hand_landmarks.landmark):
                out["left_hand"][i] = (lm.x, lm.y, lm.z)

        if r.right_hand_landmarks:
            for i, lm in enumerate(r.right_hand_landmarks.landmark):
                out["right_hand"][i] = (lm.x, lm.y, lm.z)

        if r.face_landmarks:
            for i, lm in enumerate(r.face_landmarks.landmark):
                out["face"][i] = (lm.x, lm.y, lm.z)

        return out

    def detect_gesture(self, landmarks):
        pose       = landmarks.get("pose", {})
        left_hand  = landmarks.get("left_hand", {})
        right_hand = landmarks.get("right_hand", {})
        face       = landmarks.get("face", {})

        l_sh = pose.get(11)
        r_sh = pose.get(12)
        if not (l_sh and r_sh):
            return "idle_monkey"

        sh_mid_x   = (l_sh[0] + r_sh[0]) / 2
        sh_mid_y   = (l_sh[1] + r_sh[1]) / 2
        shoulder_w = abs(l_sh[0] - r_sh[0])

        # get face positions from mesh, fall back to pose nose if not available
        if face:
            lip_x  = face[FACE_UPPER_LIP][0]
            lip_y  = face[FACE_UPPER_LIP][1]
            chin_x = face[FACE_CHIN][0]
            chin_y = face[FACE_CHIN][1]
            nose_y = face[FACE_NOSE_TIP][1]
            nose_x = face[FACE_NOSE_TIP][0]
        else:
            nose_lm = pose.get(0)
            if not nose_lm:
                return "idle_monkey"
            nose_x = nose_lm[0]; nose_y = nose_lm[1]
            lip_x  = nose_x;     lip_y  = nose_y + 0.07
            chin_x = nose_x;     chin_y = nose_y + 0.13

        chest_y = sh_mid_y + 0.15

        def d(ax, ay, bx, by):
            return np.sqrt((ax - bx) ** 2 + (ay - by) ** 2)

        # get index fingertip or fall back to wrist
        def finger_tip(hand_lms, pose_wrist_id):
            if INDEX_TIP in hand_lms:
                return hand_lms[INDEX_TIP][:2]
            w = pose.get(pose_wrist_id)
            return (w[0], w[1]) if w else None

        r_tip = finger_tip(right_hand, 16)
        l_tip = finger_tip(left_hand, 15)

        r_wrist_y = right_hand[WRIST][1] if WRIST in right_hand else (pose.get(16) or (0,0))[1]
        l_wrist_y = left_hand[WRIST][1]  if WRIST in left_hand  else (pose.get(15) or (0,0))[1]
        r_wrist_x = right_hand[WRIST][0] if WRIST in right_hand else (pose.get(16) or (0,0))[0]
        l_wrist_x = left_hand[WRIST][0]  if WRIST in left_hand  else (pose.get(15) or (0,0))[0]

        # idea - one hand raised, one not, and raised finger is actually extended
        r_above_sh = r_tip is not None and r_tip[1] < r_sh[1] - 0.05
        l_above_sh = l_tip is not None and l_tip[1] < l_sh[1] - 0.05
        if r_above_sh ^ l_above_sh:
            active_hand = right_hand if r_above_sh else left_hand
            idx_mcp = active_hand.get(INDEX_MCP)
            idx_tip_lm = active_hand.get(INDEX_TIP)
            if idx_mcp and idx_tip_lm:
                if idx_tip_lm[1] < idx_mcp[1]:
                    return "idea_monkey"
            else:
                return "idea_monkey"

        # scared - both hands near chest, upright posture
        d_l_chest = abs(l_wrist_y - chest_y)
        d_r_chest = abs(r_wrist_y - chest_y)
        is_upright = shoulder_w < 0.40 and abs(nose_x - sh_mid_x) < 0.08
        if d_l_chest < 0.13 and d_r_chest < 0.13 and is_upright:
            return "scared_monkey"

        # evil plan - smiling with hands pressed together below shoulders
        if r_tip and l_tip:
            hands_sep = d(r_tip[0], r_tip[1], l_tip[0], l_tip[1])
        else:
            hands_sep = d(r_wrist_x, r_wrist_y, l_wrist_x, l_wrist_y)

        is_smiling = False
        if face and FACE_MOUTH_LEFT in face and FACE_MOUTH_RIGHT in face:
            ml = face[FACE_MOUTH_LEFT]
            mr = face[FACE_MOUTH_RIGHT]
            ul = face[FACE_UPPER_LIP]
            ll = face[FACE_LOWER_LIP]
            mouth_width  = d(ml[0], ml[1], mr[0], mr[1])
            mouth_height = d(ul[0], ul[1], ll[0], ll[1]) + 1e-6
            is_smiling = (mouth_width / mouth_height) > 2.5

        hands_below = r_wrist_y > sh_mid_y and l_wrist_y > sh_mid_y
        if hands_sep < 0.14 and is_smiling and hands_below:
            return "evil_plan_monkey"

        # neuron activation - leaning forward, hands away from face
        r_far = r_tip is None or d(r_tip[0], r_tip[1], lip_x, lip_y) > 0.18
        l_far = l_tip is None or d(l_tip[0], l_tip[1], lip_x, lip_y) > 0.18
        if shoulder_w > 0.42 and r_far and l_far:
            return "neuron_activation"

        # wink - right finger near lips but to the right side
        if r_tip:
            d_r_lip = d(r_tip[0], r_tip[1], lip_x, lip_y)
            if d_r_lip < 0.10 and r_tip[0] > lip_x - 0.01:
                return "wink_monkey"

        # thinking - right finger near lips, any horizontal position
        if r_tip:
            d_r_lip = d(r_tip[0], r_tip[1], lip_x, lip_y)
            if d_r_lip < 0.14 and r_tip[1] > nose_y:
                return "thinking_monkey"

        # nerd - hand on chin OR both hands low like reading
        for tip, hx, hy in [(r_tip, chin_x, chin_y), (l_tip, chin_x, chin_y)]:
            if tip and d(tip[0], tip[1], hx, hy) < 0.11:
                return "nerd_monkey"

        both_low   = l_wrist_y > sh_mid_y + 0.08 and r_wrist_y > sh_mid_y + 0.08
        close_horiz = abs(l_wrist_x - r_wrist_x) < 0.30
        close_total = d(l_wrist_x, l_wrist_y, r_wrist_x, r_wrist_y) < 0.28
        if both_low and close_horiz and close_total:
            return "nerd_monkey"

        return "idle_monkey"
