from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech
from moviepy.editor import VideoFileClip
import pysrt
import srt
import os
from datetime import timedelta
from googletrans import Translator
from flask import url_for

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
    
def convert_srt_to_webvtt(srt_file_path, webvtt_file_path):
    with open(srt_file_path, 'r', encoding='utf-8') as srt_file:
        srt_content = srt_file.readlines()
    
    with open(webvtt_file_path, 'w', encoding='utf-8') as webvtt_file:
        webvtt_file.write("WEBVTT\n\n")
        for line in srt_content:
            webvtt_file.write(line.replace(',', '.'))

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

def get_subtitle(input_video_path, project_id, subtitle_folder):
    
    audio_path = f"{project_id}.wav"
    video_clip = VideoFileClip(input_video_path)
    audio_clip = video_clip.audio
    
    audio_clip.write_audiofile(audio_path)
    
    convert_to_mono(audio_path)
    
    transcript = transcribe_audio(audio_path)
    
    srt_vi_path = os.path.join(subtitle_folder, f"{project_id}_subtitles_vi.srt")
    srt_en_path = os.path.join(subtitle_folder, f"{project_id}_subtitles_en.srt")

    create_srt_file(transcript, srt_vi_path)
    translate_srt_file(srt_vi_path, srt_en_path)
    os.remove(audio_path)
    
    webvtt_vi_path = os.path.join(subtitle_folder, f"{project_id}_subtitles_vi.vtt")
    webvtt_en_path = os.path.join(subtitle_folder, f"{project_id}_subtitles_en.vtt")

    convert_srt_to_webvtt(srt_vi_path, webvtt_vi_path)
    convert_srt_to_webvtt(srt_en_path, webvtt_en_path)
    
    srt_vi_final = url_for('subtitles_file', filename=os.path.basename(srt_vi_path), _external=True)
    srt_en_final = url_for('subtitles_file', filename=os.path.basename(srt_en_path), _external=True)
    webvtt_vi_final = url_for('subtitles_file', filename=os.path.basename(webvtt_vi_path), _external=True)
    webvtt_en_final = url_for('subtitles_file', filename=os.path.basename(webvtt_en_path), _external=True)
    
    return {
        'srt': [
        {"src": srt_vi_final, "srcLang": 'vi', "label": 'Việt Nam'},
        {"src": srt_en_final, "srcLang": 'en', "label": 'English'}
    ],
        'vtt': [
        {"src": webvtt_vi_final, "srcLang": 'vi', "label": 'Việt Nam'},
        {"src": webvtt_en_final, "srcLang": 'en', "label": 'English'}
    ]
    }
    