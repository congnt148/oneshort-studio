import cv2
from models.frame_item import FrameItem
import threading
import torch

class VideoProcessor:
    def __init__(self, yolo_model, view):
        self.yolo_model = yolo_model
        self.view = view

    def extract_frames(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error: Could not open video.")
            return []

        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        target_width = int(height * (9 / 16))

        frames = []
        index = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
             # Chuyển frame sang GPU
            # frame_tensor = torch.tensor(frame).to(self.yolo_model.device)
            # boxes, centers = self.yolo_model.detect_objects(frame_tensor)
            # center_x = frame.shape[1] // 2
            frame_item = FrameItem(index, 0, frame)
            frames.append(frame_item)
            index += 1

        cap.release()
        return frames
    

    def display_frames_in_timeline(self, frame_items):
        if frame_items:
            self.view.display_frames_in_timeline(frame_items)

