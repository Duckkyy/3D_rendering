# Apply motion to FBX skeleton using rotation_quaternion
import bpy
import numpy as np
import mathutils
import os

# === Config paths ===
fbx_path = os.path.abspath("X_Bot.fbx")
motion_path = os.path.abspath("3D_pose.npy")
output_path = os.path.abspath("output_glb/motion.glb")

# === Clear scene and import FBX ===
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx_path)

armature = next((obj for obj in bpy.data.objects if obj.type == 'ARMATURE'), None)
if not armature:
    raise RuntimeError("Armature not found")

bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

# === Load motion ===
motion = np.load(motion_path)  # shape: (frames, 17, 3)
num_frames = motion.shape[0]
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = num_frames

# === Bone mapping (OpenPose 17-keypoints to Mixamo bones, child -> parent structure) ===
bone_pairs = [
    # Right arm chain
    ("mixamorig:RightForeArm", "mixamorig:RightArm", 4, 3, (1, 0, 0)),
    ("mixamorig:RightArm", "mixamorig:RightShoulder", 3, 2, (1, 0, 0)),
    # Left arm chain  
    ("mixamorig:LeftForeArm", "mixamorig:LeftArm", 7, 6, (-1, 0, 0)),
    ("mixamorig:LeftArm", "mixamorig:LeftShoulder", 6, 5, (-1, 0, 0)),
    # Right leg chain
    ("mixamorig:RightLeg", "mixamorig:RightUpLeg", 10, 9, (0, -1, 0)),
    ("mixamorig:RightUpLeg", "mixamorig:Hips", 9, 8, (0, -1, 0)),
    # Left leg chain
    ("mixamorig:LeftLeg", "mixamorig:LeftUpLeg", 13, 12, (0, -1, 0)), 
    ("mixamorig:LeftUpLeg", "mixamorig:Hips", 12, 11, (0, -1, 0)),
    # Spine chain
    ("mixamorig:Spine", "mixamorig:Hips", 1, 0, (0, 1, 0)),
    ("mixamorig:Spine1", "mixamorig:Spine", 1, 1, (0, 1, 0)),
    ("mixamorig:Spine2", "mixamorig:Spine1", 1, 1, (0, 1, 0)),
    ("mixamorig:Neck", "mixamorig:Head", 1, 0, (0, 1, 0)),
]

# === Scale motion to match FBX height ===
motion_y = motion[:, :, 1]
motion_height = np.max(motion_y[:, 0]) - np.min(motion_y[:, 13])
model_height = armature.dimensions[2]
scale_factor = model_height / motion_height
print(f"Scale factor: {scale_factor:.3f}")

# === Apply rotation_quaternion ===
for frame in range(num_frames):
    bpy.context.scene.frame_set(frame)
    for bone_name, parent_name, idx_child, idx_parent, rest_dir in bone_pairs:
        if bone_name not in armature.pose.bones:
            continue
            
        child_pos = motion[frame, idx_child] * scale_factor
        parent_pos = motion[frame, idx_parent] * scale_factor
        
        # Tính vector chuyển động
        motion_vec = mathutils.Vector(child_pos - parent_pos)
        if motion_vec.length > 0.001:
            motion_vec.normalize()
            
            # Sử dụng rest_dir tương ứng cho từng bone
            rest_vec = mathutils.Vector(rest_dir)
            quat = rest_vec.rotation_difference(motion_vec)
            
            pose_bone = armature.pose.bones[bone_name]
            pose_bone.rotation_mode = 'QUATERNION'
            
            # Áp dụng rotation với damping để smooth hơn
            alpha = 0.7  # Damping factor
            current_rot = pose_bone.rotation_quaternion.copy()
            pose_bone.rotation_quaternion = current_rot.slerp(quat, alpha)
            pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

# === Export GLB ===
bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
print(f"Exported animated GLB to {output_path}")
