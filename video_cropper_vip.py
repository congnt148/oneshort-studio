import cv2
import numpy as np
from ultralytics import YOLO
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip, AudioFileClip
import pysrt
import srt
import os
from datetime import timedelta
import subprocess
from googletrans import Translator

# Load YOLOv8 model
model = YOLO('yolov8s.pt')

def detect_objects(frame):
    results = model(frame)
    boxes = []
    for result in results:
        if result.boxes is not None:
            for box in result.boxes.xyxy:
                boxes.append(box.cpu().numpy())
    return np.array(boxes)

def convert_to_mono(audio_path):
    sound = AudioSegment.from_wav(audio_path)
    sound = sound.set_channels(1).set_frame_rate(16000)
    sound.export(audio_path, format="wav")

def transcribe_audio(audio_path, language_code="vi-VI"):
    client = speech.SpeechClient()
    with open(audio_path, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code=language_code,
        enable_word_time_offsets=True
    )
    response = client.recognize(config=config, audio=audio)
    return response

def translate_srt_file(input_srt_path, output_srt_path, target_language='en'):
    translator = Translator()
    subs = pysrt.open(input_srt_path)

    for sub in subs:
        translated_text = translator.translate(sub.text, dest=target_language).text
        sub.text = translated_text

    subs.save(output_srt_path)

def create_srt_file(transcript, srt_file_path):
    subs = []
    words = transcript.results[0].alternatives[0].words
    word_count = len(words)
    words_per_subtitle = 5

    for i in range(0, word_count, words_per_subtitle):
        subtitle_text = ' '.join(word.word for word in words[i:i + words_per_subtitle])
        
        start_time = words[i].start_time
        end_time = words[min(i + words_per_subtitle - 1, word_count - 1)].end_time
        
        start_time_seconds = start_time.total_seconds()
        end_time_seconds = end_time.total_seconds()
        
        subs.append(srt.Subtitle(index=len(subs) + 1, start=timedelta(seconds=start_time_seconds), end=timedelta(seconds=end_time_seconds), content=subtitle_text))

    with open(srt_file_path, "w", encoding="utf-8") as srt_file:
        srt_file.write(srt.compose(subs))

def add_subtitles_to_video(video_path, srt_file_path_vi, srt_file_path_en, output_path, audio_file):
    temp_output_path = "temp_output.mp4"
    command = f"ffmpeg -i {video_path} -i {audio_file} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {temp_output_path}"
    subprocess.run(command, shell=True, check=True)
    os.rename(temp_output_path, video_path)
    
    video = VideoFileClip(video_path)
    audio = AudioFileClip(video_path)
    subtitles_vi = pysrt.open(srt_file_path_vi)
    subtitles_en = pysrt.open(srt_file_path_en)
    print(f"Loaded {len(subtitles_vi)} Vietnamese subtitles from {srt_file_path_vi}")
    print(f"Loaded {len(subtitles_en)} English subtitles from {srt_file_path_en}")

    if not subtitles_vi and not subtitles_en:
        print("No subtitles found, skipping subtitle addition.")
        video.write_videofile(output_path, codec='libx264', fps=video.fps, audio_codec='aac')
        return

    generator = lambda txt: TextClip(txt, font='Arial', fontsize=24, color='white')
    subtitles_clips_vi = []
    subtitles_clips_en = []
    for sub in subtitles_vi:
        text_clip = generator(sub.text)
        start_seconds = sub.start.ordinal / 1000
        duration = (sub.end - sub.start).ordinal / 1000
        text_clip = text_clip.set_duration(duration).set_start(start_seconds)
        text_clip = text_clip.set_position(('center', 50))  # set position to top without margin
        subtitles_clips_vi.append(text_clip)

    for sub in subtitles_en:
        text_clip = generator(sub.text)
        start_seconds = sub.start.ordinal / 1000
        duration = (sub.end - sub.start).ordinal / 1000
        text_clip = text_clip.set_duration(duration).set_start(start_seconds)
        text_clip = text_clip.set_position(('center', 'bottom'))  # adjust position to bottom
        subtitles_clips_en.append(text_clip)

    final_clip = CompositeVideoClip([video.set_audio(audio)] + subtitles_clips_vi + subtitles_clips_en)
    final_clip.write_videofile(output_path, codec='libx264', fps=video.fps, audio_codec='aac')
    
def crop_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Could not open input video.")
        return
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    target_width = int(height * (9 / 16))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_video_path = "temp_video.mp4"
    out = cv2.VideoWriter(temp_video_path, fourcc, fps, (target_width, height))

    if not out.isOpened():
        print("Error: Could not open output video for writing.")
        return

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        center_x = width // 2
        x_min = max(0, center_x - target_width // 2)
        x_max = min(width, center_x + target_width // 2)
        cropped_frame = frame[:, x_min:x_max]
        cropped_frame_resized = cv2.resize(cropped_frame, (target_width, height))
        out.write(cropped_frame_resized)
        print(f"Frame {frame_count} cropped and written: x_min = {x_min}, x_max = {x_max}")

    cap.release()
    out.release()

    audio_path = "audio.wav"
    video_clip = VideoFileClip(input_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path)

    convert_to_mono(audio_path)
    transcript = transcribe_audio(audio_path)
    srt_file_path = "subtitles.srt"
    srt_translate_file_path = "subtitles_translate.srt"
    create_srt_file(transcript, srt_file_path)
    translate_srt_file(srt_file_path, srt_translate_file_path)
    # add_subtitles_to_video(temp_video_path, srt_file_path, srt_translate_file_path, output_path, audio_path)
   
    os.remove(audio_path)
    os.remove(temp_video_path)
    os.remove(srt_file_path)
    os.remove(srt_translate_file_path)
    print("Video cropping process completed!")

if __name__ == "__main__":
    input_video_path = "input_video.mp4"
    output_video_path = "output_cropped_video.mp4"
    crop_video(input_video_path, output_video_path)
