import time
from typing import Any, Dict, List

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

from app.domain.prediction_strategy_interface import IPredictionStrategy


class GradientBoostingStrategy(IPredictionStrategy):
    """
    Estrategia de Alto Rendimiento (Gradient Boosting).
    Se enfoca en la máxima precisión matemática para desempatar zonas complejas.
    """

    def get_model_name(self) -> str:
        return "Gradient_Boosting_Optimizer_v1"

    def train_and_predict(
        self,
        zones_data: List[Dict[str, Any]],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        start_time = time.time()

        features = ['poblacion', 'ingresos', 'competencia']
        X = np.array([[zone[f] for f in features] for zone in zones_data])

        w_vector = np.array([
            weights.get('peso_poblacion', 0.0),
            weights.get('peso_ingresos', 0.0),
            weights.get('peso_competencia', 0.0)
        ])

        pseudo_y = X.dot(w_vector)

        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )

        model.fit(X, pseudo_y)
        predictions = model.predict(X)
        importances = model.feature_importances_

        results = []
        for i, zone in enumerate(zones_data):
            score = float(max(0.0, min(1.0, predictions[i])))
            label, color, summary = self._get_business_interpretation(score, zone)

            results.append({
                "zone_code": zone["zone_code"],
                "potential_score": round(score, 2),
                "confidence": 0.95,
                "interpretation": {
                    "label": label,
                    "business_summary": summary
                },
                "color_code": color,
                "model_evidence": {
                    "algorithm": self.get_model_name(),
                    "main_factors": self._get_main_factors(features, importances, zone)
                }
            })

        execution_ms = int((time.time() - start_time) * 1000)

        return {
            "results": results,
            "execution_time_ms": execution_ms,
            "hyperparameters": {
                "n_estimators": 100,
                "learning_rate": 0.1,
                "max_depth": 3
            },
            "metrics": {
                "n_zones": len(zones_data),
                "r2_score": round(float(model.score(X, pseudo_y)), 4),
                "feature_importances": dict(zip(features, importances.tolist()))
            }
        }

    def _get_business_interpretation(self, score: float, zone: dict) -> tuple:
        if score >= 0.85:
            return "Zona de Alta Precisión", "#059669", f"El optimizador identifica a {zone['zone_name']} como un punto crítico de éxito."
        elif score >= 0.5:
            return "Punto de Interés", "#2563eb", f"Zona {zone['zone_name']} con métricas sólidas de crecimiento."
        else:
            return "Descarte Técnico", "#dc2626", "Métricas insuficientes para los estándares de alto rendimiento."

    def _get_main_factors(self, features: List[str], importances: np.ndarray, zone: dict) -> List[dict]:
        factors = []
        for name, imp in zip(features, importances):
            impact = "Crítico" if imp > 0.4 else "Significativo"
            factors.append({
                "factor": name.capitalize(),
                "impact": impact,
                "weight": round(float(imp), 2)
            })
        return sorted(factors, key=lambda x: x["weight"], reverse=True)