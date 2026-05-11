from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base  # Tu instancia de DeclarativeBase


class MLExperiment(Base):
    """
    Representación física en DB para la trazabilidad exigida en el CA 5[cite: 53].
    Aquí se registran los 'experimentos' o intentos de entrenamiento.
    """
    __tablename__ = "ml_experiments"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String, index=True, nullable=False)
    strategy_name = Column(String, nullable=False) # ej: 'RandomForest' [cite: 55]
    
    # JSON permite guardar cualquier estructura de Dict que venga de la Entity
    hyperparameters = Column(JSON, nullable=True) # Variables utilizadas [cite: 53]
    metrics = Column(JSON, nullable=True)        # Métricas de evaluación [cite: 53]
    
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación uno a uno: un experimento genera un modelo
    trained_model = relationship("TrainedModel", back_populates="experiment", uselist=False)


class TrainedModel(Base):
    """
    Catálogo de modelos listos para inferencia. 
    Cumple con el requisito de 'versión única' del CA 5[cite: 53].
    """
    __tablename__ = "trained_models"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("ml_experiments.id"), unique=True)
    
    model_name = Column(String, nullable=False)
    version = Column(String, nullable=False, unique=True) # Versión única [cite: 53]
    
    # Ruta física al archivo (.joblib) guardado en el volumen de Docker o S3
    artifact_path = Column(String, nullable=False) 
    
    is_active = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("MLExperiment", back_populates="trained_model")