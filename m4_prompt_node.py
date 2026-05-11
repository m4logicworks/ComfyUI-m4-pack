import os
import json
from server import PromptServer
from aiohttp import web

# カスタムAPIエンドポイント: JSONファイルを読み込む
@PromptServer.instance.routes.get("/m4/read_json")
async def read_json(request):
    path = request.rel_url.query.get("path", "")
    if not path or not os.path.exists(path):
        return web.json_response({"error": "File not found or path empty"})
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return web.json_response({"data": data})
    except Exception as e:
        return web.json_response({"error": str(e)})

class M4PromptNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text_1": ("STRING", {"multiline": True, "default": ""}),
                "json_file_path": ("STRING", {"default": "", "multiline": False}),
                "prompt_selector": ([""], {}),
                "text_2": ("STRING", {"multiline": True, "default": ""}),
                "output_choice": (["Text 1", "Text 2"], {"default": "Text 1"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "process_text"
    CATEGORY = "M4/text"

    def process_text(self, text_1, json_file_path, prompt_selector, text_2, output_choice):
        # 選択された出力ソースのテキストを返す
        if output_choice == "Text 1":
            return (text_1,)
        else:
            return (text_2,)
