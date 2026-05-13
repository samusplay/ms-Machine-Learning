# app/application/scoring_service.py

import asyncio
import os
from typing import Any, Dict

import httpx

from app.application.recommendation_engine import RecommendationEngine
from app.application.strategies import (
    GradientBoostingStrategy,
    KNNStrategy,
    LinearRegressionStrategy,
    RandomForestStrategy,
)

from app.domain.entities import MLExperimentEntity


class ScoringService:

    def __init__(self, analytics_client, config_client, model_repository):

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

    async def execute_scoring_pipeline(
        self,
        dataset_id: str,
        strategy_name: str
    ) -> Dict[str, Any]:

        # =========================
        # 1. OBTENER DATOS
        # =========================
        weights = await self.config_client.get_active_weights()

        zones_data = await self.analytics_client.get_normalized_zones(
            dataset_id
        )

        if not zones_data:
            raise ValueError(
                f"El dataset {dataset_id} no contiene zonas procesables."
            )

        # =========================
        # 2. ESTRATEGIA
        # =========================
        strategy = self.strategies.get(strategy_name.lower())

        if not strategy:
            available = list(self.strategies.keys())

            raise ValueError(
                f"La estrategia '{strategy_name}' no está implementada. "
                f"Disponibles: {available}"
            )

        # =========================
        # 3. EJECUTAR MODELO
        # =========================
        prediction_output = strategy.train_and_predict(
            zones_data,
            weights
        )

        # =========================
        # 4. EXTRAER FACTORES
        # =========================
        extracted_factors = []

        for zone in prediction_output.get("results", []):

            model_evidence = zone.get("model_evidence", {})

            main_factors = model_evidence.get(
                "main_factors",
                []
            )

            for factor in main_factors:

                extracted_factors.append({
                    "variable": factor.get("factor"),
                    "weight": factor.get("weight", 0)
                })

        # =========================
        # 5. RECOMENDACIONES
        # =========================
        recommendations = RecommendationEngine.build_recommendations(
            extracted_factors
        )

        # =========================
        # 6. GUARDAR EXPERIMENTO
        # =========================
        experiment = MLExperimentEntity(
            dataset_id=dataset_id,
            strategy_name=strategy.get_model_name(),
            hyperparameters=prediction_output.get(
                "hyperparameters",
                {}
            ),
            metrics=prediction_output.get(
                "metrics",
                {}
            ),
            execution_time_ms=prediction_output.get(
                "execution_time_ms"
            )
        )

        self.model_repository.save_experiment(experiment)

        # =========================
        # 7. AUDITORÍA ASÍNCRONA
        # =========================
        asyncio.create_task(
            self._notify_audit(experiment)
        )

        # =========================
        # 8. RESPUESTA FINAL
        # =========================
        return {
            "dataset_id": dataset_id,
            "algorithm_used": strategy.get_model_name(),
            "execution_time_ms": prediction_output.get(
                "execution_time_ms"
            ),
            "results": prediction_output.get("results"),
            "recommendations": recommendations,
            "model_metrics": prediction_output.get("metrics")
        }

    # ==========================================
    # MÉTODO INDEPENDIENTE DE LA CLASE
    # ==========================================
    async def _notify_audit(
        self,
        experiment: MLExperimentEntity
    ):

        audit_url = os.getenv(
            "MS_AUDIT_URL",
            "http://ms-auditoria:8000"
        )

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
            print(
                f"⚠️ Audit event failed (non-blocking): {e}"
            )