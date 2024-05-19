import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from services.crop_view import crop_video_to_center
import json
from ultralytics import YOLO
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

model = YOLO('yolov8s.pt')

def load_object_weights(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

object_weights_file_path = 'assets/object_weights.json'
object_weights = load_object_weights(object_weights_file_path)

def detect_objects(frame, confidence_threshold=0.6):
    results = model(frame)
    boxes = []
    
    for result in results:
        if result.boxes is not None:
            for box in result.boxes:
                confidence = box.conf.item()  

                if confidence > confidence_threshold:
                    label = result.names[int(box.cls.item())]
                    weight = object_weights.get(label, 0.1)
                    xyxy = box.xyxy.cpu().numpy()
                    if len(xyxy) > 0 and len(xyxy[0]) == 4: 
                        boxes.append((xyxy[0], weight))
    return boxes

def compute_scene_center_x(video_clip):
    width = int(video_clip.size[0])
    frame_center_x = width / 2
    first_frame = video_clip.get_frame(0)
    boxes_first_frame = detect_objects(first_frame)
    if len(boxes_first_frame) > 0:
        max_weight_box = max(boxes_first_frame, key=lambda x: x[1])
        box, weight = max_weight_box
        if len(box) == 4:
            center_x_first_frame = np.mean([box[0], box[2]])
        else:
            center_x_first_frame = None
    else:
        center_x_first_frame = None

    if center_x_first_frame is not None:
        return center_x_first_frame

    return frame_center_x

def detect_scenes_pyscenedetect(video_path, output_path):
    video_clip = VideoFileClip(video_path)
    
    # get audio video clip
    # audio = video_clip.audio
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
        cropped_clips.append(cropped_clip)

    final_clip = concatenate_videoclips(cropped_clips)
    final_clip.write_videofile(output_path, fps=video_clip.fps, codec='libx264')

    video_clip.close()

