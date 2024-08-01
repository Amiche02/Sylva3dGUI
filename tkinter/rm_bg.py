import os
import sys

import numpy as np
import torch
import torch.nn.functional as F
from torchvision.transforms.functional import normalize
from huggingface_hub import hf_hub_download
from briarmbg import BriaRMBG
from PIL import Image

from utils import create_output_folder

# Initialize and load the model
net = BriaRMBG()
model_path = hf_hub_download("briaai/RMBG-1.4", 'model.pth')
if torch.cuda.is_available():
    net.load_state_dict(torch.load(model_path))
    net = net.cuda()
else:
    net.load_state_dict(torch.load(model_path, map_location="cpu"))
net.eval()

def resize_image(image, size=(1024, 1024)):
    image = image.convert('RGB')
    orig_width, orig_height = image.size
    ratio = min(size[0] / orig_width, size[1] / orig_height)
    new_size = (int(orig_width * ratio), int(orig_height * ratio))
    image = image.resize(new_size, Image.BILINEAR)
    return image

def pad_image(image, size=(1024, 1024)):
    new_image = Image.new("RGB", size)
    new_image.paste(image, ((size[0] - image.size[0]) // 2, (size[1] - image.size[1]) // 2))
    return new_image

def prepare_image(image, size=(1024, 1024)):
    resized_image = resize_image(image, size)
    padded_image = pad_image(resized_image, size)
    return padded_image

def process(image):
    if not isinstance(image, Image.Image):
        raise TypeError("Input must be a PIL image")

    orig_image = image
    w, h = orig_image.size
    image = prepare_image(orig_image)
    im_np = np.array(image)
    im_tensor = torch.tensor(im_np, dtype=torch.float32).permute(2, 0, 1)
    im_tensor = torch.unsqueeze(im_tensor, 0)
    im_tensor = torch.divide(im_tensor, 255.0)
    im_tensor = normalize(im_tensor, [0.5, 0.5, 0.5], [1.0, 1.0, 1.0])
    if torch.cuda.is_available():
        im_tensor = im_tensor.cuda()

    result = net(im_tensor)
    result = torch.squeeze(F.interpolate(result[0][0], size=(h, w), mode='bilinear'), 0)
    ma = torch.max(result)
    mi = torch.min(result)
    result = (result - mi) / (ma - mi)
    im_array = (result * 255).cpu().data.numpy().astype(np.uint8)
    pil_im = Image.fromarray(np.squeeze(im_array))
    new_im = Image.new("RGBA", pil_im.size, (0, 0, 0, 0))
    new_im.paste(orig_image, mask=pil_im)

    return new_im

def remove_background_briarmbg(input_folder, output_folder):
    output_dir = create_output_folder(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'tiff')):
            input_image_path = os.path.join(input_folder, file_name)
            image = Image.open(input_image_path)
            output_image = process(image)
            output_image_path = os.path.join(output_dir, f"rm_{os.path.splitext(file_name)[0]}.png")
            output_image.save(output_image_path)
            print(f"Processed and saved: {output_image_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Remove background from images.")
    parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing input images.")
    parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder to save output images.")
    
    args = parser.parse_args()
    remove_background_briarmbg(args.input_folder, args.output_folder)
