import json
import fastapi
from fastapi import Request
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

# Establish connections to PostgreSQL databases for "reclamos"
db_uri = "postgresql://postgres:01061979@localhost:5432/reclamos"
engine = create_engine(db_uri)

# API Route Definitions
router = fastapi.APIRouter()

@router.get("/obtener_motivos")
async def obtener_motivos():
  try:
    with Session(engine) as session:
      rows = session.execute(text("SELECT * FROM motivo ORDER BY nombre_motivo")).fetchall()
      return {"error": "N", "mensaje": "", "objetos": rows}  
  except Exception as e:
      return {"error": "S", "mensaje": str(e)}  

@router.delete("/eliminar_motivo/{id_motivo}")
async def eliminar_motivo(id_motivo: int):
  try:
    with Session(engine) as session:
      query = text("DELETE FROM motivo WHERE id_motivo = :id_motivo")
      session.execute(query, {"id_motivo": id_motivo})
      session.commit()
      return {"error": "N", "mensaje": f"La fila con id: {id_motivo} se ha eliminado."}
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}  

@router.post("/crear_motivo")
async def crear_motivo(request: Request):
  motivo_str = await request.body()
  motivo = json.loads(motivo_str)
  try:
    with Session(engine) as session:
      sql = f"INSERT INTO motivo (nombre_motivo) VALUES('{motivo['nombre_motivo']}') RETURNING id_motivo" if motivo['id_motivo'] == 0 else f"UPDATE motivo SET nombre_motivo='{motivo['nombre_motivo']}' WHERE id_motivo='{motivo['id_motivo']}' RETURNING id_motivo"
      rows = session.execute(text(sql)).fetchall()
      session.commit()
      return {"error": "N", "mensaje": "", "objetos": rows}
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}