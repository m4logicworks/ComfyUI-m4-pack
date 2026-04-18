import os

class SaveTextNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True, "multiline": True}),
                "folder_path": ("STRING", {"default": "", "multiline": False}),
                "filename": ("STRING", {"default": "output", "multiline": False}),
                "collision_behavior": (["replace", "rename"], {"default": "replace"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_file_path",)
    FUNCTION = "save_text"
    OUTPUT_NODE = True
    CATEGORY = "M4/savers"

    def save_text(self, text, folder_path, filename, collision_behavior):
        if not folder_path:
            raise ValueError("Folder path cannot be empty")
        
        # フォルダが存在しない場合は作成する
        os.makedirs(folder_path, exist_ok=True)
        
        base_name = filename
        ext = ".txt"
        file_path = os.path.join(folder_path, base_name + ext)
        
        # rename設定かつ同名ファイルが存在する場合、サフィックスで連番を付与
        if collision_behavior == "rename" and os.path.exists(file_path):
            counter = 1
            while True:
                new_name = f"{base_name}_{counter}{ext}"
                file_path = os.path.join(folder_path, new_name)
                if not os.path.exists(file_path):
                    break
                counter += 1
                
        # テキストファイルを書き込み（replace設定の場合は上書き）
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
            
        return (file_path,)
