import asyncio
import os
import sys

# Añadimos la raíz del proyecto al path para que encuentre la carpeta 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infrastructure.clients.http_analytics_client import HttpAnalyticsClient
from app.infrastructure.clients.http_config_client import HttpConfigClient


async def smoke_test():
    print("🔍 Iniciando Prueba de Humo en red interna Docker...")
    
    # IMPORTANTE: Aquí NO usamos localhost, usamos el nombre del servicio de Docker
    # Estas variables ya deberían estar en tu docker-compose, pero las aseguramos aquí:
    os.environ["MS_ANALYTICS_URL"] = "http://ms-analytics:8000"
    os.environ["CONFIG_SERVICE_URL"] = "http://ms-configuration:8000"

    analytics = HttpAnalyticsClient()
    config = HttpConfigClient()

    try:
        # 1. Probar Configuración
        print("📡 Intentando conectar con ms-configuration...")
        weights = await config.get_active_weights()
        print(f"✅ Conexión exitosa. Pesos activos: {weights}")

        # 2. Probar Analítica
        dataset_id = "dataset_001" # Asegúrate de que este ID exista en tu DB de analítica
        print(f"📡 Intentando conectar con ms-analytics (Dataset: {dataset_id})...")
        zones = await analytics.get_normalized_zones(dataset_id)
        
        if len(zones) > 0:
            print(f"✅ Conexión exitosa. Se recibieron {len(zones)} zonas.")
            print(f"📊 Ejemplo de datos validados por Pydantic: {zones[0]}")
        else:
            print("⚠️ Conexión exitosa, pero el dataset no devolvió zonas.")

        print("\n🚀 ¡PIPELINE DE DATOS VERIFICADO! Los microservicios se hablan correctamente.")

    except Exception as e:
        print(f"\n❌ FALLO EN LA PRUEBA: {str(e)}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(smoke_test())