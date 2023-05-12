from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import motivos, reclamos, archivos, estados, usuarios

app = FastAPI()

app.include_router(motivos.router)
app.include_router(reclamos.router)
app.include_router(archivos.router)
app.include_router(estados.router)
app.include_router(usuarios.router)

# Allow all origins in CORS configuration
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)