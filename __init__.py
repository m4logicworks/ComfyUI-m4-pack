from .m4_image_loader import SequenceImageLoader
from .m4_text_saver import SaveTextNode

NODE_CLASS_MAPPINGS = {
    "SequenceImageLoader": SequenceImageLoader,
    "SaveTextNode": SaveTextNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SequenceImageLoader": "M4 Sequence Image Loader",
    "SaveTextNode": "M4 Save Text"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
