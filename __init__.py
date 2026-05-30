from .m4_image_loader import SequenceImageLoader
from .m4_text_saver import SaveTextNode
from .m4_prompt_node import M4PromptNode
from .m4_resolution_preset import M4ResolutionPresetNode
from .m4_texture_generator import M4TextureGeneratorNode

NODE_CLASS_MAPPINGS = {
    "SequenceImageLoader": SequenceImageLoader,
    "SaveTextNode": SaveTextNode,
    "M4PromptNode": M4PromptNode,
    "M4ResolutionPresetNode": M4ResolutionPresetNode,
    "M4TextureGeneratorNode": M4TextureGeneratorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SequenceImageLoader": "M4 Sequence Image Loader",
    "SaveTextNode": "M4 Save Text",
    "M4PromptNode": "M4 Prompt Node",
    "M4ResolutionPresetNode": "M4 Resolution Preset Node",
    "M4TextureGeneratorNode": "M4 Texture Generator"
}

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
