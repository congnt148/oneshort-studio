import cv2
import numpy as np
from ultralytics import YOLO
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import translate_v2 as translate
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip, AudioFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
import pysrt
import os
import srt
from datetime import timedelta
import subprocess
from pysrt import open as open_srt

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

def create_srt_file(transcript, srt_file_path):
    subs = []
    for i, result in enumerate(transcript.results):
        if result.alternatives and result.alternatives[0].words:
            start_time_seconds = result.alternatives[0].words[0].start_time.total_seconds()
            end_time_seconds = result.alternatives[0].words[-1].end_time.total_seconds()
            start_time = timedelta(seconds=start_time_seconds)
            end_time = timedelta(seconds=end_time_seconds)
        else:
            start_time = end_time = timedelta(0)
        subs.append(srt.Subtitle(i, start_time, end_time, result.alternatives[0].transcript))

    with open(srt_file_path, "w") as srt_file:
        srt_file.write(srt.compose(subs))
        
    # Khởi tạo dịch vụ Google Translate
    translate_client = translate.Client()
    # Mở file phụ đề
    subs = open_srt(srt_file_path)
    # Dịch từng dòng phụ đề
    for sub in subs:
        result = translate_client.translate(sub.text, target_language='en')
        sub.text = result['translatedText']
    # Lưu phụ đề đã dịch
    translated_srt_file_path = 'translated_subtitles.srt'
    subs.save(translated_srt_file_path, encoding='utf-8')
    

def add_subtitles_to_video(video_path, srt_file_path, output_path, audio_file):
    temp_output_path = "temp_output.mp4"
    command = f"ffmpeg -i {video_path} -i {audio_file} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {temp_output_path}"
    subprocess.run(command, shell=True, check=True)
    # Now rename the temporary output file to the final output file
    os.rename(temp_output_path, video_path)
    video = VideoFileClip(video_path)
    audio = AudioFileClip(video_path)  # Create an audio clip from the original video
    subtitles = pysrt.open(srt_file_path)
    print(f"Loaded {len(subtitles)} subtitles from {srt_file_path}")

    if not subtitles:
        print("No subtitles found, skipping subtitle addition.")
        video.write_videofile(output_path, codec='libx264', fps=video.fps, audio_codec='aac')
        return
    
    generator = lambda txt: TextClip(txt, font='Arial', fontsize=24, color='white')
    subtitles_clip = SubtitlesClip(srt_file_path, generator)

    video_with_subtitles = CompositeVideoClip([video.set_audio(audio), subtitles_clip.set_position(('center', 'bottom'))])  # Set the audio of the video

    video_with_subtitles.write_videofile(output_path, codec='libx264', fps=video.fps, audio_codec='aac')  # Make sure to specify an audio codec
   


def crop_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Could not open input video.")
        return
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

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
        detect_objects(frame)
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
    create_srt_file(transcript, srt_file_path)
    add_subtitles_to_video(temp_video_path, srt_file_path, output_path, audio_path)
   
    # os.remove(audio_path)
    # os.remove(temp_video_path)
    print("Video cropping process completed!")

if __name__ == "__main__":
    input_video_path = "input_video.mp4"
    output_video_path = "output_cropped_video.mp4"
    crop_video(input_video_path, output_video_path)

