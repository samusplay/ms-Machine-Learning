import os
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException

from app.domain.ports.analytics_client_interface import IAnalyticsClient
from app.schemas.external_data import AnalyticsResponse


class HttpAnalyticsClient(IAnalyticsClient):
    def __init__(self):
        # Tomamos la URL de la red interna de Docker (ms-analytics:8000)
        self.base_url = os.getenv("MS_ANALYTICS_URL", "http://ms-analytics:8000")

    async def get_normalized_zones(self, dataset_id: str) -> List[Dict[str, Any]]:
        """
        Consume el endpoint de métricas territoriales y valida 
        que la estructura sea la correcta según el schema.
        """
        url = f"{self.base_url}/api/v1/analytics/zones/metrics/{dataset_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                
                # Si el ms-analytics responde con error (404, 500, etc)
                response.raise_for_status() 
                
                # VALIDACIÓN CRUCIAL:
                # Aquí usamos el schema para asegurar que los datos coinciden con lo que vimos en Postman
                raw_data = response.json()
                validated_response = AnalyticsResponse(**raw_data)
                
                # Retornamos la lista de zonas (como diccionarios) para que el Service trabaje fácil
                return [zone.model_dump() for zone in validated_response.data]

            except httpx.HTTPStatusError as e:
                # Error de respuesta (ej: 404 si el dataset no existe)
                raise HTTPException(
                    status_code=e.response.status_code, 
                    detail=f"Error en ms-analytics: {e.response.text}"
                )
            except Exception as e:
                # Error de conexión o de validación de schema
                raise HTTPException(
                    status_code=500, 
                    detail=f"Fallo en la comunicación con analítica: {str(e)}"
                )