import os
import torch
import numpy as np
from PIL import Image, ImageOps

class SequenceImageLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "", "multiline": False}),
                "image_index": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "INT", "INT")
    RETURN_NAMES = ("image", "filename", "width", "height")
    FUNCTION = "load_image"
    CATEGORY = "M4/loaders"

    def load_image(self, folder_path, image_index):
        if not os.path.isdir(folder_path):
            raise ValueError(f"Folder path does not exist: {folder_path}")

        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions) and not f.startswith('.')]
        files.sort()

        if not files:
            raise ValueError(f"No valid images found in folder: {folder_path}")

        # インデックスが画像数を超えた場合は最後の画像を選択
        index = min(image_index, len(files) - 1)
        filename = files[index]
        file_path = os.path.join(folder_path, filename)

        # 画像読み込みとExifの回転補正
        img = Image.open(file_path)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        
        width, height = img.size
        
        # ComfyUIの形式 [B, H, W, C] に変換
        image_tensor = torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0)
        
        # 拡張子を除いたファイル名を取得
        filename_no_ext = os.path.splitext(filename)[0]

        return (image_tensor, filename_no_ext, width, height)
