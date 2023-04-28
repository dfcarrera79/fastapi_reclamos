import fastapi
from sqlalchemy.orm import Session
from fastapi import Request
from sqlalchemy import create_engine, text
from utils import utils

router = fastapi.APIRouter()

db_uri = "postgresql://postgres:01061979@localhost:5432/reclamos"
engine = create_engine(db_uri)

@router.get("/obtener_motivos")
async def obtener_motivos():
  try:
    with Session(engine) as session:
      rows = session.execute(text("SELECT * FROM motivo ORDER BY nombre_motivo")).fetchall()

      # Convert the rows to a JSON object
      motivos = utils.motivos_from_rows(rows)

      return {"error": "N", "mensaje": "", "objetos": motivos}

  except Exception as e:
      return {"error": "S", "mensaje": str(e)}  
    
@router.delete("/eliminar_motivo/{id_motivo}")
async def eliminar_motivo(id_motivo: int):
  try:
    with Session(engine) as session:
      query = f"DELETE FROM motivo WHERE id_motivo={id_motivo}"
      print(query)
      rows = session.execute(text(f"DELETE FROM motivo WHERE id_motivo={id_motivo}")).fetchall()
      return {"error": "N", "mensaje": "", "objetos": rows}
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}  
    
# DELETE FROM motivo WHERE id_motivo='${id_motivo}'
    
# @router.post("/crear_motivo")   
# async def crear_motivo(request: Request):
#   motivo = await request.body()
#   try:
#     with Session(engine) as session:
#       rows = session.execute(text(f"INSERT INTO motivo (nombre_motivo) VALUES('{motivo.nombre_motivo}') RETURNING id_motivo")).fetchall()
#       return {"error": "N", "mensaje": "", "objetos": rows}

#   except Exception as e:
#       return {"error": "S", "mensaje": str(e)}  