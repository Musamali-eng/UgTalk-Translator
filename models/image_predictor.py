"""Pretrained image classification for the Flask image-analysis endpoint."""

from __future__ import annotations

from io import BytesIO
from typing import Any


# A much broader, non-overlapping label set for CLIP zero-shot classification.
# CLIP can only ever pick from labels you give it, so the previous 12-item list
# (with near-duplicates like "a rose flower" / "a flower") forced most photos
# into the wrong bucket. This list covers common everyday subjects instead.
DEFAULT_CANDIDATE_LABELS = [
    # nature
    "a flower", "a tree", "a forest", "a mountain", "a beach", "the ocean",
    "a lake", "a river", "the sky", "clouds", "a sunset", "snow",
    # animals
    "a dog", "a cat", "a bird", "a horse", "a fish", "an insect",
    "a farm animal", "a wild animal",
    # people
    "a person", "a group of people", "a child", "a portrait of a face",
    # vehicles
    "a car", "a truck", "a motorcycle", "a bicycle", "an airplane",
    "a boat", "a train",
    # objects / tech
    "a laptop computer", "a smartphone", "a television", "a camera",
    "headphones", "a book", "a chair", "a table", "a lamp",
    # food
    "a plate of food", "a fruit", "a vegetable", "a dessert", "a drink",
    # places
    "a building", "a house", "a city street", "an office", "a bedroom",
    "a kitchen", "a store", "a stadium",
    # misc
    "text or a document", "a piece of art or a painting", "a logo",
    "a screenshot", "an object",
]


class ImagePredictor:
    """Identifies image content with zero-shot CLIP and a MobileNet fallback."""

    def __init__(self, candidate_labels: list[str] | None = None) -> None:
        self._model = None
        self._preprocess = None
        self._labels: list[str] = []
        self._clip_model = None
        self._clip_processor = None
        self._candidate_labels = candidate_labels or DEFAULT_CANDIDATE_LABELS

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

        from torchvision.models import MobileNet_V2_Weights, mobilenet_v2

        weights = MobileNet_V2_Weights.DEFAULT
        self._model = mobilenet_v2(weights=weights)
        self._model.eval()
        self._preprocess = weights.transforms()
        self._labels = list(weights.meta["categories"])

    def _predict_with_clip(self, image, limit: int) -> dict[str, Any]:
        import torch

        self._load_clip()
        candidate_labels = self._candidate_labels
        inputs = self._clip_processor(
            text=[f"a photo of {label}" for label in candidate_labels],
            images=image,
            return_tensors="pt",
            padding=True,
        )
        with torch.inference_mode():
            logits = self._clip_model(**inputs).logits_per_image[0]
            probabilities = torch.softmax(logits, dim=0)
            scores, indices = torch.topk(
                probabilities, k=max(1, min(limit, len(candidate_labels)))
            )

        predictions = [
            {"label": candidate_labels[int(index)], "confidence": round(float(score), 4)}
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

    def _predict_with_mobilenet(self, image, limit: int) -> dict[str, Any]:
        import torch

        self._load_model()
        batch = self._preprocess(image).unsqueeze(0)

        with torch.inference_mode():
            probabilities = torch.nn.functional.softmax(self._model(batch)[0], dim=0)
            scores, indices = torch.topk(probabilities, k=max(1, min(limit, 5)))

        predictions = [
            {"label": self._labels[int(index)], "confidence": round(float(score), 4)}
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

    def predict(self, image_bytes: bytes, limit: int = 5) -> dict[str, Any]:
        """Return human-readable image labels and confidence scores."""
        from PIL import Image

        if not image_bytes:
            raise ValueError("The uploaded image is empty")

        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
        except Exception as exc:
            raise ValueError(f"Could not read the uploaded image: {exc}") from exc

        # Zero-shot labels are more useful for user images than fixed ImageNet
        # labels, so try CLIP first and fall back to MobileNet only if CLIP
        # itself can't be used (e.g. can't download weights, no internet).
        try:
            return self._predict_with_clip(image, limit)
        except Exception:
            pass

        try:
            return self._predict_with_mobilenet(image, limit)
        except Exception as exc:
            raise RuntimeError(
                "Image classification failed: neither CLIP nor MobileNet could "
                f"run. Make sure torch, torchvision, transformers, and pillow "
                f"are installed. Underlying error: {exc}"
            ) from exc