from ultralytics import YOLO
import numpy as np

class YOLOModel:
    def __init__(self, model_path='assets/yolov8s.pt'):
        self.model = YOLO(model_path)

    def detect_objects(self, frame):
        results = self.model(frame)
        boxes = []
        for result in results:
            if result.boxes is not None:
                for box in result.boxes.xyxy:
                    boxes.append(box.cpu().numpy())
        return np.array(boxes)
