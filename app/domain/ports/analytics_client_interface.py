from abc import ABC, abstractmethod
from typing import Any, Dict, List


#Puerto de salida hacia el Microservicio de analytics
class IAnalyticsClient(ABC):
    @abstractmethod
    def get_zones_with_metrics(self, dataset_id: str) -> List[Dict[str, Any]]:
        pass