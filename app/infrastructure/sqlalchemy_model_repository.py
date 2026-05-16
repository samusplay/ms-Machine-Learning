from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities import (
    MLExperimentEntity,
    TrainedModelEntity,
    ZonePredictionEntity,
)
from app.domain.model_repository import ModelRepositoryPort
from app.infrastructure.models import MLExperiment, ZonePrediction


class SQLAlchemyModelRepository(ModelRepositoryPort):

    def __init__(self, db: Session):
        self.db = db

    def save_experiment(self, entity: MLExperimentEntity) -> MLExperimentEntity:
        db_exp = MLExperiment(
            dataset_id=entity.dataset_id,
            strategy_name=entity.strategy_name,
            hyperparameters=entity.hyperparameters,
            metrics=entity.metrics,
            execution_time_ms=entity.execution_time_ms,
        )
        self.db.add(db_exp)
        self.db.commit()
        self.db.refresh(db_exp)
        entity.id = db_exp.id
        return entity

    def save_zone_predictions(
        self,
        experiment_id: int,
        predictions: list
    ) -> None:
        for p in predictions:
            interp = p.get("interpretation", {})
            evidence = p.get("model_evidence", {})
            db_pred = ZonePrediction(
                experiment_id=experiment_id,
                zone_code=p["zone_code"],
                zone_name=p.get("zone_name", ""),
                potential_score=p["potential_score"],
                confidence=p["confidence"],
                label=interp.get("label", ""),
                business_summary=interp.get("business_summary", ""),
                color_code=p.get("color_code", ""),
                algorithm=evidence.get("algorithm", ""),
            )
            self.db.add(db_pred)
        self.db.commit()

    def get_last_prediction_by_zone(
        self,
        zone_code: str
    ) -> Optional[ZonePredictionEntity]:
        db_pred = (
            self.db.query(ZonePrediction)
            .filter(ZonePrediction.zone_code == zone_code)
            .order_by(ZonePrediction.created_at.desc())
            .first()
        )
        if not db_pred:
            return None
        return ZonePredictionEntity(
            id=db_pred.id,
            experiment_id=db_pred.experiment_id,
            zone_code=db_pred.zone_code,
            zone_name=db_pred.zone_name,
            potential_score=db_pred.potential_score,
            confidence=db_pred.confidence,
            label=db_pred.label,
            business_summary=db_pred.business_summary,
            color_code=db_pred.color_code,
            algorithm=db_pred.algorithm,
            created_at=db_pred.created_at,
        )

    def get_active_model(self, strategy_name: str) -> Optional[TrainedModelEntity]:
        return None