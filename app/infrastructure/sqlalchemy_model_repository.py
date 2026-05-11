# app/infrastructure/sqlalchemy_model_repository.py

from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities import MLExperimentEntity, TrainedModelEntity
from app.domain.model_repository import ModelRepositoryPort
from app.infrastructure.models import MLExperiment


class SQLAlchemyModelRepository(ModelRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def save_experiment(self, entity: MLExperimentEntity) -> MLExperimentEntity:
        db_exp = MLExperiment(
            dataset_id=entity.dataset_id,
            strategy_name=entity.strategy_name,
            hyperparameters=entity.hyperparameters,
            metrics=entity.metrics
        )
        self.db.add(db_exp)
        self.db.commit()
        self.db.refresh(db_exp)
        entity.id = db_exp.id
        return entity

    def get_active_model(self, strategy_name: str) -> Optional[TrainedModelEntity]:
        # Por ahora retorna None — se implementa cuando lleguemos al endpoint /predict
        return None