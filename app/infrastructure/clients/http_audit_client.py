import logging
import os
import httpx
from datetime import datetime

from app.domain.ports.audit_client_interface import IAuditClient

logger = logging.getLogger(__name__)

class HttpAuditClient(IAuditClient):
    def __init__(self):
        self.base_url = os.getenv("MS_AUDIT_URL", "http://ms-auditoria:8000")

    async def send_prediction_event(
        self,
        zone_code: str,
        model_version: str,
        trace_id: str,
        details: dict
    ) -> None:
        payload = {
            "event_type": "PREDICTION_GENERATED",
            "source_service": "ms-ml",
            "reference_id": zone_code,
            "trace_id": trace_id,
            "details": details,
            "status": "SUCCESS"
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/events",
                    json=payload,
                    timeout=3.0
                )
                response.raise_for_status()
        except Exception as e:
            # DEGRADACIÓN CONTROLADA (CA-5):
            # Si ms-auditoria falla por latencia o caída temporal,
            # capturamos la excepción para no interrumpir el flujo
            # principal. El error queda registrado en logs internos
            # para seguimiento, pero no afecta la respuesta al usuario.
            logger.warning(
                f"[AUDIT-FAIL] {datetime.now()} | "
                f"event_type: {payload.get('event_type', 'UNKNOWN')} | "
                f"service: {payload.get('service_name', payload.get('source_service', 'UNKNOWN'))} | "
                f"causa: {str(e)}"
            )
