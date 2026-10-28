"""SAM 3 promptable concept segmentation: masks from short noun phrases."""
import numpy as np


class ConceptSegmenter:
    def __init__(self):
        from sam3.model_builder import build_sam3_image_model
        from sam3.model.sam3_image_processor import Sam3Processor
        self.processor = Sam3Processor(build_sam3_image_model())

    def mask(self, pil_image, prompt: str) -> np.ndarray:
        """Union of all instance masks matching `prompt` (e.g. 'road surface')."""
        state = self.processor.set_image(pil_image)
        out = self.processor.set_text_prompt(state=state, prompt=prompt)
        masks = out["masks"]
        if len(masks) == 0:
            return np.zeros((pil_image.height, pil_image.width), dtype=bool)
        return np.any(np.stack([m.squeeze().cpu().numpy() > 0 for m in masks]), axis=0)

    def road_mask(self, pil_image) -> np.ndarray:
        return self.mask(pil_image, "road surface")
