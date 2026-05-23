# app/application/scoring_service.py — completo

import asyncio
from typing import Any, Dict

from app.application.strategies import (
    GradientBoostingStrategy,
    KNNStrategy,
    LinearRegressionStrategy,
    RandomForestStrategy,
)
from app.domain.entities import MLExperimentEntity


class ScoringService:
    def __init__(self, analytics_client, config_client, model_repository, audit_client):
        self.analytics_client = analytics_client
        self.config_client = config_client
        self.model_repository = model_repository
        self.audit_client = audit_client

        self.strategies = {
            "linear": LinearRegressionStrategy(),
            "knn": KNNStrategy(),
            "gradient_boosting": GradientBoostingStrategy(),
            "random_forest": RandomForestStrategy()
        }

    async def execute_scoring_pipeline(self, dataset_id: str, strategy_name: str, trace_id: str) -> Dict[str, Any]:

        # 1. Obtención de Datos Reales (CA 1)
        weights = await self.config_client.get_active_weights()
        zones_data = await self.analytics_client.get_normalized_zones(dataset_id)

        if not zones_data:
            raise ValueError(f"El dataset {dataset_id} no contiene zonas procesables.")

        # 2. Selección de Estrategia (CA 2)
        strategy = self.strategies.get(strategy_name.lower())
        if not strategy:
            available = list(self.strategies.keys())
            raise ValueError(f"La estrategia '{strategy_name}' no está implementada. Disponibles: {available}")

        # 3. Ejecución
        prediction_output = strategy.train_and_predict(zones_data, weights)

        # 4. Persistencia (CA 5) — guardamos experimento Y predicciones por zona (HU-20)
        experiment = MLExperimentEntity(
            dataset_id=dataset_id,
            strategy_name=strategy.get_model_name(),
            hyperparameters=prediction_output.get("hyperparameters", {}),
            metrics=prediction_output.get("metrics", {}),
            execution_time_ms=prediction_output.get("execution_time_ms")
        )
        experiment = self.model_repository.save_experiment(experiment)  # ← ahora retorna con id

        # Guardamos cada zona individualmente para que GET /predictions/{zone_code} funcione
        self.model_repository.save_zone_predictions(
            experiment_id=experiment.id,
            predictions=prediction_output.get("results", [])
        )

        # CA 5 — Notificación asíncrona a ms-audit
        results = prediction_output.get("results", [])
        for zone in results:
            asyncio.create_task(self._notify_audit_per_zone(zone, trace_id, strategy.get_model_name()))

        # 5. Salida final
        return {
            "dataset_id": dataset_id,
            "algorithm_used": strategy.get_model_name(),
            "execution_time_ms": prediction_output.get("execution_time_ms"),
            "results": prediction_output.get("results"),
            "model_metrics": prediction_output.get("metrics")
        }

    async def _notify_audit_per_zone(self, zone: dict, trace_id: str, model_name: str):
        zone_code = zone.get("zone_code")
        if not zone_code:
            return
        details = {
            "potential_score": zone.get("potential_score"),
            "confidence": zone.get("confidence"),
            "label": zone.get("interpretation", {}).get("label"),
            "algorithm": model_name
        }
        await self.audit_client.send_prediction_event(
            zone_code=zone_code,
            model_version=model_name,
            trace_id=trace_id,
            details=details
        )