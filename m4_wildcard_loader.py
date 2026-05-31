import os
import yaml
import random
from server import PromptServer
from aiohttp import web

# シーケンシャル（上から順番に進む）モードの状態管理用
# キーは unique_id、値は {"last_key": key, "index": current_index}
_sequential_states = {}

def parse_yaml_wildcards(data, prefix=""):
    result = {}
    current_items = []
    
    if isinstance(data, dict):
        for k, v in data.items():
            new_prefix = f"{prefix}/{k}" if prefix else k
            sub_result, sub_items = parse_yaml_wildcards(v, new_prefix)
            result.update(sub_result)
            current_items.extend(sub_items)
        if prefix:
            result[prefix] = current_items
    elif isinstance(data, list):
        items = [str(item) for item in data]
        current_items.extend(items)
        if prefix:
            result[prefix] = items
    else:
        val = str(data)
        current_items.append(val)
        if prefix:
            result[prefix] = [val]
            
    return result, current_items

def get_all_wildcards(base_dir):
    wildcards = {}
    keys = []
    
    if not base_dir or not os.path.isdir(base_dir):
        return {"keys": [], "wildcards": {}}
        
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(('.yaml', '.yml')):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_dir)
                rel_path_no_ext = os.path.splitext(rel_path)[0].replace('\\', '/')
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data:
                            flat, _ = parse_yaml_wildcards(data, prefix=rel_path_no_ext)
                            for k, v in flat.items():
                                wildcards[k] = v
                                keys.append(k)
                except Exception as e:
                    print(f"[M4WildcardLoader] Error reading yaml file {file_path}: {e}")
                    
    keys.sort()
    return {"keys": keys, "wildcards": wildcards}


# カスタムAPIエンドポイント: 指定フォルダ内のすべてのワイルドカードをスキャン
@PromptServer.instance.routes.get("/m4/get_wildcards")
async def get_wildcards_api(request):
    path = request.rel_url.query.get("path", "")
    if not path or not os.path.exists(path):
        return web.json_response({"error": "Directory not found or path empty", "keys": [], "wildcards": {}})
    try:
        data = get_all_wildcards(path)
        return web.json_response({"data": data})
    except Exception as e:
        return web.json_response({"error": str(e), "keys": [], "wildcards": {}})

class M4WildcardLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "wildcard_dir": ("STRING", {"default": "", "multiline": False}),
                "wildcard_selector": ([""], {}),
                "preview_text": ("STRING", {"default": "", "multiline": True}),
                "mode": (["random", "sequential", "fixed"], {"default": "random"}),
                "fixed_index": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "step": 1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

    @classmethod
    def VALIDATE_INPUTS(s, **kwargs):
        # ドロップダウンの選択肢がフロントエンド側で動的に変更されるため、
        # サーバー側の静的リストチェックを常にパスさせます
        return True

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "load_wildcard"
    CATEGORY = "M4/text"

    def load_wildcard(self, wildcard_dir, wildcard_selector, preview_text, mode, fixed_index, seed, unique_id=None):
        if not wildcard_dir or not os.path.isdir(wildcard_dir):
            return ("",)
            
        if not wildcard_selector:
            return ("",)
            
        data = get_all_wildcards(wildcard_dir)
        wildcards = data.get("wildcards", {})
        
        if wildcard_selector not in wildcards:
            return ("",)
            
        items = wildcards[wildcard_selector]
        if not items:
            return ("",)
            
        output_text = ""
        
        if mode == "random":
            # seedを使用して再現性のあるランダム選択を行う
            r = random.Random(seed)
            output_text = r.choice(items)
            
        elif mode == "sequential":
            # unique_idごとに状態を管理する
            global _sequential_states
            state = _sequential_states.get(unique_id, {"last_key": None, "index": 0})
            
            # 選択するキーが変わった場合はインデックスをリセット
            if state["last_key"] != wildcard_selector:
                state = {"last_key": wildcard_selector, "index": 0}
                
            idx = state["index"]
            output_text = items[idx % len(items)]
            
            # インデックスを進める
            state["index"] = (idx + 1) % len(items)
            _sequential_states[unique_id] = state
            
        elif mode == "fixed":
            idx = fixed_index % len(items)
            output_text = items[idx]
            
        return (output_text,)
