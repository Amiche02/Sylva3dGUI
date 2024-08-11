import os
import argparse
from rembg import remove
from PIL import Image

def process_image(input_path, output_path):
    try:
        input_image = Image.open(input_path)
        output_image = remove(input_image)
        output_image.save(output_path, format='PNG')  # Save as PNG to support RGBA
        print(f"Processed and saved: {output_path}")
    except Exception as e:
        print(f"Failed to process {input_path}: {e}")

def process_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'tiff')):
            input_image_path = os.path.join(input_folder, file_name)
            output_image_path = os.path.join(output_folder, f"rm_{file_name.split('.')[0]}.png")
            process_image(input_image_path, output_image_path)

def main():
    parser = argparse.ArgumentParser(description="Remove background from images in a folder.")
    parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing input images.")
    parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder to save output images.")
    
    args = parser.parse_args()
    process_images(args.input_folder, args.output_folder)

if __name__ == "__main__":
    main()
