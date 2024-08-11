"""
Extract frames from a video.

Author: Stéphane KPOVIESSI
At Sylvagreg company
Big data engineer student
"""

import cv2
import os

def create_output_folder(output_dir, video_path):
    """
    Create a directory for storing frames, named after the basename of the video file.

    Parameters:
    output_dir (str): The base directory to save the frames.
    video_path (str): Path to the input video file.

    Returns:
    str: Path to the newly created directory for storing frames.
    """
    video_basename = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = os.path.join(output_dir, video_basename, 'images')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    return output_folder

def extract_frames(video_path, output_folder, frame_rate):
    """
    Extracts frames from a video at a specified frame rate.

    Parameters:
    video_path (str): Path to the input video file.
    output_folder (str): Folder to save the extracted frames.
    frame_rate (int): Frame rate to extract frames (frames per second).
    """
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}.")
        return

    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    if fps == 0:
        print("Error: Unable to retrieve video FPS.")
        return

    print(f"Video FPS: {fps}")

    # Calculate the interval between frames to extract
    interval = int(fps / frame_rate)

    frame_idx = 0
    extracted_frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % interval == 0:
            frame_name = os.path.join(output_folder, f"frame_{extracted_frame_idx:04d}.png")
            cv2.imwrite(frame_name, frame)
            extracted_frame_idx += 1

        frame_idx += 1

    cap.release()
    print(f"Extracted {extracted_frame_idx} frames.")

