import json
import datetime
import fastapi
from fastapi import Request
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from fastapi.responses import JSONResponse
from utils import db_config

## Models
class EstadoModel(BaseModel):
  id_reclamo: int
  estado: str
  login_usuario: Optional[str]
  nombre_usuario: Optional[str]
  respuesta_finalizado: Optional[str]

# Establish connections to PostgreSQL database for "reclamos"
# db_uri = "postgresql://postgres:01061979@localhost:5432/reclamos"
db_uri = db_config.db_uri1
engine = create_engine(db_uri)

# API Route Definitions
router = fastapi.APIRouter()

@router.put("/actualizar_estado")
async def actualizar_estado(data: EstadoModel):
  id_reclamo = data.id_reclamo 
  estado = data.estado
  login_usuario = data.login_usuario
  nombre_usuario = data.nombre_usuario
  respuesta_finalizado = data.respuesta_finalizado
  
  sql = ""

  if estado == "PEN":
    sql = f"UPDATE reclamo SET estado='PEN', fecha_enproceso=NULL, login_usuario=NULL, nombre_usuario=NULL WHERE id_reclamo='{id_reclamo}' RETURNING id_reclamo"

  if estado == "PRO":
    fecha = datetime.datetime.now().isoformat()
    sql = f"UPDATE reclamo SET estado='PRO', fecha_enproceso='{fecha}', login_usuario='{login_usuario}', nombre_usuario='{nombre_usuario}', respuesta_finalizado='{respuesta_finalizado}' WHERE id_reclamo='{id_reclamo}' RETURNING id_reclamo"

  if estado == "FIN":
    fecha = datetime.datetime.now().isoformat()
    sql = f"UPDATE reclamo SET estado='FIN', fecha_finalizado='{fecha}', login_usuario='{login_usuario}', nombre_usuario='{nombre_usuario}', respuesta_finalizado='{respuesta_finalizado}' WHERE id_reclamo='{id_reclamo}' RETURNING id_reclamo"
  
  try: 
    with Session(engine) as session:
      rows = session.execute(text(sql)).fetchall()
      session.commit()
      return JSONResponse({"error": "N", "mensaje": "Estado actualizado exitosamente", "objetos": rows[0][0]})
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}  
