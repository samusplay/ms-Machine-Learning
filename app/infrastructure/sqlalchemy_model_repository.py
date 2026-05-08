from sqlalchemy.orm import Session

from app.domain.entities import MLExperimentEntity
from app.domain.model_repository import ModelRepositoryPort
from app.infrastructure.models import MLExperiment  # Tu modelo ORM


#Va ser el unico que va conocer la Db
class SQLAlchemyModelRepository(ModelRepositoryPort):
    #Crea un sesion la libreria
    def __init__(self, db: Session):
        self.db = db

    def save_experiment(self, entity: MLExperimentEntity) -> MLExperimentEntity:
        # MAPEO: De Entity (Dominio) a Model (Infraestructura/ORM)
        db_exp = MLExperiment(
            dataset_id=entity.dataset_id,
            strategy_name=entity.strategy_name,
            hyperparameters=entity.hyperparameters,
            metrics=entity.metrics
        )
        
        self.db.add(db_exp)
        self.db.commit()
        self.db.refresh(db_exp)
        
        # Le asignamos el ID generado por la DB a nuestra entidad de dominio
        entity.id = db_exp.id
        return entity