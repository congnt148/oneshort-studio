import cv2
from ultralytics import YOLO
import numpy as np
import torch


class YOLOModel:
    def __init__(self, model_path='assets/yolov8s.pt'):
        # Kiểm tra xem GPU có sẵn không và chuyển mô hình lên GPU
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = YOLO(model_path).to(self.device)

    def detect_objects(self, frame):
        # Chuyển frame sang tensor và chuyển lên GPU, đồng thời thay đổi kích thước frame để phù hợp với yêu cầu của mô hình
        frame_resized = cv2.resize(frame, (640, 640))
        frame_tensor = torch.from_numpy(frame_resized).permute(2, 0, 1).unsqueeze(0).float().to(self.device)

        # Gọi mô hình YOLO để phát hiện đối tượng
        results = self.model(frame_tensor)
        
        boxes = []
        centers = []
        for result in results:
            if result.boxes is not None:
                for box in result.boxes.xyxy:
                    boxes.append(box.cpu().numpy())
                    center_x = (box[0] + box[2]) / 2
                    centers.append(center_x)
                    
        return np.array(boxes), centers
