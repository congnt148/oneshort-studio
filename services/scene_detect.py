import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
import cv2
from services.audio import add_audio_to_video
from services.crop_view import crop_video_to_center
from concurrent.futures import ThreadPoolExecutor

def write_video(frames, output_video, fps):
    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    for frame in frames:
        out.write(frame) 
        
    out.release()

def detect_scenes_pyscenedetect(video_path, output_path, image_folder, project_id):
    video_clip = VideoFileClip(video_path)

    fps = video_clip.fps
    
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    
    scene_list = scene_manager.get_scene_list()
    all_frames = []
    
    if not scene_list:
        frames = crop_video_to_center(video_clip, fps, project_id)
        all_frames.extend(frames)
    else:
        for i, (start_frame, end_frame) in enumerate(scene_list):
            subclip = video_clip.subclip(start_frame.get_seconds(), end_frame.get_seconds())
            frames = crop_video_to_center(subclip, fps, project_id)
            all_frames.extend(frames)
        # def process_scene(scene):
        #     start_frame, end_frame = scene
        #     subclip = video_clip.subclip(start_frame.get_seconds(), end_frame.get_seconds())
        #     return crop_video_to_center(subclip, fps, project_id)

        # with ThreadPoolExecutor() as executor:
        #     frames_list = list(executor.map(process_scene, scene_list))
        
        # for frames in frames_list:
        #     all_frames.extend(frames)
        
    temp_video_path = 'temp_video.mp4'
    write_video(all_frames, temp_video_path, fps)
    video_clip.close()
    add_audio_to_video(temp_video_path, video_path, output_path)
    
    os.remove(temp_video_path)
    video_clip.close()
