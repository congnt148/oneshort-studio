from tkinter import filedialog
from models.yolo_model import YOLOModel
from models.video_processor import VideoProcessor
from models.frame_item import FrameItem


class MainPresenter:
    def __init__(self, view):
        self.view = view
        self.yolo_model = YOLOModel()
        self.video_processor = VideoProcessor(self.yolo_model, self.view)
        self.input_video_path = ""

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("MOV files", "*.mov")])
        if file_path:
            self.input_video_path = file_path
            self.process_timeline_frames()
            # Tạo và khởi chạy các luồng xử lý
            # threading.Thread(target=self.process_timeline_frames).start()
            # threading.Thread(target=self.process_video).start()
            # frame_items = self.extract_frames()
            
    def process_timeline_frames(self):
        # Xử lý trích xuất khung hình và hiển thị trên timeline
        frame_items = self.extract_frames()
        self.view.display_frames_in_timeline(frame_items)
        self.view.display_frame_list(frame_items)

    def process_video(self):
        # Xử lý hiển thị video
        self.view.display_video(self.input_video_path)
            
    def extract_frames(self):
        if self.input_video_path:
            frame_items = self.video_processor.extract_frames(self.input_video_path)
            return frame_items  # Trả về frame_items
        else:
            return []
