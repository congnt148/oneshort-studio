# app.py
from flask import Flask, request, url_for, send_file, jsonify
import os
from datetime import datetime
from services.scene_detect import detect_scenes_pyscenedetect

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/crop_video', methods=['POST'])
def crop_video_api():
    if 'video' not in request.files:
        return jsonify(error="No video file provided"), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify(error="No selected file"), 400

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    filename = f"{timestamp}.mp4"
    input_video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    video.save(input_video_path)

    
    output_filename = f"cropped_{timestamp}.mp4"
    output_video_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    try:
        detect_scenes_pyscenedetect(input_video_path, output_video_path)
    except Exception as e:
        return jsonify(error=str(e)), 500
    
    video_final_url = url_for('uploaded_file', filename=output_filename, _external=True)
    video_raw_url = url_for('uploaded_file', filename=filename, _external=True)
    
    return jsonify(video_final_url=video_final_url, video_raw_url=video_raw_url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
