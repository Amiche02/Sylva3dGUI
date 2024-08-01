"""
Extract frames from a video.

Author: Stéphane KPOVIESSI
At Sylvagreg company
Big data engineer student
"""

import cv2
from PIL import Image, ImageTk
import os
from pathlib import Path


def create_output_folder(output_dir):
    output_folder = os.path.join(output_dir,'rmbg', 'images')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    return output_folder

def extract_images(path):
    image_formats = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
    images = []

    path = Path(path)
    if not path.exists():
        print(f"The path {path} does not exist.")
        return images

    for file in path.rglob('*'):
        if file.is_file() and file.suffix.lower() in image_formats:
            images.append(str(file))

    return images

def create_thumbnail(image_path, max_size=(100, 100)):
    image = cv2.imread(image_path)
    h, w = image.shape[:2]
    scale = min(max_size[0] / w, max_size[1] / h)
    thumbnail = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    thumbnail = cv2.cvtColor(thumbnail, cv2.COLOR_BGR2RGB)
    return ImageTk.PhotoImage(Image.fromarray(thumbnail))

def create_video_output_folder(output_dir, video_path):
    video_basename = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = os.path.join(output_dir, video_basename, 'images')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    return output_folder

def create_resize_output_folder(input_folder):
    base_folder = os.path.dirname(input_folder)
    output_folder = os.path.join(base_folder, 'resize', 'images')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    return output_folder

def resize_image(image, scale_percent):
    width = int(image.width * scale_percent / 100)
    height = int(image.height * scale_percent / 100)
    resized_image = image.resize((width, height), Image.LANCZOS)
    return resized_image

def process_images(image_paths, scale_percent):
    if not image_paths:
        print("No images to process.")
        return []
    
    input_folder = os.path.dirname(image_paths[0])
    output_folder = create_resize_output_folder(input_folder)
    resized_image_paths = []

    for image_path in image_paths:
        image = Image.open(image_path)
        resized_image = resize_image(image, scale_percent)
        output_image_path = os.path.join(output_folder, os.path.basename(image_path))
        resized_image.save(output_image_path)
        resized_image_paths.append(output_image_path)
        print(f"Processed and saved: {output_image_path}")
    
    return resized_image_paths

def extract_frames(video_path, output_folder, frame_rate):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}.")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    if fps == 0:
        print("Error: Unable to retrieve video FPS.")
        return

    print(f"Video FPS: {fps}")

    interval = int(fps / frame_rate)

    frame_idx = 0
    extracted_frame_idx = 0
    extracted_image_paths = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % interval == 0:
            frame_name = os.path.join(output_folder, f"frame_{extracted_frame_idx:04d}.png")
            cv2.imwrite(frame_name, frame)
            print(f"Extracted frame: {frame_name}")
            extracted_image_paths.append(frame_name)
            extracted_frame_idx += 1

        frame_idx += 1

    cap.release()
    print(f"Extracted {extracted_frame_idx} frames.")
    return extracted_image_paths
