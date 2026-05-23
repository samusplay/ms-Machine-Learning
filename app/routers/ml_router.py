# app/routers/ml_router.py

import traceback
import uuid

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.application.scoring_service import ScoringService
from app.infrastructure.clients.http_analytics_client import HttpAnalyticsClient
from app.infrastructure.clients.http_audit_client import HttpAuditClient
from app.infrastructure.clients.http_config_client import HttpConfigClient
from app.infrastructure.database import get_db
from app.infrastructure.sqlalchemy_model_repository import SQLAlchemyModelRepository
from app.schemas.scoring import ScoringRequest, ScoringResponse

router = APIRouter()

def get_scoring_service(db: Session = Depends(get_db)) -> ScoringService:
    return ScoringService(
        analytics_client=HttpAnalyticsClient(),
        config_client=HttpConfigClient(),
        model_repository=SQLAlchemyModelRepository(db),
        audit_client=HttpAuditClient()
    )

@router.post("/execute/{dataset_id}", response_model=ScoringResponse)
async def execute_scoring(
    dataset_id: str,
    request: ScoringRequest,
    service: ScoringService = Depends(get_scoring_service),
    x_trace_id: str = Header(None, alias="X-Trace-Id")
):
    trace_id = x_trace_id or str(uuid.uuid4())
    try:
        result = await service.execute_scoring_pipeline(
            dataset_id=dataset_id, 
            strategy_name=request.strategy,
            trace_id=trace_id
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
    
@router.get("/predictions/{zone_code}")
def get_prediction_by_zone(
    zone_code: str,
    db: Session = Depends(get_db),
    x_trace_id: str = Header(None, alias="X-Trace-Id")
):
    trace_id = x_trace_id or str(uuid.uuid4())
    repo = SQLAlchemyModelRepository(db)
    prediction = repo.get_last_prediction_by_zone(zone_code)

    if not prediction:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "ZONE_NOT_FOUND",
                    "message": f"No existe predicción para la zona {zone_code}."
                },
                "trace_id": trace_id
            }
        )

    return {
        "success": True,
        "data": {
            "zone_code": prediction.zone_code,
            "prediction": {
                "potential_value": prediction.potential_score,
                "confidence_score": prediction.confidence,
                "business_label": prediction.label,
                "color_code": prediction.color_code,
            },
            "model_reference": prediction.algorithm,
        },
        "error": None,
        "trace_id": trace_id
    }