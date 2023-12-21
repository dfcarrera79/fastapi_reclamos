import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers import motivos, reclamos, archivos, estados, usuarios

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/public/imagenes_reclamos"), name="static")

# API endpoints
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)