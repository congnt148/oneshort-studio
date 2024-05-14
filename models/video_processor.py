import cv2

class VideoProcessor:
    def __init__(self, yolo_model):
        self.yolo_model = yolo_model

    def crop_video(self, input_path, output_path):
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print("Error: Could not open input video.")
            return
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        video_height = height
        target_width = int(video_height * (9 / 16))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, video_height))

        if not out.isOpened():
            print("Error: Could not open output video for writing.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            boxes = self.yolo_model.detect_objects(frame)
            center_x = width // 2
            x_min = max(0, center_x - target_width // 2)
            x_max = min(width, center_x + target_width // 2)
            cropped_frame = frame[:, x_min:x_max]
            cropped_frame_resized = cv2.resize(cropped_frame, (target_width, video_height))
            out.write(cropped_frame_resized)

        cap.release()
        out.release()
        print("Video cropping process completed!")
