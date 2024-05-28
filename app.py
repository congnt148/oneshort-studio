from flask import Flask, request, url_for, send_file, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from services.scene_detect import detect_scenes_pyscenedetect

app = Flask(__name__)
CORS(app, resources={r"/crop_video": {"origins": "http://localhost:3001"}}) 

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
        return jsonify(status=False, error=str(e)), 500
    
    video_final_url = url_for('uploaded_file', filename=output_filename, _external=True)
    video_raw_url = url_for('uploaded_file', filename=filename, _external=True)
    
    return jsonify(
        status=True, 
        data={
            'videoFinalUrl': video_final_url, 
            'videoRawUrl': video_raw_url
        }
    )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
