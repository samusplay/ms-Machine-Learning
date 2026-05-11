import os
from typing import Dict

import httpx



from app.domain.ports.config_client_interface import IConfigClient


class HttpConfigClient(IConfigClient):

    def __init__(self):

       self.base_url = "http://ms-configuration:8000"
    async def get_active_weights(self) -> Dict[str, float]:

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{self.base_url}/profiles/active"
            )

            response.raise_for_status()

            data = response.json()

            return {
                "peso_poblacion": data["peso_poblacion"],
                "peso_ingresos": data["peso_ingresos"],
                "peso_competencia": data["peso_competencia"]
            }