import os
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# Añadir el directorio raíz de este microservicio al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi.testclient import TestClient
from app.main import app
from app.routers.ml_router import get_scoring_service, get_db

# Mock de ScoringService
mock_scoring_service = MagicMock()

def override_get_scoring_service():
    return mock_scoring_service

def override_get_db():
    return MagicMock()

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_scoring_service] = override_get_scoring_service
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_scoring_service, None)
    app.dependency_overrides.pop(get_db, None)
    mock_scoring_service.reset_mock()

def test_ml_health():
    client = TestClient(app)
    response = client.get("/api/v1/ml/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "ms-Machine Learning"

def test_execute_scoring_success():
    client = TestClient(app)
    
    # Mock result must match the full ZoneResultSchema structure
    mock_result = {
        "dataset_id": "dataset_abc",
        "algorithm_used": "RandomForest",
        "execution_time_ms": 250,
        "results": [
            {
                "zone_code": "001",
                "potential_score": 0.85,
                "confidence": 0.90,
                "interpretation": {"label": "HIGH", "business_summary": "Zona de alto potencial."},
                "color_code": "#00FF00",
                "model_evidence": {
                    "algorithm": "RandomForest",
                    "main_factors": [{"factor": "Poblacion", "impact": "HIGH", "weight": 0.4}]
                }
            }
        ],
        "model_metrics": {"accuracy": 0.92}
    }
    
    mock_scoring_service.execute_scoring_pipeline = AsyncMock(return_value=mock_result)
    
    payload = {"strategy": "default"}
    response = client.post("/api/v1/ml/execute/dataset_abc", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["algorithm_used"] == "RandomForest"
    assert data["execution_time_ms"] == 250
    assert data["data"][0]["zone_code"] == "001"
    mock_scoring_service.execute_scoring_pipeline.assert_called_once_with(
        dataset_id="dataset_abc",
        strategy_name="default"
    )

def test_execute_scoring_value_error():
    client = TestClient(app)
    mock_scoring_service.execute_scoring_pipeline = AsyncMock(side_effect=ValueError("Estrategia inválida"))
    
    payload = {"strategy": "invalid"}
    response = client.post("/api/v1/ml/execute/dataset_abc", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Estrategia inválida"

def test_get_prediction_by_zone_success():
    client = TestClient(app)
    
    mock_prediction = MagicMock()
    mock_prediction.zone_code = "001"
    mock_prediction.potential_score = 0.85
    mock_prediction.confidence = 0.9
    mock_prediction.label = "HIGH"
    mock_prediction.color_code = "GREEN"
    mock_prediction.algorithm = "RandomForest"
    
    with patch("app.routers.ml_router.SQLAlchemyModelRepository") as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo.get_last_prediction_by_zone.return_value = mock_prediction
        mock_repo_class.return_value = mock_repo
        
        response = client.get("/api/v1/ml/predictions/001")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["zone_code"] == "001"
        assert data["data"]["prediction"]["potential_value"] == 0.85
        assert data["data"]["prediction"]["business_label"] == "HIGH"
        mock_repo.get_last_prediction_by_zone.assert_called_once_with("001")

def test_get_prediction_by_zone_not_found():
    client = TestClient(app)
    
    with patch("app.routers.ml_router.SQLAlchemyModelRepository") as mock_repo_class:
        mock_repo = MagicMock()
        mock_repo.get_last_prediction_by_zone.return_value = None
        mock_repo_class.return_value = mock_repo
        
        response = client.get("/api/v1/ml/predictions/999")
        assert response.status_code == 404
        # FastAPI puts HTTPException detail in response.json()["detail"]
        detail = response.json()["detail"]
        assert detail["success"] is False
        assert detail["error"]["code"] == "ZONE_NOT_FOUND"
