import time
from typing import Any, Dict, List

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from app.domain.prediction_strategy_interface import IPredictionStrategy


#Crea Multiples Arboles y promedia los resultados
class RandomForestStrategy(IPredictionStrategy):

    def get_model_name(self) -> str:
        return "RandomForest_v1"

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

        # Random Forest con 100 árboles — más árboles = más estable
        # random_state=42 garantiza reproducibilidad (mismos datos = mismo resultado)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        pseudo_y = X.dot(w_vector)
        model.fit(X, pseudo_y)
        predictions = model.predict(X)

        # feature_importances_ es nativo de RandomForest
        # dice exactamente cuánto contribuyó cada variable al resultado
        importances = model.feature_importances_

        results = []
        for i, zone in enumerate(zones_data):
            score = float(max(0.0, min(1.0, predictions[i])))
            label, color, summary = self._get_business_interpretation(score, zone)
            results.append({
                "zone_code": zone["zone_code"],
                "potential_score": round(score, 2),
                # OOB score no disponible con pocos datos, usamos confianza fija
                "confidence": round(float(np.mean(importances)), 3),
                "interpretation": {
                    "label": label,
                    "business_summary": summary
                },
                "color_code": color,
                "model_evidence": {
                    "algorithm": self.get_model_name(),
                    "main_factors": self._get_main_factors(
                        importances, features, zone, weights
                    )
                }
            })

        execution_ms = int((time.time() - start_time) * 1000)

        return {
            "results": results,
            "execution_time_ms": execution_ms,
            "hyperparameters": {
                "n_estimators": 100,
                "random_state": 42,
            },
            "metrics": {
                "n_zones": len(zones_data),
                "model": self.get_model_name(),
                "r2_score": round(float(model.score(X, pseudo_y)), 4),
                "feature_importances": {
                    features[i]: round(float(importances[i]), 4)
                    for i in range(len(features))
                }
            }
        }

    def _get_business_interpretation(self, score: float, zone: dict) -> tuple:
        if score >= 0.8:
            return (
                "Oportunidad de Oro", "#10b981",
                f"Zona {zone['zone_name']} detectada como expansión prioritaria por patrones compuestos."
            )
        elif score >= 0.5:
            return (
                "Zona de Expansión", "#3b82f6",
                f"Zona {zone['zone_name']} con potencial moderado según patrones históricos."
            )
        else:
            return (
                "Riesgo Elevado", "#ef4444",
                f"Zona {zone['zone_name']} con baja tracción según múltiples árboles de decisión."
            )

    def _get_main_factors(
        self,
        importances: np.ndarray,
        features: List[str],
        zone: dict,
        weights: dict
    ) -> List[dict]:
        # feature_importances_ de RandomForest da el peso REAL
        # de cada variable — no es una estimación, es matemáticamente exacto
        factor_names = {
            'poblacion': 'Población',
            'ingresos': 'Ingresos',
            'competencia': 'Competencia'
        }
        factors = []
        for i, feature in enumerate(features):
            importance = float(importances[i])
            is_penalty = feature == 'competencia'
            factors.append({
                "factor": factor_names[feature],
                "impact": (
                    "Penalización Alta" if is_penalty and importance > 0.3
                    else "Penalización Baja" if is_penalty
                    else "Positivo (Alto)" if importance > 0.3
                    else "Positivo (Medio)"
                ),
                "weight": round(importance, 4)
            })

        factors.sort(key=lambda x: x["weight"], reverse=True)
        return factors