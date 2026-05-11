# app/application/recommendation_engine.py

from typing import List, Dict, Any


class RecommendationEngine:

    RULES = {
        "Competencia Alta": {
            "message": "Desarrollar una estrategia de precios agresiva y fortalecer diferenciadores de marca.",
            "type": "risk"
        },

        "Infraestructura Vial": {
            "message": "Aprovechar la conectividad de la zona para impulsar estrategias logísticas y comerciales.",
            "type": "opportunity"
        },

        "Alta Densidad Poblacional": {
            "message": "Incrementar campañas de captación y expansión comercial debido al alto flujo potencial de clientes.",
            "type": "opportunity"
        },

        "Bajo Poder Adquisitivo": {
            "message": "Diseñar productos o servicios de bajo costo adaptados al mercado local.",
            "type": "risk"
        },

        "Turismo Elevado": {
            "message": "Implementar estrategias comerciales orientadas a visitantes y consumidores temporales.",
            "type": "opportunity"
        }
    }

    @classmethod
    def build_recommendations(
        cls,
        variables: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        recommendations = []

        for item in variables:

            variable_name = item.get("variable")
            impact = item.get("weight", 0)

            rule = cls.RULES.get(variable_name)

            if not rule:
                continue

            recommendations.append({
                "variable": variable_name,
                "impact": impact,
                "recommendation": rule["message"],
                "type": rule["type"]
            })

        return recommendations