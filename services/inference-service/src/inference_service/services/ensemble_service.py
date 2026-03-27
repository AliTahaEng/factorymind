"""Ensemble inference — fan out to multiple model backends, merge results."""
import asyncio
import logging
import time
import uuid

from inference_service.interfaces.i_model_backend import IModelBackend, ModelInput
from inference_service.schemas.result import InferenceResult, BoundingBox
from inference_service.services.preprocessor import decode_and_preprocess

logger = logging.getLogger(__name__)


class EnsembleInferenceService:
    """Fans out to yolo + vit + anomaly backends, merges into a single InferenceResult."""

    def __init__(
        self,
        yolo_backend: IModelBackend,
        vit_backend: IModelBackend,
        anomaly_backend: IModelBackend,
        image_width: int = 640,
        image_height: int = 640,
        yolo_conf_threshold: float = 0.25,
        anomaly_threshold: float = 0.5,
        vit_threshold: float = 0.5,
    ):
        self._yolo = yolo_backend
        self._vit = vit_backend
        self._anomaly = anomaly_backend
        self._width = image_width
        self._height = image_height
        self._yolo_conf_threshold = yolo_conf_threshold
        self._anomaly_threshold = anomaly_threshold
        self._vit_threshold = vit_threshold

    async def run(self, image_id: str, image_bytes: bytes) -> InferenceResult:
        start = time.perf_counter()
        inspection_id = str(uuid.uuid4())
        import numpy as np
        image = decode_and_preprocess(image_bytes, self._width, self._height)

        request_id = str(uuid.uuid4())
        model_input_yolo = ModelInput(image=image, model_name="yolov8_defect", request_id=request_id)
        model_input_vit = ModelInput(image=image, model_name="vit_classifier", request_id=request_id)
        model_input_anomaly = ModelInput(image=image, model_name="efficientad_anomaly", request_id=request_id)

        yolo_out, vit_out, anomaly_out = await asyncio.gather(
            self._yolo.infer(model_input_yolo),
            self._vit.infer(model_input_vit),
            self._anomaly.infer(model_input_anomaly),
        )

        # Ensemble decision: defect if any model fires above threshold
        defect_detected = (
            (yolo_out.defect_detected and yolo_out.confidence >= self._yolo_conf_threshold)
            or (vit_out.defect_detected and vit_out.confidence >= self._vit_threshold)
            or (anomaly_out.anomaly_score >= self._anomaly_threshold)
        )

        # Confidence = max of all
        confidence = max(yolo_out.confidence, vit_out.confidence, anomaly_out.confidence)
        anomaly_score = anomaly_out.anomaly_score

        # Determine defect type from the strongest signal
        defect_type = None
        if defect_detected:
            if yolo_out.bounding_boxes:
                defect_type = yolo_out.bounding_boxes[0].get("label", "defect")
            elif vit_out.defect_detected:
                defect_type = "classification_defect"
            else:
                defect_type = "anomaly"

        bboxes = [BoundingBox(**bb) for bb in yolo_out.bounding_boxes]

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        import time as t
        return InferenceResult(
            image_id=image_id,
            inspection_id=inspection_id,
            defect_detected=defect_detected,
            defect_type=defect_type,
            confidence=confidence,
            anomaly_score=anomaly_score,
            bounding_boxes=bboxes,
            model_version="ensemble-v1",
            processing_time_ms=elapsed_ms,
            timestamp=int(t.time() * 1000),
        )
