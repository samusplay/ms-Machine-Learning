# app/routers/ml_router.py

import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.application.scoring_service import ScoringService
from app.infrastructure.clients.http_analytics_client import HttpAnalyticsClient
from app.infrastructure.clients.http_config_client import HttpConfigClient
from app.infrastructure.database import get_db
from app.infrastructure.sqlalchemy_model_repository import SQLAlchemyModelRepository
from app.schemas.scoring import ScoringRequest, ScoringResponse

router = APIRouter()

def get_scoring_service(db: Session = Depends(get_db)) -> ScoringService:
    return ScoringService(
        analytics_client=HttpAnalyticsClient(),
        config_client=HttpConfigClient(),
        model_repository=SQLAlchemyModelRepository(db)
    )

@router.post("/execute/{dataset_id}", response_model=ScoringResponse)
async def execute_scoring(
    dataset_id: str,
    request: ScoringRequest,
    service: ScoringService = Depends(get_scoring_service)
):
    try:
        result = await service.execute_scoring_pipeline(
            dataset_id=dataset_id, 
            strategy_name=request.strategy
        )
        
        return {
            "success": True,
            "dataset_id": result["dataset_id"],
            "algorithm_used": result["algorithm_used"],
            "execution_time_ms": result["execution_time_ms"],
            "data": result["results"],
            "model_metrics": result["model_metrics"]
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        traceback.print_exc()  # ← imprime el traceback completo en los logs
        print(f"\n🚨 ERROR DETALLADO: {type(e).__name__}: {e}\n")
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")