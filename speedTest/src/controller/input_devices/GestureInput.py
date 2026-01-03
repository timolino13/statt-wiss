import cv2
import mediapipe as mp
import numpy as np
from threading import Thread
from controller.input_devices.InputDevice import InputDevice

mp_hands = mp.solutions.hands

class GestureInput(InputDevice):
    """
    Handgesten-Input. Erkennt Faust und Handbewegungen.
    Kommuniziert nur über den CursorController.
    """
    def __init__(self, cursor_controller):
        super().__init__(cursor_controller)
        self.active = False
        self.thread = None
        self.click_hold = False

    def activate(self):
        self.active = True
        self.thread = Thread(target=self._hand_tracking, daemon=True)
        self.thread.start()

    def deactivate(self):
        self.active = False
        if self.thread is not None:
            self.thread.join(timeout=1)

    def _is_fist(self, hand_landmarks):
        wrist = hand_landmarks.landmark[0]
        finger_tips = [8, 12, 16, 20]
        finger_bases = [5, 9, 13, 17]

        folded = 0
        for tip, base in zip(finger_tips, finger_bases):
            tip_y = hand_landmarks.landmark[tip].y
            base_y = hand_landmarks.landmark[base].y
            tip_x = hand_landmarks.landmark[tip].x
            base_x = hand_landmarks.landmark[base].x

            folded_condition = tip_y > base_y
            dist_to_wrist = np.sqrt((tip_x - wrist.x)**2 + (tip_y - wrist.y)**2)
            close_condition = dist_to_wrist < 0.15

            if folded_condition and close_condition:
                folded += 1

        return folded >= 3

    def _hand_center(self, hand_landmarks):
        points = [hand_landmarks.landmark[0], hand_landmarks.landmark[9]]
        x = np.mean([p.x for p in points])
        y = np.mean([p.y for p in points])
        return x, y

    def _hand_tracking(self):
        cap = cv2.VideoCapture(0)
        with mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.9,
            min_tracking_confidence=0.7
        ) as hands:
            while self.active:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        fist = self._is_fist(hand_landmarks)
                        hx, hy = self._hand_center(hand_landmarks)

                        # Übergabe an CursorController (x/y normiert zwischen 0 und 1)
                        self.input_controller.move_to(hx, hy)

                        if fist:
                            if not self.click_hold:
                                self.input_controller.left_click(hx, hy)
                                self.click_hold = True
                        else:
                            if self.click_hold:
                                self.input_controller.left_release(hx, hy)
                                self.click_hold = False

                # optional Debugkamera
                cv2.imshow("Handkamera (Debug)", frame)
                if cv2.waitKey(1) & 0xFF == 27:  # ESC
                    break

        cap.release()
        cv2.destroyAllWindows()


    def get_name(self):
        return "Hand Tracking"
