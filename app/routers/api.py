
from fastapi import APIRouter

from app.routers import ml_router

api_router=APIRouter()

#Registrar rutas con sintaxis

'''
api_router.include_router(
    sync_router.router,
    tags=["Internal Pipeline"]
)

'''

#Router Registrado Ml

api_router.include_router(
    ml_router.router,
    tags=["Machine Learning"]  # ← sin prefix aquí
)