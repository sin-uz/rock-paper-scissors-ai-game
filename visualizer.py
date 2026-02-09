import cv2
import mediapipe as mp


class AnnotationsVisualizer:
    def __init__(self, landmarks=True, connections=True, bbox=True, label=True):
        self.draw_landmarks = landmarks
        self.draw_connections = connections
        self.draw_bbox = bbox
        self.draw_label = label
        self.mp_hands = mp.solutions.hands

    def render(self, image, detected_hands, mirror_display):
        height, width = image.shape[:2]

        for hand_label, landmarks_norm in detected_hands.items():
            landmarks_px = self._to_pixel_points(
                landmarks_norm, width, height, mirror_display
            )
            
            if not landmarks_px:
                continue

            bbox = self._bounding_box(landmarks_px)
            self._draw_hand_features(image, landmarks_px, bbox, hand_label)

        return image

    def _draw_hand_features(self, image, landmarks_px, bbox, label):
        if self.draw_landmarks:
            self._draw_landmarks(image, landmarks_px)

        if self.draw_connections:
            self._draw_connections(image, landmarks_px)

        if self.draw_bbox:
            self._draw_bbox(image, bbox)

        if self.draw_label:
            self._draw_label(image, label, bbox)

    @staticmethod
    def _to_pixel_points(landmarks_norm, width, height, mirror_display):
        points = []

        for x_norm, y_norm, _ in landmarks_norm:
            if mirror_display:
                x_norm = 1.0 - x_norm

            x_px = int(x_norm * (width - 1))
            y_px = int(y_norm * (height - 1))
            points.append((x_px, y_px))

        return points

    @staticmethod
    def _bounding_box(points):
        xs = [x for x, _ in points]
        ys = [y for _, y in points]
        return min(xs), min(ys), max(xs), max(ys)

    @staticmethod
    def _draw_landmarks(image, points):
        for x_px, y_px in points:
            cv2.circle(image, (x_px, y_px), 4, (0, 255, 0), cv2.FILLED)

    def _draw_connections(self, image, points):
        for start_idx, end_idx in self.mp_hands.HAND_CONNECTIONS:
            x1, y1 = points[start_idx]
            x2, y2 = points[end_idx]
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    @staticmethod
    def _draw_bbox(image, bbox):
        x_min, y_min, x_max, y_max = bbox
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (255, 0, 255), 2)

    @staticmethod
    def _draw_label(image, label, bbox):
        x_min, y_min, _, _ = bbox
        cv2.putText(
            image, label, (x_min, y_min - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2
        )
