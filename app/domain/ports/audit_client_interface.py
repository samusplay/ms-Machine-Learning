from abc import ABC, abstractmethod

class IAuditClient(ABC):
    @abstractmethod
    async def send_prediction_event(
        self,
        zone_code: str,
        model_version: str,
        trace_id: str,
        details: dict
    ) -> None:
        pass
