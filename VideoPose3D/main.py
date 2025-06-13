import subprocess

# Step 1: Extract 2D keypoints from video
subprocess.run([
    "python", "inference/infer_video_d2.py",
    "--cfg", "COCO-Keypoints/keypoint_rcnn_R_101_FPN_3x.yaml",
    "--output-dir", "output_keypoints/",
    "--image-ext", "mp4",
    "input_video/"
], check=True)

# Step 2: Prepare 2D data
subprocess.run([
    "python", "data/prepare_data_2d_custom.py",
    "-i", "output_keypoints/",
    "-o", "yoga"
], check=True)

# Step 3: Run 3D pose estimation and rendering
subprocess.run([
    "python", "run.py",
    "-d", "custom",
    "-k", "yoga",
    "-arc", "3,3,3,3,3",
    "-c", "checkpoint",
    "--evaluate", "pretrained_h36m_detectron_coco.bin",
    "--render",
    "--viz-subject", "yoga.mp4",
    "--viz-action", "custom",
    "--viz-camera", "0",
    "--viz-video", "input_video/yoga.mp4",
    "--viz-output", "output_3D_pose.mp4",
    "--viz-export", "3D_pose",
    "--viz-size", "6"
], check=True)