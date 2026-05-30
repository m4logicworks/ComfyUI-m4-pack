import torch
import torch.nn.functional as F
import math

TEXTURE_TYPES = [
    "White Noise",
    "Gaussian Noise",
    "Film Grain",
    "Perlin Noise (Smooth)",
    "Fractal Noise (High Detail)",
    "Canvas Texture",
    "Paper Texture",
    "Horizontal Brush",
    "Vertical Brush",
    "Diagonal Hatching",
    "Vignette",
    "Color Cloud"
]

COLOR_PRESETS = {
    "White (Default)": "#FFFFFF",
    "Black": "#000000",
    "Gray": "#808080",
    "Red": "#FF0000",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "Sepia": "#704214",
    "Warm": "#FFD0B0",
    "Cool": "#B0D0FF",
    "Custom HEX": ""
}

class M4TextureGeneratorNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "height": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1}),
                "texture_type": (TEXTURE_TYPES, {"default": "White Noise"}),
                "scale": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 100.0, "step": 0.05}),
                "strength": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "color_preset": (list(COLOR_PRESETS.keys()), {"default": "White (Default)"}),
                "custom_hex": ("STRING", {"default": "#FFFFFF"})
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_texture"
    CATEGORY = "M4/image"

    def hex_to_rgb(self, hex_str):
        hex_str = hex_str.lstrip('#')
        if len(hex_str) != 6:
            return (1.0, 1.0, 1.0) # 失敗時は白
        try:
            return tuple(int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        except ValueError:
            return (1.0, 1.0, 1.0)

    def generate_fractal_noise(self, h, w, octaves=4, persistence=0.5, scale=1.0, x_scale=1.0, y_scale=1.0):
        noise = torch.zeros((1, 1, h, w))
        amplitude = 1.0
        total_amplitude = 0.0
        
        for i in range(octaves):
            freq = 2 ** i
            # 解像度を計算
            h_i = max(2, int(h / (scale * y_scale * freq)))
            w_i = max(2, int(w / (scale * x_scale * freq)))
            
            base_noise = torch.rand((1, 1, h_i, w_i))
            upscaled = F.interpolate(base_noise, size=(h, w), mode='bicubic', align_corners=False)
            
            noise += upscaled * amplitude
            total_amplitude += amplitude
            amplitude *= persistence
            
        return noise / total_amplitude

    def generate_texture(self, width, height, batch_size, texture_type, scale, strength, color_preset, custom_hex):
        images = []
        
        # カラーの決定
        hex_color = custom_hex if color_preset == "Custom HEX" else COLOR_PRESETS[color_preset]
        r, g, b = self.hex_to_rgb(hex_color)
        color_tensor = torch.tensor([r, g, b]).view(1, 1, 3)

        for _ in range(batch_size):
            if texture_type == "White Noise":
                base = torch.rand((height, width, 1))
            
            elif texture_type == "Gaussian Noise":
                base = torch.randn((height, width, 1))
                base = (base - base.min()) / (base.max() - base.min() + 1e-5)
                
            elif texture_type == "Film Grain":
                # 細かいノイズと少し大きいノイズのブレンド
                n1 = torch.randn((height, width, 1))
                n2 = F.interpolate(torch.randn((1, 1, height//2, width//2)), size=(height, width), mode='bicubic', align_corners=False).squeeze(0).permute(1, 2, 0)
                base = n1 * 0.7 + n2 * 0.3
                base = (base - base.min()) / (base.max() - base.min() + 1e-5)
                
            elif texture_type == "Perlin Noise (Smooth)":
                noise = self.generate_fractal_noise(height, width, octaves=3, scale=scale * 10.0)
                base = noise.squeeze(0).permute(1, 2, 0)
                
            elif texture_type == "Fractal Noise (High Detail)":
                noise = self.generate_fractal_noise(height, width, octaves=6, scale=scale * 5.0)
                base = noise.squeeze(0).permute(1, 2, 0)
                
            elif texture_type == "Canvas Texture":
                # 縦横の細かいノイズを合成
                h_noise = self.generate_fractal_noise(height, width, octaves=2, scale=scale*2.0, x_scale=10.0, y_scale=0.1)
                v_noise = self.generate_fractal_noise(height, width, octaves=2, scale=scale*2.0, x_scale=0.1, y_scale=10.0)
                base = (h_noise + v_noise).squeeze(0).permute(1, 2, 0) / 2.0
                
            elif texture_type == "Paper Texture":
                n1 = self.generate_fractal_noise(height, width, octaves=4, scale=scale*3.0)
                n2 = torch.rand((height, width, 1)) * 0.2
                base = n1.squeeze(0).permute(1, 2, 0) + n2
                
            elif texture_type == "Horizontal Brush":
                noise = self.generate_fractal_noise(height, width, octaves=4, scale=scale*4.0, x_scale=15.0, y_scale=1.0)
                base = noise.squeeze(0).permute(1, 2, 0)
                
            elif texture_type == "Vertical Brush":
                noise = self.generate_fractal_noise(height, width, octaves=4, scale=scale*4.0, x_scale=1.0, y_scale=15.0)
                base = noise.squeeze(0).permute(1, 2, 0)
                
            elif texture_type == "Diagonal Hatching":
                # 斜め波模様の生成
                y, x = torch.meshgrid(torch.linspace(0, scale*100, height), torch.linspace(0, scale*100, width), indexing='ij')
                diag = torch.sin(x + y) * 0.5 + 0.5
                n = torch.rand((height, width)) * 0.3
                base = (diag + n).unsqueeze(2)
                
            elif texture_type == "Vignette":
                y, x = torch.meshgrid(torch.linspace(-1, 1, height), torch.linspace(-1, 1, width), indexing='ij')
                dist = torch.sqrt(x*x + y*y)
                base = (1.0 - torch.clamp(dist / (scale * 1.5), 0.0, 1.0)).unsqueeze(2)
                
            elif texture_type == "Color Cloud":
                noise_r = self.generate_fractal_noise(height, width, octaves=4, scale=scale*5.0)
                noise_g = self.generate_fractal_noise(height, width, octaves=4, scale=scale*5.0)
                noise_b = self.generate_fractal_noise(height, width, octaves=4, scale=scale*5.0)
                base = torch.cat([noise_r, noise_g, noise_b], dim=1).squeeze(0).permute(1, 2, 0)

            # 強さ(strength)とベースカラーの適用
            if texture_type != "Color Cloud":
                base = base.repeat(1, 1, 3) # グレースケールをRGBに拡張
            
            # テクスチャをカラーに乗算する（暗い部分は暗く、明るい部分はベース色になる）
            textured_color = color_tensor * base
            
            # strength = 0 なら単色のベースカラー、strength = 1 ならテクスチャ全開
            final_image = torch.lerp(color_tensor.repeat(height, width, 1), textured_color, strength)
            
            # クリップ
            final_image = torch.clamp(final_image, 0.0, 1.0)
            images.append(final_image)

        batch_tensor = torch.stack(images, dim=0)
        return (batch_tensor,)
