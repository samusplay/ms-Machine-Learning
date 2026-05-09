# app/application/scoring_service.py

from typing import Any, Dict

from app.application.strategies import (
    GradientBoostingStrategy,
    KNNStrategy,
    LinearRegressionStrategy,
    RandomForestStrategy,
)
from app.domain.entities import MLExperimentEntity


class ScoringService:
    def __init__(self, analytics_client, config_client, model_repository):
        """
        Inyectamos los 'Ports' (Interfaces) para cumplir con DIP.
        """
        self.analytics_client = analytics_client
        self.config_client = config_client
        self.model_repository = model_repository
        
        # Registro dinámico de estrategias
        self.strategies = {
            "linear": LinearRegressionStrategy(),
            "knn": KNNStrategy(),
            "gradient_boosting": GradientBoostingStrategy(),
            "random_forest": RandomForestStrategy()
        }

    async def execute_scoring_pipeline(self, dataset_id: str, strategy_name: str) -> Dict[str, Any]:
        """
        Orquestación del Pipeline de ML (CA 1, CA 2, CA 5).
        """
        # 1. Obtención de Datos Reales (CA 1)
        weights = await self.config_client.get_active_weights()
        zones_data = await self.analytics_client.get_normalized_zones(dataset_id)

        if not zones_data:
            raise ValueError(f"El dataset {dataset_id} no contiene zonas procesables.")

        # 2. Selección de Estrategia (Patrón Strategy - CA 2)
        strategy = self.strategies.get(strategy_name.lower())
        if not strategy:
            available = list(self.strategies.keys())
            raise ValueError(f"La estrategia '{strategy_name}' no está implementada. Disponibles: {available}")

        # 3. Ejecución de la Inteligencia (Entrenamiento + Predicción)
        prediction_output = strategy.train_and_predict(zones_data, weights)

        # 4. Persistencia y Trazabilidad (CA 5)
        experiment = MLExperimentEntity(
            dataset_id=dataset_id,
            strategy_name=strategy.get_model_name(),
            hyperparameters=prediction_output.get("hyperparameters", {}),
            metrics=prediction_output.get("metrics", {}),
            execution_time_ms=prediction_output.get("execution_time_ms")
        )
        
        self.model_repository.save_experiment(experiment)

        # 5. Formato de Salida Final (Contrato de API)
        return {
            "dataset_id": dataset_id,
            "algorithm_used": strategy.get_model_name(),
            "execution_time_ms": prediction_output.get("execution_time_ms"),
            "results": prediction_output.get("results"),
            "model_metrics": prediction_output.get("metrics")
        }