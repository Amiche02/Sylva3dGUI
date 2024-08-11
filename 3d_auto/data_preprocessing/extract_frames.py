"""
Extract frames from a video.

Author: Stéphane KPOVIESSI
At Sylvagreg company
Big data engineer student
"""
 
import argparse
from utils import create_output_folder, extract_frames

def main():
    parser = argparse.ArgumentParser(description="Extract frames from a video.")
    parser.add_argument("--video_path", type=str, required=True, help="Path to the input video file.")
    parser.add_argument("--output_dir", type=str, required=True, help="Base directory to save the extracted frames.")
    parser.add_argument("--frame_rate", type=int, default=6, help="Frame rate to extract frames (frames per second).")
    
    args = parser.parse_args()
    
    output_folder = create_output_folder(args.output_dir, args.video_path)
    extract_frames(args.video_path, output_folder, args.frame_rate)

if __name__ == "__main__":
    main()
