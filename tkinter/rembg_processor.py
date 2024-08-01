import os
from rembg import remove
from PIL import Image
from utils import create_output_folder

def process_image(input_path, output_path):
    try:
        input_image = Image.open(input_path)
        output_image = remove(input_image)
        output_image.save(output_path, format='PNG')
        print(f"Processed and saved: {output_path}")
    except Exception as e:
        print(f"Failed to process {input_path}: {e}")

def remove_background_rembg(input_folder, output_folder):
    output_folder = create_output_folder(output_folder)
    
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'tiff')):
            input_image_path = os.path.join(input_folder, file_name)
            output_image_path = os.path.join(output_folder, f"rm_{file_name.split('.')[0]}.png")
            process_image(input_image_path, output_image_path)
