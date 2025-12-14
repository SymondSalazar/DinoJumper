import cv2
import mediapipe as mp
import threading
import time
import numpy as np
from typing import Optional


class InputHandler:
    def __init__(self) -> None:
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose

        self.cap = cv2.VideoCapture(0)

        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )

        self.UMBRAL_SALTO = 0.4
        self.UMBRAL_AGACHARSE = 0.7
        self.UMBRAL_MANO_RESET = 0.3

        self.lock = threading.Lock()
        self.jump_pressed = False
        self.jump_triggered = False
        self.duck_pressed = False
        self.was_jumping = False

        self.hand_raised = False
        self.hand_raise_triggered = False
        self.was_hand_raised = False

        self.game_over_state = False

        self.current_frame = None
        self.frame_lock = threading.Lock()

        self.running = True
        self.camera_thread = None
        self._start_camera_thread()

    def _start_camera_thread(self) -> None:
        if self.camera_thread is None or not self.camera_thread.is_alive():
            self.running = True
            self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
            self.camera_thread.start()

    def _camera_loop(self) -> None:
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            results = self.pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            height, width, _ = image.shape

            if self.game_over_state:
                cv2.line(
                    image,
                    (0, int(height * self.UMBRAL_MANO_RESET)),
                    (width, int(height * self.UMBRAL_MANO_RESET)),
                    (255, 0, 255),
                    2,
                )
            else:
                cv2.line(
                    image,
                    (0, int(height * self.UMBRAL_SALTO)),
                    (width, int(height * self.UMBRAL_SALTO)),
                    (0, 255, 0),
                    2,
                )

                cv2.line(
                    image,
                    (0, int(height * self.UMBRAL_AGACHARSE)),
                    (width, int(height * self.UMBRAL_AGACHARSE)),
                    (0, 0, 255),
                    2,
                )

            current_jump_state = False
            current_duck_state = False
            current_hand_raised = False

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                nose_y = landmarks[self.mp_pose.PoseLandmark.NOSE].y

                if self.game_over_state:
                    left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
                    right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]

                    if (
                        left_wrist.y < self.UMBRAL_MANO_RESET
                        or right_wrist.y < self.UMBRAL_MANO_RESET
                    ):
                        current_hand_raised = True
                        cv2.putText(
                            image,
                            "MANO ARRIBA - RESET",
                            (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (255, 0, 255),
                            2,
                        )

                if nose_y < self.UMBRAL_SALTO:
                    current_jump_state = True
                    cv2.putText(
                        image,
                        "SALTANDO",
                        (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                    )

                elif nose_y > self.UMBRAL_AGACHARSE:
                    current_duck_state = True
                    cv2.putText(
                        image,
                        "AGACHADO",
                        (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2,
                    )
                else:
                    cv2.putText(
                        image,
                        "NEUTRO",
                        (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 255, 255),
                        2,
                    )

                self.mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
                )

            with self.lock:
                if current_jump_state and not self.was_jumping:
                    self.jump_triggered = True
                else:
                    self.jump_triggered = False

                self.jump_pressed = current_jump_state
                self.duck_pressed = current_duck_state
                self.was_jumping = current_jump_state

                if current_hand_raised and not self.was_hand_raised:
                    self.hand_raise_triggered = True
                else:
                    self.hand_raise_triggered = False

                self.hand_raised = current_hand_raised
                self.was_hand_raised = current_hand_raised

            with self.frame_lock:
                self.current_frame = image.copy()

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.close()
                break

    # No lo elimines es necesario para Pygame
    def update(self) -> None:
        pass

    def reset(self) -> None:
        with self.lock:
            self.jump_pressed = False
            self.jump_triggered = False
            self.duck_pressed = False
            self.was_jumping = False
            self.hand_raised = False
            self.hand_raise_triggered = False
            self.was_hand_raised = False
            self.game_over_state = False

    def set_game_over(self, is_game_over: bool) -> None:
        with self.lock:
            self.game_over_state = is_game_over

    def get_camera_frame(self) -> Optional[np.ndarray]:
        with self.frame_lock:
            if self.current_frame is not None:
                frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                frame_rgb = cv2.flip(frame_rgb, 1)
                frame_rgb = np.rot90(frame_rgb)
                return frame_rgb
        return None

    def is_jump_just_pressed(self) -> bool:
        with self.lock:
            result = self.jump_triggered
            if result:
                self.jump_triggered = False
            return result

    def is_jump_held(self) -> bool:
        with self.lock:
            return self.jump_pressed

    def is_duck_held(self) -> bool:
        with self.lock:
            return self.duck_pressed

    def is_hand_raised_just_now(self) -> bool:
        with self.lock:
            result = self.hand_raise_triggered
            if result:
                self.hand_raise_triggered = False
            return result

    def close(self) -> None:
        self.running = False
        if self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.join(timeout=1.0)
        if self.cap.isOpened():
            self.cap.release()

    def __del__(self) -> None:
        self.close()
