import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO('yolov8s.pt')  # Load YOLOv8 model, you can replace 'yolov8s.pt' with other model variants if needed

def detect_objects(frame):
    results = model(frame)
    # Extract bounding box coordinates
    boxes = []
    for result in results:
        if result.boxes is not None:
            for box in result.boxes.xyxy:
                boxes.append(box.cpu().numpy())
    return np.array(boxes)

def crop_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Could not open input video.")
        return
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total frames in video

    # Save the height of the video
    video_height = height

    # Calculate the target width to maintain aspect ratio 9:16 (vertical video)
    target_width = int(video_height * (9 / 16))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, video_height))

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

        # Resize cropped frame to match desired dimensions (720x405)
        cropped_frame_resized = cv2.resize(cropped_frame, (target_width, video_height))

        out.write(cropped_frame_resized)
        print(f"Frame {frame_count} cropped and written: x_min = {x_min}, x_max = {x_max}")

    cap.release()
    out.release()
    print("Video cropping process completed!")

if __name__ == "__main__":
    input_video_path = "input_video.mp4"  # Path to input video
    output_video_path = "output_cropped_video.mp4"  # Path to save cropped video
    crop_video(input_video_path, output_video_path)
