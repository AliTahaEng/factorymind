"""Triton gRPC adapter — production ML backend."""
import time
import logging
import numpy as np

from inference_service.interfaces.i_model_backend import IModelBackend, ModelInput, ModelOutput

logger = logging.getLogger(__name__)


class TritonAdapter(IModelBackend):
    """Calls NVIDIA Triton Inference Server via gRPC."""

    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import tritonclient.grpc as grpcclient
                self._client = grpcclient.InferenceServerClient(
                    url=f"{self._host}:{self._port}", verbose=False
                )
            except ImportError:
                logger.warning("tritonclient not installed — falling back to fake adapter")
                raise RuntimeError("tritonclient not available")
        return self._client

    async def infer(self, model_input: ModelInput) -> ModelOutput:
        start = time.perf_counter()
        try:
            client = self._get_client()
            import tritonclient.grpc as grpcclient
            # Prepare input tensor: (1, 3, H, W) float32
            img = model_input.image  # (H, W, 3)
            inp = np.transpose(img, (2, 0, 1))[np.newaxis].astype(np.float32)
            triton_input = grpcclient.InferInput("input__0", inp.shape, "FP32")
            triton_input.set_data_from_numpy(inp)
            outputs = [grpcclient.InferRequestedOutput("output__0")]
            result = client.infer(model_name=model_input.model_name, inputs=[triton_input], outputs=outputs)
            raw = result.as_numpy("output__0")
            latency = (time.perf_counter() - start) * 1000
            # Minimal parsing: treat first output value as confidence
            confidence = float(raw.flatten()[0]) if raw.size > 0 else 0.0
            return ModelOutput(
                model_name=model_input.model_name,
                request_id=model_input.request_id,
                raw_outputs={"output__0": raw.tolist()},
                defect_detected=confidence > 0.5,
                confidence=confidence,
                anomaly_score=confidence,
                latency_ms=latency,
            )
        except Exception as exc:
            logger.error("Triton inference error for %s: %s", model_input.model_name, exc)
            latency = (time.perf_counter() - start) * 1000
            return ModelOutput(
                model_name=model_input.model_name,
                request_id=model_input.request_id,
                defect_detected=False,
                confidence=0.0,
                anomaly_score=0.0,
                latency_ms=latency,
            )

    async def health_check(self) -> bool:
        try:
            client = self._get_client()
            return client.is_server_live()
        except Exception:
            return False
