from flask import Flask, request, url_for, send_file, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from services.scene_detect import detect_scenes_pyscenedetect

app = Flask(__name__)
CORS(app, resources={r"/crop_video": {"origins": "http://localhost:3001"}}) 

UPLOAD_FOLDER = 'uploads'
IMAGE_FOLDER = 'images'
FINAL_FOLDER = 'finals'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['FINAL_FOLDER'] = FINAL_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)
    
if not os.path.exists(FINAL_FOLDER):
    os.makedirs(FINAL_FOLDER)

@app.route('/crop_video', methods=['POST'])
def crop_video_api():
    if 'video' not in request.files:
        return jsonify(error="No video file provided"), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify(error="No selected file"), 400

    project_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    filename = f"{project_id}.mp4"
    input_video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    video.save(input_video_path)

    
    output_filename = f"cropped_{project_id}.mp4"
    output_video_path = os.path.join(app.config['FINAL_FOLDER'], output_filename)
    image_folder = os.path.join(app.config['IMAGE_FOLDER'], project_id)
    os.makedirs(image_folder, exist_ok=True)
    
    try:
        detect_scenes_pyscenedetect(input_video_path, output_video_path, image_folder, project_id)
    except Exception as e:
        return jsonify(status=False, error=str(e)), 500
    
    video_final_url = url_for('finaled_file', filename=output_filename, _external=True)
    video_raw_url = url_for('uploaded_file', filename=filename, _external=True)
    
    return jsonify(
        status=True, 
        data={
            'videoFinalUrl': video_final_url, 
            'videoRawUrl': video_raw_url,
        }
    )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/finals/<filename>')
def finaled_file(filename):
    return send_file(os.path.join(app.config['FINAL_FOLDER'], filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
