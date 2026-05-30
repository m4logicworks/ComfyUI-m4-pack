RESOLUTION_PRESETS = [
    # 正方形 (Square)
    "1024 x 1024 (1:1)",
    "1536 x 1536 (1:1)",
    "2048 x 2048 (1:1)",
    
    # 縦長 (Portrait - SDXL/Flux)
    "896 x 1152 (3:4)",
    "832 x 1216 (2:3)",
    "768 x 1344 (9:16)",
    "640 x 1536 (9:21)",
    
    # 横長 (Landscape - SDXL/Flux)
    "1152 x 896 (4:3)",
    "1216 x 832 (3:2)",
    "1344 x 768 (16:9)",
    "1536 x 640 (21:9)",
    
    # 縦長高解像度 (2K)
    "1536 x 2048 (3:4)",
    "1344 x 2048 (2:3)",
    "1152 x 2048 (9:16)",
    "1024 x 2048 (1:2)",
    
    # 横長高解像度 (2K)
    "2048 x 1536 (4:3)",
    "2048 x 1344 (3:2)",
    "2048 x 1152 (16:9)",
    "2048 x 1024 (2:1)",
    
    # 動画・配信規格
    "1280 x 720 (HD 16:9)",
    "720 x 1280 (HD 9:16)",
    "1920 x 1080 (FHD 16:9)",
    "1080 x 1920 (FHD 9:16)",
    
    # カスタム指定
    "Custom"
]

class M4ResolutionPresetNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "preset": (RESOLUTION_PRESETS, {"default": "1024 x 1024 (1:1)"}),
                "custom_width": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "custom_height": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "invert_aspect": ("BOOLEAN", {"default": False}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1}),
            }
        }

    RETURN_TYPES = ("INT", "INT", "INT")
    RETURN_NAMES = ("width", "height", "batch_size")
    FUNCTION = "get_resolution"
    CATEGORY = "M4/utils"

    def get_resolution(self, preset, custom_width, custom_height, invert_aspect, batch_size):
        if preset == "Custom":
            width = custom_width
            height = custom_height
        else:
            try:
                # "1024 x 1024 (1:1)" -> "1024 x 1024"
                res_part = preset.split(" (")[0]
                w_str, h_str = res_part.split(" x ")
                width = int(w_str)
                height = int(h_str)
            except Exception as e:
                # パース失敗時の安全用デフォルト
                width = 1024
                height = 1024

        # 縦横反転が有効な場合
        if invert_aspect:
            width, height = height, width

        return (width, height, batch_size)
