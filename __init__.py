from .m4_image_loader import SequenceImageLoader
from .m4_text_saver import SaveTextNode
from .m4_prompt_node import M4PromptNode

NODE_CLASS_MAPPINGS = {
    "SequenceImageLoader": SequenceImageLoader,
    "SaveTextNode": SaveTextNode,
    "M4PromptNode": M4PromptNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SequenceImageLoader": "M4 Sequence Image Loader",
    "SaveTextNode": "M4 Save Text",
    "M4PromptNode": "M4 Prompt Node"
}

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
