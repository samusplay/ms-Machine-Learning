from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IAnalyticsClient(ABC):
    @abstractmethod
    async def get_normalized_zones(self, dataset_id: str) -> List[Dict[str, Any]]:
        pass