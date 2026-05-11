import time
from typing import Any, Dict, List

import numpy as np
from sklearn.neighbors import KNeighborsRegressor

from app.domain.prediction_strategy_interface import IPredictionStrategy


class KNNStrategy(IPredictionStrategy):

    def get_model_name(self) -> str:
        return "KNearestNeighbors_v1"

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

        # n_neighbors=3 significa que busca las 3 zonas más parecidas
        # Si tenemos pocas zonas ajustamos para no superar el total
        n_neighbors = min(3, len(zones_data))
        model = KNeighborsRegressor(n_neighbors=n_neighbors)
        pseudo_y = X.dot(w_vector)
        model.fit(X, pseudo_y)
        predictions = model.predict(X)

        # kneighbors retorna distancias e índices de los vecinos más cercanos
        # Lo usamos para explicar qué zonas son "gemelas" (CA3)
        distances, indices = model.kneighbors(X)

        results = []
        for i, zone in enumerate(zones_data):
            score = float(max(0.0, min(1.0, predictions[i])))
            label, color, summary = self._get_business_interpretation(
                score, zone, zones_data, indices[i]
            )
            results.append({
                "zone_code": zone["zone_code"],
                "potential_score": round(score, 2),
                # Confianza basada en qué tan cercanos son los vecinos
                # distancia 0 = idéntico, distancia alta = poco confiable
                "confidence": round(float(1 / (1 + np.mean(distances[i]))), 3),
                "interpretation": {
                    "label": label,
                    "business_summary": summary
                },
                "color_code": color,
                "model_evidence": {
                    "algorithm": self.get_model_name(),
                    "main_factors": self._get_main_factors(
                        zone, zones_data, indices[i], weights
                    )
                }
            })

        execution_ms = int((time.time() - start_time) * 1000)

        return {
            "results": results,
            "execution_time_ms": execution_ms,
            "hyperparameters": {
                "n_neighbors": n_neighbors,
            },
            "metrics": {
                "n_zones": len(zones_data),
                "model": self.get_model_name(),
                "r2_score": round(float(model.score(X, pseudo_y)), 4),
            }
        }

    def _get_business_interpretation(
        self,
        score: float,
        zone: dict,
        zones_data: List[dict],
        neighbor_indices: np.ndarray
    ) -> tuple:
        # Obtenemos los nombres de las zonas vecinas para el business_summary
        # Esto es el lenguaje de inversores — "zona similar a X y Y que ya son rentables"
        neighbor_names = [
            zones_data[idx]["zone_name"]
            for idx in neighbor_indices
            if zones_data[idx]["zone_code"] != zone["zone_code"]
        ]
        neighbors_text = " y ".join(neighbor_names[:2]) if neighbor_names else "zonas similares"

        if score >= 0.8:
            return (
                "Oportunidad de Oro", "#10b981",
                f"Zona {zone['zone_name']} comparte patrones con {neighbors_text}, "
                f"zonas de alto rendimiento comprobado."
            )
        elif score >= 0.5:
            return (
                "Zona de Expansión", "#3b82f6",
                f"Zona {zone['zone_name']} es análoga a {neighbors_text}. "
                f"Potencial moderado por analogía territorial."
            )
        else:
            return (
                "Riesgo Elevado", "#ef4444",
                f"Zona {zone['zone_name']} similar a {neighbors_text} "
                f"que presentan baja tracción en el histórico."
            )

    def _get_main_factors(
        self,
        zone: dict,
        zones_data: List[dict],
        neighbor_indices: np.ndarray,
        weights: dict
    ) -> List[dict]:
        # En KNN los factores se explican por comparación con los vecinos
        # calculamos la diferencia entre la zona actual y sus vecinos
        neighbor_zones = [zones_data[idx] for idx in neighbor_indices]

        factors = []
        for feature, name in [
            ('poblacion', 'Población'),
            ('ingresos', 'Ingresos'),
            ('competencia', 'Competencia')
        ]:
            zone_val = zone[feature]
            neighbor_avg = np.mean([n[feature] for n in neighbor_zones])
            is_penalty = feature == 'competencia'

            if is_penalty:
                impact = "Penalización Alta" if zone_val > neighbor_avg else "Penalización Baja"
            else:
                impact = "Positivo (Alto)" if zone_val >= neighbor_avg else "Positivo (Medio)"

            factors.append({
                "factor": name,
                "impact": impact,
                "weight": weights.get(f'peso_{feature}', 0.0)
            })

        factors.sort(key=lambda x: x["weight"], reverse=True)
        return factors