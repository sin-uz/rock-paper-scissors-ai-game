import mediapipe as mp
from collections import deque

from .domain import SyncPhase, SyncStatus


class RoundSynchronizer:
    def __init__(
        self,
        classifier,
        min_half_cycles: int = 4,
        min_amplitude: float = 0.035,
        vel_still_threshold: float = 0.30,
        still_time: float = 0.18,
        move_window: int = 7,
        move_consensus: int = 5,
        max_shake_time: float = 2.4,
    ):
        self.classifier = classifier
        self.min_half_cycles = min_half_cycles
        self.min_amplitude = min_amplitude
        self.vel_still_threshold = vel_still_threshold
        self.still_time = still_time
        self.move_window = move_window
        self.move_consensus = move_consensus
        self.max_shake_time = max_shake_time

        self._reset_internal()

    def reset(self) -> None:
        self._reset_internal()

    def update(self, side, landmarks, t):
        if not landmarks:
            # self._reset_internal()
            return None, self.status()

        wrist_y_coord= self._get_coordinate(landmarks, self._HL.WRIST, 1)
        print(f"wrist: {wrist_y_coord}")

        if self._last_t is None:
            self._last_t = t
            self._last_wrist_y = wrist_y_coord
            return None, self.status()

        dt = max(t - self._last_t, 1e-6)
        dy = wrist_y_coord - self._last_wrist_y
        wrist_velocity = dy / dt

        if self._phase == SyncPhase.WAITING:
            self._shake_start_t = t
            self._phase = SyncPhase.SHAKING
            self._extrema_y = wrist_y_coord
            self._last_dir = 0

        if self._phase == SyncPhase.SHAKING and self._shake_start_t is not None:
            if (t - self._shake_start_t) > self.max_shake_time:
                self._reset_internal()
                return None, self.status()

        if self._phase == SyncPhase.SHAKING:
            cur_dir = 1 if wrist_velocity > 0 else (
                -1 if wrist_velocity < 0 else 0
            )

            if self._extrema_y is None:
                self._extrema_y = wrist_y_coord
            else:
                if cur_dir >= 0:
                    self._extrema_y = max(self._extrema_y, wrist_y_coord)
                if cur_dir <= 0:
                    self._extrema_y = min(self._extrema_y, wrist_y_coord)

            if self._last_dir != 0 and cur_dir != 0 and cur_dir != self._last_dir:
                if self._pivot_y is None:
                    self._pivot_y = self._last_wrist_y

                amp = abs(wrist_y_coord - self._pivot_y)
                if amp >= self.min_amplitude:
                    self._half_cycles += 1
                    self._pivot_y = wrist_y_coord

            if cur_dir != 0:
                self._last_dir = cur_dir

            if self._half_cycles >= self.min_half_cycles:
                if abs(wrist_velocity) < self.vel_still_threshold:
                    if self._still_start_t is None:
                        self._still_start_t = t
                    elif (t - self._still_start_t) >= self.still_time:
                        self._phase = SyncPhase.LOCKING

        move = self.classifier.determine_move(side, landmarks)
        if self._phase == SyncPhase.LOCKING:
            if move is not None:
                self._moves.append(move)

            locked = self._try_lock()
            if locked is not None:
                self._reset_internal()
                return locked, self.status()

            if abs(wrist_velocity) >= self.vel_still_threshold * 1.8:
                self._phase = SyncPhase.SHAKING
                self._still_start_t = None
                self._moves.clear()

        self._last_t = t
        self._last_wrist_y = wrist_y_coord
        return None, self.status()

    def status(self):
        progress = min(self._half_cycles / max(self.min_half_cycles, 1), 1.0)
        return SyncStatus(
            phase=self._phase, cycles=self._half_cycles, progress=progress
        )

    def _try_lock(self):
        if len(self._moves) < self.move_window:
            return None

        freq = {}
        for m in self._moves:
            freq[m] = freq.get(m, 0) + 1

        best_move, best_count = max(freq.items(), key=lambda kv: kv[1])
        if best_count >= self.move_consensus:
            return best_move
        return None

    def _reset_internal(self) -> None:
        self._phase = SyncPhase.WAITING
        self._half_cycles = 0
        self._shake_start_t = None
        self._still_start_t = None

        self._last_t = None
        self._last_wrist_y = None

        self._last_dir: int = 0
        self._pivot_y = None
        self._extrema_y = None

        self._moves = deque(maxlen=self.move_window)

    @staticmethod
    def _get_coordinate(landmarks, landmark_id, axis):
        return landmarks[int(landmark_id)][axis]

    @property
    def _HL(self):
        return mp.solutions.hands.HandLandmark
    


