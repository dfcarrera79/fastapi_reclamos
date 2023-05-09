import json
import fastapi
from fastapi import Request
from sqlalchemy import create_engine, text

router = fastapi.APIRouter()

db_uri = "postgresql://postgres:01061979@localhost:5432/reclamos"
engine = create_engine(db_uri)

@router.put("/actualizar_estado")
async def actualizar_estado(request: Request):
  reclamo_str = await request.body()
  reclamo = json.loads(reclamo_str)
  print('[RECLAMO]: ' ,reclamo)
  return reclamo