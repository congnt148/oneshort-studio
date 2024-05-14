import cv2
import numpy as np
from ultralytics import YOLO
# import time
# import os

# Load YOLOv8 model
model = YOLO('yolov8s.pt')  # Load YOLOv8 model, you can replace 'yolov8s.pt' with other model variants if needed

# Load EDSR model for super-resolution
# model_path = "EDSR_x2.pb"
# if not os.path.isfile(model_path):
#     raise FileNotFoundError(f"Model file {model_path} not found. Please ensure the model file is in the correct path.")

# sr_model = cv2.dnn_superres.DnnSuperResImpl_create()
# sr_model.readModel(model_path)
# sr_model.setModel('edsr', 2)  # Assuming you want 2x upscaling

def detect_objects(frame):
    results = model(frame)
    # Extract bounding box coordinates
    boxes = []
    for result in results:
        if result.boxes is not None:
            for box in result.boxes.xyxy:
                boxes.append(box.cpu().numpy())
    return np.array(boxes)

def crop_and_upscale_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Could not open input video.")
        return
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total frames in video

    # Calculate the target width to maintain aspect ratio 9:16 (vertical video)
    target_width = int(height * (9 / 16))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_width * 4, height * 4))  # Multiply by 4 due to upscaling

    if not out.isOpened():
        print("Error: Could not open output video for writing.")
        return

    frame_count = 0  # Frame counter

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1  # Increment frame counter

        # Object Detection
        boxes = detect_objects(frame)

        # Calculate crop width to maintain aspect ratio 9:16
        center_x = width // 2  # Center x of the frame

        x_min = max(0, center_x - target_width // 2)
        x_max = min(width, center_x + target_width // 2)

        cropped_frame = frame[:, x_min:x_max]

        # Super Resolution Upscaling
        start_time = time.time()
        
        # TUDO: Disabe upscaled_frame
        # upscaled_frame = sr_model.upsample(cropped_frame)
        end_time = time.time()
        print(f"Frame {frame_count} cropped: x_min = {x_min}, x_max = {x_max}, elapsed time = {end_time - start_time}")

        out.write(cropped_frame)

    cap.release()
    out.release()
    print("Video cropping and upscaling process completed!")

if __name__ == "__main__":
    input_video_path = "input_video.mp4"  # Path to input video
    output_video_path = "output_cropped_upscaled_video.mp4"  # Path to save cropped and upscaled video
    crop_and_upscale_video(input_video_path, output_video_path)
