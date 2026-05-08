
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


#Contrato de las Tablas
@dataclass
class MLExperimentEntity:
    """Entidad pura de dominio para un Experimento"""
    dataset_id: str
    strategy_name: str
    id: Optional[int] = None
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TrainedModelEntity:
    """Entidad pura de dominio para un Modelo Entrenado"""
    experiment_id: int
    model_name: str
    version: str
    artifact_path: str
    id: Optional[int] = None
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)