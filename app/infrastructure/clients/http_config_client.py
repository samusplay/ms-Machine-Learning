import os
from typing import Dict

import httpx

from app.domain.ports.config_client_interface import IConfigClient
from app.schemas.external_data import ConfigResponse

#Implementamos la interfaz y pare leer variables de entorno y llevarnos el endpoint de
"""
http://localhost:8000/api/v1/analytics/config/status
"""
class HttpConfigClient(IConfigClient):
    def __init__(self):
        # Usamos el nombre del servicio en Docker para la red interna
        self.base_url = os.getenv("CONFIG_SERVICE_URL", "http://ms-configuration:8000")

    async def get_active_weights(self) -> Dict[str, float]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/v1/config/status")
            response.raise_for_status()
            
            # Validamos con el schema de Pydantic
            data = ConfigResponse(**response.json())
            
            # Mapeamos a un diccionario simple para el dominio
            return {
                "poblacion": data.weights_active.peso_poblacion,
                "ingresos": data.weights_active.peso_ingresos,
                "competencia": data.weights_active.peso_competencia
            }