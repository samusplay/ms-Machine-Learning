# app/application/scoring_service.py

import asyncio
import os
from typing import Any, Dict
from app.application.recommendation_engine import RecommendationEngine



import httpx

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


        # Generación de recomendaciones de negocio
        extracted_factors = []

        for zone in prediction_output.get("results", []):
            model_evidence = zone.get("model_evidence", {})
            main_factors = model_evidence.get("main_factors", [])

            for factor in main_factors:

                extracted_factors.append({
                    "variable": factor.get("factor"),
                    "weight": factor.get("weight", 0)
                })

        # Generación de recomendaciones de negocio
        recommendations = RecommendationEngine.build_recommendations(
            extracted_factors
        )


        # 4. Persistencia y Trazabilidad (CA 5)
        experiment = MLExperimentEntity(
            dataset_id=dataset_id,
            strategy_name=strategy.get_model_name(),
            hyperparameters=prediction_output.get("hyperparameters", {}),
            metrics=prediction_output.get("metrics", {}),
            execution_time_ms=prediction_output.get("execution_time_ms")
        )

        self.model_repository.save_experiment(experiment)

        # CA 5 — Evento asíncrono hacia ms-audit (fire and forget)
        asyncio.create_task(self._notify_audit(experiment))

        # 5. Formato de Salida Final (Contrato de API)
        return {
            "dataset_id": dataset_id,
            "algorithm_used": strategy.get_model_name(),
            "execution_time_ms": prediction_output.get("execution_time_ms"),
            "results": prediction_output.get("results"),

            "recommendations": recommendations,

            "model_metrics": prediction_output.get("metrics")
        }

        #Metodo Para Brayan
        async def _notify_audit(self, experiment: MLExperimentEntity):
        #"""CA 5 — Notifica a ms-audit de forma asíncrona sin bloquear el pipeline."""
         audit_url = os.getenv("MS_AUDIT_URL", "http://ms-auditoria:8000")
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                     f"{audit_url}/api/v1/audit/events",
                    json={
                        "event_type": "ML_MODEL_UPDATED",
                        "service": "ms-ml",
                        "message": "La inteligencia predictiva ha sido actualizada",
                        "metadata": {
                            "dataset_id": experiment.dataset_id,
                            "strategy": experiment.strategy_name,
                            "metrics": experiment.metrics
                        }
                    },
                    timeout=3.0
                )
        except Exception as e:
            print(f"⚠️ Audit event failed (non-blocking): {e}")