from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


#Datos que van salir y llegar de  los diefrentes resultados
class ScoringRequest(BaseModel):
    # Por defecto usamos 'linear' como pide el documento
    strategy: str = Field(default="linear", description="Algoritmo a utilizar (linear, knn, gradient_boosting)")

class InterpretationSchema(BaseModel):
    label: str
    business_summary: str

class MainFactorSchema(BaseModel):
    factor: str
    impact: str
    weight: Optional[float] = None

class ModelEvidenceSchema(BaseModel):
    algorithm: str
    main_factors: List[MainFactorSchema]

class ZoneResultSchema(BaseModel):
    zone_code: str
    potential_score: float
    confidence: float
    interpretation: InterpretationSchema
    color_code: str
    model_evidence: ModelEvidenceSchema

class ScoringResponse(BaseModel):
    success: bool
    dataset_id: str
    algorithm_used: str
    execution_time_ms: int
    data: List[ZoneResultSchema]
    model_metrics: Dict[str, Any]