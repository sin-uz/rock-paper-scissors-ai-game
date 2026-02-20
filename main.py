import cv2
from hand_detector import HandDetector
from visualizer import AnnotationsVisualizer
from gesture_classifier import VectorBasedClassifier
from game_logic.game_controller import GameController

def main():

    cap = cv2.VideoCapture(0)

    classifier = VectorBasedClassifier()
    controller = GameController(classifier)
    visualizer = AnnotationsVisualizer()

    with HandDetector(user_perspective=True) as detector:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            frame = cv2.flip(frame, 1) 

            detected_hands = detector.detect(frame)

            controller.update(detected_hands)

            frame = visualizer.render(frame, detected_hands, mirror_display=False)

            frame = controller.render_ui(frame)
            
            cv2.imshow('Gra P-K-N', frame)
            
            if cv2.waitKey(1) & 0xFF == 27:
                break
                
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()