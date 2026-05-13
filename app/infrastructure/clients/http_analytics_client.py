import os

import httpx
from fastapi import HTTPException


class HttpAnalyticsClient:

    def __init__(self):

        self.base_url = os.getenv(
            "MS_ANALYTICS_URL",
            "http://ms-analytics:8000"
        )

    async def get_normalized_zones(self, dataset_id: int):

        async with httpx.AsyncClient() as client:

            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/analysis/zones/metrics/{dataset_id}"
                )

                response.raise_for_status()

                return response.json()

            except httpx.HTTPStatusError as e:

                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Error en ms-analytics: {e.response.text}"
                )

            except Exception as e:

                raise HTTPException(
                    status_code=500,
                    detail=str(e)
                )