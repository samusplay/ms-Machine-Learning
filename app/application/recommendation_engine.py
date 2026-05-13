# app/application/recommendation_engine.py

from typing import List, Dict, Any


class RecommendationEngine:

    RULES = {

        "Competencia": {
            "message": "Desarrollar una estrategia de precios agresiva y fortalecer diferenciadores de marca.",
            "type": "risk"
        },

        "Población": {
            "message": "Incrementar campañas de captación y expansión comercial debido al alto flujo potencial de clientes.",
            "type": "opportunity"
        },

        "Ingresos": {
            "message": "Potenciar productos premium y estrategias de fidelización debido al alto poder adquisitivo.",
            "type": "opportunity"
        },

        "Infraestructura Vial": {
            "message": "Aprovechar la conectividad de la zona para impulsar estrategias logísticas y comerciales.",
            "type": "opportunity"
        },

        "Turismo": {
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

            # Buscar regla
            rule = cls.RULES.get(variable_name)

            if not rule:
                continue

            recommendations.append({
                "variable": variable_name,
                "impact": impact,
                "recommendation": rule["message"],
                "type": rule["type"]
            })

        # =====================================
        # ORDENAR POR MAYOR IMPACTO
        # =====================================
        recommendations.sort(
            key=lambda x: abs(x["impact"]),
            reverse=True
        )

        # =====================================
        # DEVOLVER SOLO TOP 5
        # =====================================
        return recommendations[:5]