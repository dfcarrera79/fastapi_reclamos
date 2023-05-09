from fastapi import FastAPI
from api import motivos, reclamos, archivos

app = FastAPI()

app.include_router(motivos.router)
app.include_router(reclamos.router)
app.include_router(archivos.router)