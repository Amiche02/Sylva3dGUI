import os
import argparse
from PIL import Image

def resize_image(image, scale_percent):
    """
    Resize an image by a given percentage while maintaining the aspect ratio.

    Parameters:
    image (PIL.Image.Image): The input image.
    scale_percent (int): The percentage to scale the image.

    Returns:
    PIL.Image.Image: The resized image.
    """
    width = int(image.width * scale_percent / 100)
    height = int(image.height * scale_percent / 100)
    resized_image = image.resize((width, height), Image.LANCZOS)
    return resized_image

def create_output_folder(input_folder):
    """
    Create the output folder for resized images.

    Parameters:
    input_folder (str): Path to the input folder.

    Returns:
    str: Path to the newly created output folder.
    """
    base_folder = os.path.dirname(input_folder)
    output_folder = os.path.join(base_folder, 'resize', 'images')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    return output_folder

def process_images(input_folder, scale_percent):
    """
    Process all images in the input folder and save the resized images in the output folder.

    Parameters:
    input_folder (str): Path to the input folder containing images.
    scale_percent (int): The percentage to scale the images.
    """
    output_folder = create_output_folder(input_folder)

    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'tiff')):
            input_image_path = os.path.join(input_folder, file_name)
            image = Image.open(input_image_path)
            resized_image = resize_image(image, scale_percent)
            output_image_path = os.path.join(output_folder, file_name)
            resized_image.save(output_image_path)
            print(f"Processed and saved: {output_image_path}")

def main():
    parser = argparse.ArgumentParser(description="Resize images in a folder.")
    parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing input images.")
    parser.add_argument("--scale_percent", type=int, required=True, help="Percentage to scale the images.")
    
    args = parser.parse_args()
    
    process_images(args.input_folder, args.scale_percent)

if __name__ == "__main__":
    main()
