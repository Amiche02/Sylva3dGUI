import pycolmap
from pathlib import Path

image_dir = Path("data/rgb_images/josue")
output_path = Path("data/outputs/result2")

output_path.mkdir(parents=True, exist_ok=True)
mvs_path = output_path / "mvs"
database_path = output_path / "database.db"

# Count and print the number of images in the image directory
image_files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
num_images = len(image_files)
print(f"Number of images in the directory: {num_images}")

pycolmap.extract_features(database_path, image_dir)
pycolmap.match_exhaustive(database_path)

maps = pycolmap.incremental_mapping(database_path, image_dir, output_path)
maps[0].write(output_path)

pycolmap.undistort_images(mvs_path, output_path, image_dir)
pycolmap.patch_match_stereo(mvs_path)
pycolmap.stereo_fusion(mvs_path / "dense.ply", mvs_path)
