from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.database import Base, check_db_connection, engine
from app.routers.api import api_router


# Gestor de vida de la aplicación (lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\033[94m⚙️  Configurando servicios de Machine Learning..\033[0m")
    
    # 1. Creamos las tablas de transformación físicamente en Postgres
    try:
       
        Base.metadata.create_all(bind=engine)
        print("\033[92m✅ Tablas de Machine learning sincronizadas\033[0m")
    except Exception as e:
        print(f"\033[91m🚨 Error creando tablas en ms-ml: {e}\033[0m")

   
    if check_db_connection():
        print("\033[92m✅ PERSISTENCIA: Conectado a db_ml\033[0m")
    else:
        print("\033[91m🚨 PERSISTENCIA: Fallo al conectar a db_ml\033[0m")
    
    yield
    print("\033[93m\nFinalizando procesos de analytics...\033[0m")


app = FastAPI(
    title="API Machine Learning",
    description="API para gestionar entrenamiento de IA Machine Learning",
    version="1.0.0",
    lifespan=lifespan
)

#eSto incluye el archivo del router para no estar escribiendo rutas
app.include_router(api_router,prefix="/api/v1/ml")


@app.get("/api/v1/ml/health", tags=["IA"])
def health():
    return {"status": "ok", "service": "ms-ml"}