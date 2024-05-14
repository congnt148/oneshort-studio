import os
from tkinter import filedialog
from models.yolo_model import YOLOModel
from models.video_processor import VideoProcessor

class MainPresenter:
    def __init__(self, view):
        self.view = view
        self.yolo_model = YOLOModel()
        self.video_processor = VideoProcessor(self.yolo_model)
        self.input_video_path = ""

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*"), ("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("MOV files", "*.mov")])
        if file_path:
            self.input_video_path = file_path
            self.view.show_video(file_path)

    def start_crop(self):
        if self.input_video_path:
            output_path = os.path.splitext(self.input_video_path)[0] + "_cropped.mp4"
            self.video_processor.crop_video(self.input_video_path, output_path)
            print(f"Output saved to {output_path}")
