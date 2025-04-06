from fastapi import APIRouter
from .endpoints import users, experiments, analysis, execute_code

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(execute_code.router, prefix="/execute-code", tags=["code-execution"]) 