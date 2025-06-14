# Computer Rendering

## Set up environment

1. Install node and Three.js
   - Install [node](https://nodejs.org/en)
   - Install three.js
    ```bash
    npm install --save three
    ```

2. Create conda environment
   ```bash
   git clone https://github.com/Duckkyy/3D_rendering.git
   cd 3D_rendering
   
   conda create -n 3D_rendering python=3.9
   conda activate 3D_rendering
   pip install -r requirements.txt
   ```

3. Install Detectron2
   ```bash
   git clone https://github.com/facebookresearch/detectron2.git
   python -m pip install -e detectron2
   ```
   Follow [Detectron2 Installation](https://detectron2.readthedocs.io/en/latest/tutorials/install.html) for more information.

4. Download checkpoint for 3D pose estimation
   ```bash
   cd VideoPose3D
   mkdir checkpoints && cd checkpoints
   ```
   Download the [pretrained model](https://dl.fbaipublicfiles.com/video-pose-3d/pretrained_h36m_detectron_coco.bin).


## Run demo
   In 3D_rendering folder, run command
   ```bash
   python server.py
   ```


## Folder structure
   ```
   3D_rendering
   ├── VideoPose3D
   │   ├── main.py
   ├── X_Bot.fbx
   ├── apply_motion.py
   ├── output_glb
   │   └── model.glb
   ├── server.py
   ├── static
   │   ├── css
   │   ├── index.html
   └── requirements.txt
   ```

   Note for my repo

   - First of all static folder (with index.html and css inside) is where I render my website by using Three.js and Flask
   - output_glb is a folder to save model.glb which is the file I used for rendering standing model. After running 3D pose estimation, it will create motion.glb file inside and I can render the model with motion.
   - VideoPose3D is a module in python to extract motion from an input video, then create .npy file contains motion and an output video
   - apply_motion.py helps me combine the motion to model (which is not accuracy). This file uses X_Bot.fbx (model) and .npy file created by VideoPose3D (motion) for applying motion
