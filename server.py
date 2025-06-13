from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__, static_folder='static')
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000", "http://127.0.0.1:8000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/output_glb/<path:path>')
def serve_glb(path):
    return send_from_directory('output_glb', path)

@app.route('/check-motion-file')
def check_motion_file():
    motion_file = os.path.join('output_glb', 'motion.glb')
    exists = os.path.exists(motion_file)
    return jsonify({
        'exists': exists
    })

@app.route('/upload-video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    
    try:
        video = request.files['video']
        if video.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        # Save video file
        upload_folder = 'VideoPose3D/input_video'
        uploaded_files = os.listdir(upload_folder)
        for file in uploaded_files:
            os.remove(os.path.join(upload_folder, file))
        video_path = os.path.join("VideoPose3D/input_video", video.filename)
        video.save(video_path)
        
        # TODO: Add your pose estimation code here
        # result = run_pose_estimation(video_path)
        run_2D_pose_estimation()
        prepare_2D_pose_data()
        run_3D_pose_estimation(video.filename.split('.')[0])
        run_motion_application()

        motion_exists = os.path.exists(os.path.join('output_glb', 'motion.glb'))
        
        return jsonify({
            'success': True,
            'message': 'Video processed successfully',
            'filename': video.filename,
            'motionExists': motion_exists
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_2D_pose_estimation():
    videopose_dir = "VideoPose3D"
    subprocess.run([
        "python", "inference/infer_video_d2.py",
        "--cfg", "COCO-Keypoints/keypoint_rcnn_R_101_FPN_3x.yaml",
        "--output-dir", "output_keypoints/",
        "--image-ext", "mp4",
        "input_video/"
    ], check=True, cwd=videopose_dir)

def prepare_2D_pose_data():
    videopose_dir = "VideoPose3D"
    subprocess.run([
        "python", "data/prepare_data_2d_custom.py",
        "-i", "output_keypoints/",
        "-o", "video"
    ], check=True, cwd=videopose_dir)

def run_3D_pose_estimation(filename):
    videopose_dir = "VideoPose3D"
    subprocess.run([
        "python", "run.py",
        "-d", "custom",
        "-k", "video",
        "-arc", "3,3,3,3,3",
        "-c", "checkpoint",
        "--evaluate", "pretrained_h36m_detectron_coco.bin",
        "--render",
        "--viz-subject", f"{filename}.mp4",
        "--viz-action", "custom",
        "--viz-camera", "0",
        "--viz-video", f"input_video/{filename}.mp4",
        "--viz-output", "output_3D_pose.mp4",
        "--viz-export", "3D_pose",
        "--viz-size", "6"
    ], check=True, cwd=videopose_dir)

def run_motion_application():
    """
    Runs Blender in background mode and executes apply_motion.py.
    """
    subprocess.run([
        "blender", "--background", "--python", "apply_motion.py"
    ], check=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)