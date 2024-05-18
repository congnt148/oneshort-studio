import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.all import crop
import json
from ultralytics import YOLO
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

# Khởi tạo mô hình YOLO
model = YOLO('yolov8s.pt')

def load_object_weights(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
object_weights_file_path = 'assets/object_weights.json'
object_weights = load_object_weights(object_weights_file_path)
    
def detect_objects(frame, confidence_threshold=0.7):
    # results = model(frame)
    # boxes = []
    # confidences = []
    # weights = []
    # for result in results:
    #     if result.boxes is not None:
    #         for box in result.boxes:
    #             conf = box.conf.item()
    #             if conf >= confidence_threshold:
    #                 class_name = result.names[box.cls.item()]
    #                 boxes.append(box.xyxy.cpu().numpy())
    #                 confidences.append(conf)
    #                 weights.append(object_weights.get(class_name, 0))
    # return np.array(boxes), np.array(confidences), np.array(weights)
    
    results = model(frame)
    boxes = []
    for result in results:
        if result.boxes is not None:
            for box in result.boxes.xyxy:
                confidence = box.conf.item()  # Trích xuất giá trị confidence
                if confidence > confidence_threshold:  
                    label = result.names[int(box.cls.item())]
                    weight = object_weights.get(label, 0.1) 
                    boxes.append((box.xyxy.cpu().numpy(), weight))
    return boxes

def compute_scene_center_x(video_clip):
    width = int(video_clip.size[0])  
    frame_center_x = width / 2
    first_frame = video_clip.get_frame(0)
    boxes_first_frame = detect_objects(first_frame)
    if len(boxes_first_frame) > 0:
        max_weight_box = max(boxes_first_frame, key=lambda x: x[1])
        box, weight = max_weight_box
        center_x_first_frame = np.mean([box[0], box[2]])
    else:
        center_x_first_frame = None

    if center_x_first_frame is not None:
        return center_x_first_frame

    return frame_center_x

def crop_video_to_center(video_clip, center_x):
    height = video_clip.size[1]
    new_width = height * 9 / 16

    left = max(0, center_x - new_width / 2)
    right = min(video_clip.size[0], center_x + new_width / 2)

    if right - left < new_width:
        if left == 0:
            right = new_width
        else:
            left = video_clip.size[0] - new_width

    cropped_clip = crop(video_clip, x1=left, x2=right, y1=0, y2=height)
    return cropped_clip

def detect_scenes_pyscenedetect(video_path, output_path):
    video_clip = VideoFileClip(video_path)
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())

    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)

    scene_list = scene_manager.get_scene_list()
    cropped_clips = []

    for i, (start_frame, end_frame) in enumerate(scene_list):
        subclip = video_clip.subclip(start_frame.get_seconds(), end_frame.get_seconds())
        center_x = compute_scene_center_x(subclip)
        cropped_clip = crop_video_to_center(subclip, center_x)
        # cropped_clips.append(subclip)
        output_path_1 = f'scene_{i+1}_cropped.mp4'
        cropped_clip.write_videofile(output_path_1)
        # output_path_1 = f'scene_{i+1}_cropped.mp4'
        # cropped_clip.write_videofile(output_path_1)


    # final_clip = concatenate_videoclips(cropped_clips)
    # final_clip.write_videofile(output_path)

    video_clip.close()

video_path = 'input_video.mp4'
output_path = 'input_video_crop.mp4'
detect_scenes_pyscenedetect(video_path, output_path)
