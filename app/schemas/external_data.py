from typing import List

from pydantic import BaseModel


# Lo que recibimos de ms-analytics (según tu prueba de Postman)
class AnalyticsZoneMetric(BaseModel):
    zone_code: str
    zone_name: str
    poblacion: float
    ingresos: float
    competencia: float

class AnalyticsResponse(BaseModel):
    success: bool
    data: List[AnalyticsZoneMetric]

# Lo que recibimos de ms-configuration (según tu imagen de Postman)
class ConfigWeights(BaseModel):
    peso_poblacion: float
    peso_ingresos: float
    peso_competencia: float

class ConfigResponse(BaseModel):
    success: bool
    weights_active: ConfigWeights