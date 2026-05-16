from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities import (
    MLExperimentEntity,
    TrainedModelEntity,
    ZonePredictionEntity,
)


#Interfaz Pura para que se adapate cualquier Repo
class ModelRepositoryPort(ABC):
    @abstractmethod
    def save_experiment(self, experiment: MLExperimentEntity) -> MLExperimentEntity:
        """Define la firma para guardar un experimento"""
        pass

    @abstractmethod
    def get_active_model(self, strategy_name: str) -> Optional[TrainedModelEntity]:
        """Define la firma para buscar el modelo que usaremos en /predict"""
        pass

    #Metodo para guardar la zona  prediccion
    @abstractmethod
    def save_zone_predictions(
        self,
        experiment_id: int,
        predictions: list
    ) -> None:
        pass

    #Ultima prediccion de la zona
    @abstractmethod
    def get_last_prediction_by_zone(
        self,
        zone_code: str
    ) -> Optional[ZonePredictionEntity]:
        pass