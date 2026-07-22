"""Pretrained image classification for the Flask image-analysis endpoint."""

from __future__ import annotations

from io import BytesIO
from typing import Any


class ImagePredictor:
    """Identifies image content with zero-shot CLIP and a MobileNet fallback."""

    def __init__(self) -> None:
        self._model = None
        self._preprocess = None
        self._labels: list[str] = []
        self._clip_model = None
        self._clip_processor = None

    def _load_clip(self) -> None:
        if self._clip_model is not None:
            return

        from transformers import CLIPModel, CLIPProcessor

        model_name = "openai/clip-vit-base-patch32"
        self._clip_processor = CLIPProcessor.from_pretrained(model_name)
        self._clip_model = CLIPModel.from_pretrained(model_name)
        self._clip_model.eval()

    def _load_model(self) -> None:
        if self._model is not None:
            return

        import torch
        from torchvision.models import MobileNet_V2_Weights, mobilenet_v2

        weights = MobileNet_V2_Weights.DEFAULT
        self._model = mobilenet_v2(weights=weights)
        self._model.eval()
        self._preprocess = weights.transforms()
        self._labels = list(weights.meta["categories"])

    def predict(self, image_bytes: bytes, limit: int = 5) -> dict[str, Any]:
        """Return human-readable image labels and confidence scores."""
        from PIL import Image
        import torch

        if not image_bytes:
            raise ValueError("The uploaded image is empty")

        image = Image.open(BytesIO(image_bytes)).convert("RGB")

        # Zero-shot labels are more useful for user images than fixed ImageNet labels.
        candidate_labels = [
            "a rose flower", "a flower", "a tree", "a dog", "a cat", "a bird",
            "a person", "a car", "a building", "food", "a landscape", "an object",
        ]
        try:
            self._load_clip()
            inputs = self._clip_processor(
                text=[f"a photo of {label}" for label in candidate_labels],
                images=image,
                return_tensors="pt",
                padding=True,
            )
            with torch.inference_mode():
                logits = self._clip_model(**inputs).logits_per_image[0]
                probabilities = torch.softmax(logits, dim=0)
                scores, indices = torch.topk(probabilities, k=max(1, min(limit, len(candidate_labels))))

            predictions = [
                {
                    "label": candidate_labels[int(index)],
                    "confidence": round(float(score), 4),
                }
                for score, index in zip(scores, indices)
            ]
            top_prediction = predictions[0]
            return {
                "top_prediction": top_prediction,
                "description": (
                    f"This image most likely contains {top_prediction['label']} "
                    f"({top_prediction['confidence'] * 100:.1f}% confidence)."
                ),
                "predictions": predictions,
                "model": "CLIP zero-shot image classifier",
            }

        except Exception:
            # Keep the service usable when the CLIP model cannot be downloaded.
            self._load_model()
        batch = self._preprocess(image).unsqueeze(0)

        with torch.inference_mode():
            probabilities = torch.nn.functional.softmax(self._model(batch)[0], dim=0)
            scores, indices = torch.topk(probabilities, k=max(1, min(limit, 5)))

        predictions = [
            {
                "label": self._labels[int(index)],
                "confidence": round(float(score), 4),
            }
            for score, index in zip(scores, indices)
        ]
        top_prediction = predictions[0]
        return {
            "top_prediction": top_prediction,
            "description": (
                f"This image most likely contains a {top_prediction['label']} "
                f"({top_prediction['confidence'] * 100:.1f}% confidence)."
            ),
            "predictions": predictions,
            "model": "MobileNetV2 (pretrained ImageNet)",
        }
