import os
import torch
import numpy as np
import random
from PIL import Image, ImageOps
from server import PromptServer
from aiohttp import web
import folder_paths

# インクリメントおよび各種状態管理用
# キーは unique_id、値は {"last_folder": path, "last_image": filename, "offset": int}
_loader_states = {}

# サポートする画像拡張子
VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')

def get_images_in_folder(folder_path):
    if not folder_path or not os.path.isdir(folder_path):
        return []
    try:
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(VALID_EXTENSIONS) and not f.startswith('.')]
        files.sort()
        return files
    except Exception as e:
        print(f"[M4FolderImagePromptLoader] Error listing directory {folder_path}: {e}")
        return []

# APIエンドポイント1: 指定フォルダ内の画像一覧を取得
@PromptServer.instance.routes.get("/m4/get_images")
async def get_images_api(request):
    path = request.rel_url.query.get("path", "")
    if not path or not os.path.exists(path):
        return web.json_response({"error": "Directory not found", "files": []})
    
    files = get_images_in_folder(path)
    return web.json_response({"files": files})

# APIエンドポイント2: 指定画像のプレビュー配信用
@PromptServer.instance.routes.get("/m4/get_image_preview")
async def get_image_preview_api(request):
    folder_path = request.rel_url.query.get("folder_path", "")
    filename = request.rel_url.query.get("filename", "")
    
    if not folder_path or not filename:
        return web.Response(status=400, text="Missing folder_path or filename")
        
    full_path = os.path.join(folder_path, filename)
    # パスの検証（セキュリティ上、存在する画像ファイルのみ許可）
    if not os.path.isfile(full_path) or not filename.lower().endswith(VALID_EXTENSIONS):
        return web.Response(status=404, text="Image not found")
        
    return web.FileResponse(full_path)

# APIエンドポイント3: 指定画像と同名のテキストファイル内容を取得（フロントエンドプレビュー用）
@PromptServer.instance.routes.get("/m4/get_text_preview")
async def get_text_preview_api(request):
    folder_path = request.rel_url.query.get("folder_path", "")
    filename = request.rel_url.query.get("filename", "")
    
    if not folder_path or not filename:
        return web.json_response({"text": ""})
        
    # 同名のテキストファイルを探す
    base_name = os.path.splitext(filename)[0]
    txt_path = os.path.join(folder_path, base_name + ".txt")
    
    if os.path.isfile(txt_path):
        try:
            with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return web.json_response({"text": content})
        except Exception as e:
            return web.json_response({"error": str(e), "text": ""})
            
    return web.json_response({"text": ""})


class M4FolderImagePromptLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "", "multiline": False}),
                "mode": (["increment", "fixed", "random"], {"default": "increment"}),
                "image_select": ([""], {}),
                "fixed_index": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "step": 1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    @classmethod
    def VALIDATE_INPUTS(s, **kwargs):
        # 動的ドロップダウンを許容するため、静的な入力チェックをパスさせる
        return True

    RETURN_TYPES = ("IMAGE", "STRING", "INT", "INT")
    RETURN_NAMES = ("IMAGE", "STRING", "WIDTH", "HEIGHT")
    FUNCTION = "load_image_prompt"
    CATEGORY = "M4/loaders"

    def load_image_prompt(self, folder_path, mode, image_select, fixed_index, seed, unique_id=None):
        if not folder_path or not os.path.isdir(folder_path):
            raise ValueError(f"Folder path does not exist: {folder_path}")

        files = get_images_in_folder(folder_path)
        if not files:
            raise ValueError(f"No valid images found in folder: {folder_path}")

        # インデックス起点の特定（image_selectが存在すればそのインデックス、なければ0）
        start_idx = 0
        if image_select in files:
            start_idx = files.index(image_select)

        # ターゲットとなるインデックスの決定
        target_idx = start_idx

        global _loader_states
        state = _loader_states.get(unique_id, {"last_folder": None, "last_image": None, "offset": 0})

        # フォルダまたは選択画像が変わった場合は状態をリセット
        if state["last_folder"] != folder_path or state["last_image"] != image_select:
            state = {"last_folder": folder_path, "last_image": image_select, "offset": 0}

        if mode == "fixed":
            target_idx = (start_idx + fixed_index) % len(files)
            
        elif mode == "random":
            # seedベースのランダム
            r = random.Random(seed)
            target_idx = r.randint(0, len(files) - 1)
            
        elif mode == "increment":
            # 起点 + offset
            offset = state["offset"]
            target_idx = (start_idx + offset) % len(files)
            
            # 次回に向けてオフセットをインクリメント
            state["offset"] = (offset + 1) % len(files)
            _loader_states[unique_id] = state

        # 選択されたファイル名
        chosen_filename = files[target_idx]
        file_path = os.path.join(folder_path, chosen_filename)

        # 画像の読み込みと回転補正
        img = Image.open(file_path)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        width, height = img.size

        # ComfyUI形式の画像テンソル [1, H, W, 3] に変換
        image_tensor = torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0)

        # 同名テキストファイルの読み込み
        base_name = os.path.splitext(chosen_filename)[0]
        txt_path = os.path.join(folder_path, base_name + ".txt")
        prompt_text = ""

        if os.path.isfile(txt_path):
            try:
                with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
                    prompt_text = f.read()
            except Exception as e:
                print(f"[M4FolderImagePromptLoader] Error reading prompt file {txt_path}: {e}")

        # プレビュー表示用の一時画像を保存
        # ComfyUIの標準プレビュー機能を活用する
        temp_dir = folder_paths.get_temp_directory()
        # unique_idごとにプレビュー画像を固定することでディスクの圧迫を防ぐ
        temp_filename = f"m4_preview_{unique_id}.png"
        temp_filepath = os.path.join(temp_dir, temp_filename)
        
        # プレビュー用画像を一時保存
        img.save(temp_filepath, format="PNG")

        preview_result = {
            "ui": {
                "images": [
                    {
                        "filename": temp_filename,
                        "subfolder": "",
                        "type": "temp"
                    }
                ]
            },
            "result": (image_tensor, prompt_text, width, height)
        }

        return preview_result
