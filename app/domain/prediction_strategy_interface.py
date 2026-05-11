# app/domain/prediction_strategy_interface.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List


#Contrato que va implentar cada streategys
class IPredictionStrategy(ABC):
    @abstractmethod
    def train_and_predict(
        self,
        zones_data: List[Dict[str, Any]],
        weights: Dict[str, float],
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass