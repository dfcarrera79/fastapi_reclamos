from fastapi import FastAPI
from api import motivos

app = FastAPI()

app.include_router(motivos.router)