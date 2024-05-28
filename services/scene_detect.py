from datetime import datetime
import os
import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip

from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from moviepy.editor import AudioFileClip
from moviepy.video.fx.all import crop
import json
from ultralytics import YOLO
from scipy.optimize import curve_fit
import cv2

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

def compute_scene_center_x(frame):
    width = int(frame.shape[1])
    frame_center_x = width / 2
    boxes = detect_objects(frame)
    if len(boxes) > 0:
        max_weight_box = max(boxes, key=lambda x: x[1])
        box, weight = max_weight_box
        if len(box) == 4:
            center_x = np.mean([box[0], box[2]])
        else:
            center_x = None
    else:
        center_x = None

    if center_x is not None:
        return center_x

    return frame_center_x

def poly_fit(x, a, b, c):
    return a * x ** 2 + b * x + c

def smooth_center_x_values(center_x_values):
    x = np.arange(len(center_x_values))
    y = np.array(center_x_values)
    popt, _ = curve_fit(poly_fit, x, y)
    smoothed_values = poly_fit(x, *popt)
    return smoothed_values

def crop_frame(frame, center_x, aspect_ratio=9/16):
    height = frame.shape[0]
    new_width = height * aspect_ratio

    left = max(0, center_x - new_width / 2)
    right = min(frame.shape[1], center_x + new_width / 2)

    if right - left < new_width:
        if left == 0:
            right = new_width
        else:
            left = frame.shape[1] - new_width

    cropped_frame = frame[:, int(left):int(right)]
    return cropped_frame


def crop_clip(video_clip, center_x):
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

def write_video(frames, output_video, fps):
    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    for frame in frames:
        out.write(frame) 
        
    out.release()
    
def crop_video_to_center(subclip, fps):
    center_x_values = []
    duration = subclip.duration
    for t in np.arange(0, duration, 1):
        frame = subclip.get_frame(t)
        center_x = compute_scene_center_x(frame)
        center_x_values.append(center_x)
        
    smoothed_center_x_values = smooth_center_x_values(center_x_values)    
    
    total_frames = int(duration * fps)
    all_center_x_values = np.interp(
        np.linspace(0, len(smoothed_center_x_values) - 1, total_frames),
        np.arange(len(smoothed_center_x_values)),
        smoothed_center_x_values
    )
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_video_path = f"temp_video_{timestamp}.mp4"
    subclip.write_videofile(temp_video_path, fps=fps)
    
    cap = cv2.VideoCapture(temp_video_path)
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    target_width = int(height * (9 / 16))
    frames = []
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        center_x = 0
        if(frame_count < all_center_x_values.size):
            center_x = all_center_x_values[frame_count]
        else:
            center_x = all_center_x_values[all_center_x_values.size - 1]
        
        x_min = int(max(0, center_x - target_width // 2))
        x_max = int(min(width, center_x + target_width // 2))
        cropped_frame = frame[:, x_min:x_max]
        cropped_frame_resized = cv2.resize(cropped_frame, (target_width, height))
        frame_count += 1
        frames.append(cropped_frame_resized)
    
    cap.release()
    os.remove(temp_video_path)
    return frames

def add_audio_to_video(video_path, audio_path, output_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    final_video = video.set_audio(audio)
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

def detect_scenes_pyscenedetect(video_path, output_path):
    video_clip = VideoFileClip(video_path)

    audio = video_clip.audio
    fps = video_clip.fps
    
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    
    scene_list = scene_manager.get_scene_list()
    all_frames = []
    
    if not scene_list:
        frames = crop_video_to_center(video_clip, fps)
        all_frames.extend(frames)
    else:
        for i, (start_frame, end_frame) in enumerate(scene_list):
            subclip = video_clip.subclip(start_frame.get_seconds(), end_frame.get_seconds())
            frames = crop_video_to_center(subclip, fps)
            all_frames.extend(frames)
        
    temp_video_path = 'temp_video.mp4'
    write_video(all_frames, temp_video_path, fps)
    video_clip.close()
    add_audio_to_video(temp_video_path, video_path, output_path)
    
    os.remove(temp_video_path)
    video_clip.close()