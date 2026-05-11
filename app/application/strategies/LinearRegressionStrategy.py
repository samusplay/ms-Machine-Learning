import time
from typing import Any, Dict, List

import numpy as np
from sklearn.linear_model import Ridge

from app.domain.prediction_strategy_interface import IPredictionStrategy


class LinearRegressionStrategy(IPredictionStrategy):

    def get_model_name(self) -> str:
        return "Ridge_Regression_Base_v1"

    def train_and_predict(
        self,
        zones_data: List[Dict[str, Any]],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        start_time = time.time()

       #Array con las variables que queremos tratar 
        features = ['poblacion', 'ingresos', 'competencia']
        X = np.array([[zone[f] for f in features] for zone in zones_data])

        w_vector = np.array([
            weights.get('peso_poblacion', 0.0),
            weights.get('peso_ingresos', 0.0),
            weights.get('peso_competencia', 0.0)
        ])

        model = Ridge(alpha=1.0)
        pseudo_y = X.dot(w_vector)
        model.fit(X, pseudo_y)
        predictions = model.predict(X)

       #Mandamos el resultado final
        results = []
        for i, zone in enumerate(zones_data):
            score = float(max(0.0, min(1.0, predictions[i])))
            label, color, summary = self._get_business_interpretation(score, zone, weights)
            results.append({
                "zone_code": zone["zone_code"],
                "potential_score": round(score, 2),
                "confidence": 0.98,
                "interpretation": {
                    "label": label,
                    "business_summary": summary
                },
                "color_code": color,
                "model_evidence": {
                    "algorithm": self.get_model_name(),
                    "main_factors": self._get_main_factors(zone, weights)
                }
            })

        execution_ms = int((time.time() - start_time) * 1000)

        return {
            "results": results,
            "execution_time_ms": execution_ms,
            "hyperparameters": {"alpha": 1.0},
            "metrics": {
                "n_zones": len(zones_data),
                "model": self.get_model_name(),
                "r2_score": round(float(model.score(X, pseudo_y)), 4),
            }
        }

    def _get_business_interpretation(self, score: float, zone: dict, weights: dict) -> tuple:
        if score >= 0.8:
            return (
                "Oportunidad de Oro", "#10b981",
                f"Zona {zone['zone_name']} con altísimo potencial: alta densidad territorial y baja competencia."
            )
        elif score >= 0.5:
            return (
                "Zona de Expansión", "#3b82f6",
                f"Zona {zone['zone_name']} con potencial moderado y margen de crecimiento sostenible."
            )
        else:
            return (
                "Riesgo Elevado", "#ef4444",
                f"Zona {zone['zone_name']} con baja tracción territorial según métricas actuales. No recomendada."
            )

    def _get_main_factors(self, zone: dict, weights: dict) -> List[dict]:
        factors = [
            {
                "factor": "Población",
                "impact": "Positivo (Alto)" if zone['poblacion'] > 0.7 else "Positivo (Medio)",
                "weight": weights.get('peso_poblacion', 0.0)
            },
            {
                "factor": "Ingresos",
                "impact": "Positivo (Alto)" if zone['ingresos'] > 0.5 else "Positivo (Medio)",
                "weight": weights.get('peso_ingresos', 0.0)
            },
            {
                "factor": "Competencia",
                "impact": "Penalización Alta" if zone['competencia'] > 0.5 else "Penalización Baja",
                "weight": weights.get('peso_competencia', 0.0)
            },
        ]
        factors.sort(key=lambda x: x["weight"], reverse=True)
        return factors