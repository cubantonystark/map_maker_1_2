import bpy
import os
import sys

# Function to render top view and save the image
def render_top_view(obj_file):
    # Clear existing data
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import the OBJ file
    bpy.ops.import_scene.obj(filepath=obj_file)

    # Set render resolution and format
    bpy.context.scene.render.resolution_x = 800
    bpy.context.scene.render.resolution_y = 800
    bpy.context.scene.render.image_settings.file_format = 'PNG'

    # Set camera to top view
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='CAMERA')
    bpy.ops.object.delete()
    bpy.ops.object.camera_add(location=(0, 0, 10))
    bpy.context.object.rotation_euler = (1.5708, 0, 0)  # Rotate 90 degrees (top view)

    # Set output path
    output_path = obj_file.replace(".obj", "_top_view.png")
    bpy.context.scene.render.filepath = output_path

    # Render the image
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.quit_blender()

    print(f"Generated image for {obj_file}")

# Function to process .obj files in a folder
def process_obj_files(folder_path):
    # Ensure the folder path is valid
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid folder.")
        return

    # List all .obj files in the folder
    obj_files = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.endswith(".obj")]

    if not obj_files:
        print("No .obj files found in the folder.")
        return

    # Initialize Blender in background mode
    bpy.ops.wm.blender_quit()
    bpy.ops.wm.blender_background()

    # Process each .obj file
    for obj_file in obj_files:
        render_top_view(obj_file)


if __name__ == "__main__":

    folder_path = "C:/Users/micha/Apps/MapMaker6/map_maker_1_2/ARTAK_MM/POST/Photogrammetry/NIWIC/Productions/Production_1 (20)/Data/Model"
    process_obj_files(folder_path)