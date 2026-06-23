Python 3.14.3 (v3.14.3:323c59a5e34, Feb  3 2026, 11:41:37) [Clang 16.0.0 (clang-1600.0.26.6)] on darwin
Enter "help" below or click "Help" above for more information.


import cv2
import mediapipe as mp
import math
import time
from pynput.keyboard import Key, Controller

keyboard = Controller()
mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.6
)

ACTIONS = {
    "FIST"  : lambda: keyboard.press(Key.media_play_pause),
    "ONE"   : lambda: keyboard.press(Key.media_play_pause),
    "TWO"   : lambda: keyboard.press(Key.media_next),
    "THREE" : lambda: keyboard.press(Key.media_volume_up),
    "FOUR"  : lambda: keyboard.press(Key.media_volume_down),
    "FIVE"  : lambda: keyboard.press(Key.media_volume_mute),
}

FINGER_MAP = {
    0: "FIST",
    1: "ONE",
    2: "TWO",
    3: "THREE",
    4: "FOUR",
    5: "FIVE",
}

GESTURE_LABEL = {
    "FIST"  : "FIST  — Play / Pause",
    "ONE"   : "ONE   — Play / Pause",
    "TWO"   : "TWO   — Next Track",
    "THREE" : "THREE — Volume UP",
    "FOUR"  : "FOUR  — Volume DOWN",
    "FIVE"  : "FIVE  — Mute",
    "PINCH" : "PINCH — Custom",
}

def count_fingers(lm):
    count = 0
    if lm[4].x < lm[3].x:
        count += 1
    for tip_id in [8, 12, 16, 20]:
        if lm[tip_id].y < lm[tip_id - 2].y:
            count += 1
    return count

def is_pinching(lm, w, h):
    x1 = int(lm[4].x * w)
    y1 = int(lm[4].y * h)
    x2 = int(lm[8].x * w)
    y2 = int(lm[8].y * h)
    return math.hypot(x2 - x1, y2 - y1) < 40

def draw_overlay(frame, hand_landmarks, gesture, triggered):
    h, w, _ = frame.shape

    if hand_landmarks:
        mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 180), thickness=2, circle_radius=4),
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2),
        )

    bar_color = (0, 180, 80) if triggered else (30, 30, 30)
    cv2.rectangle(frame, (0, 0), (w, 52), bar_color, -1)

    label = GESTURE_LABEL.get(gesture, "Show your hand...") if gesture else "Show your hand..."
    cv2.putText(frame, label, (15, 34),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA)

    elapsed  = time.time() - last_action_time
    progress = min(elapsed / 0.8, 1.0)
    cv2.rectangle(frame, (0, h - 5), (int(w * progress), h), (0, 200, 100), -1)

    if gesture:
        cv2.putText(frame, gesture, (w - 160, 34),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 255, 200), 2, cv2.LINE_AA)

    return frame

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("ERROR: Could not open webcam. Try changing 0 to 1 or 2.")
    exit()

last_action_time = 0
last_gesture     = None

print("\n" + "="*50)
print("  Hand Gesture Controller  -  press Q to quit")
print("="*50)
print("  Fist (0)   ->  Play / Pause")
print("  1 finger   ->  Play / Pause")
print("  2 fingers  ->  Next Track")
print("  3 fingers  ->  Volume UP")
print("  4 fingers  ->  Volume DOWN")
print("  5 fingers  ->  Mute")
print("  Pinch      ->  Custom")
print("="*50 + "\n")

try:
    while cap.isOpened():

        ret, frame = cap.read()
        if not ret:
            print("ERROR: Lost webcam feed.")
            break

        frame   = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb                = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results            = hands.process(rgb)
        rgb.flags.writeable = True

        gesture   = None
        triggered = False
        hand_lms  = None
... 
...         if results.multi_hand_landmarks:
...             hand_lms = results.multi_hand_landmarks[0]
...             lm       = hand_lms.landmark
... 
...             if is_pinching(lm, w, h):
...                 gesture = "PINCH"
...             else:
...                 n       = count_fingers(lm)
...                 gesture = FINGER_MAP.get(n)
... 
...         now = time.time()
...         if (gesture
...                 and gesture != last_gesture
...                 and (now - last_action_time) > 0.8):
... 
...             action = ACTIONS.get(gesture)
...             if action:
...                 action()
...                 triggered = True
...                 print(f"[ACTION] {GESTURE_LABEL.get(gesture, gesture)}")
... 
...             last_action_time = now
...             last_gesture     = gesture
... 
...         if gesture != last_gesture and (now - last_action_time) > 0.8:
...             last_gesture = None
... 
...         frame = draw_overlay(frame, hand_lms, gesture, triggered)
...         cv2.imshow("Gesture Controller  |  Q = quit", frame)
... 
...         if cv2.waitKey(1) & 0xFF == ord("q"):
...             print("\n[INFO] Quit. Goodbye!")
...             break
... 
... finally:
...     cap.release()
...     cv2.destroyAllWindows()
...     hands.close()
