import os
import shutil
import random
import string
import fastapi
from PIL import Image
from src import db_config
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from fastapi import FastAPI, UploadFile, File
from fastapi.encoders import jsonable_encoder

## Models
class ArchivoModel(BaseModel):
	id_detalle: str
	filepath: str

class ArchivosModel(BaseModel):
	id_detalle: str
	id_archivo: str   

class RegistrarModel(BaseModel):
  filepath: str

# Establish connections to PostgreSQL databases for "reclamos"
db_uri = db_config.db_uri1
engine = create_engine(db_uri)

# API Route Definitions
app = FastAPI()
router = fastapi.APIRouter()

def generate_random_filename():
  # Generate a random string of letters and digits
  letters_digits = string.ascii_letters + string.digits
  random_filename = ''.join(random.choice(letters_digits) for _ in range(10))
  return random_filename

@router.post("/subir_archivo")
async def subir_archivo(file: UploadFile = File(...)):
  directorio = os.path.join(os.getcwd(), 'src', 'public', 'imagenes_reclamos')
  try:
    os.makedirs(directorio, exist_ok=True)
    
    # Generate a random filename
    random_filename = generate_random_filename()
    file_extension = os.path.splitext(file.filename)[1]
    random_filename_with_extension = random_filename + file_extension
    
    # Save the file with the random filename
    file_path = os.path.join(directorio, random_filename_with_extension)
    with open(file_path, "wb") as buffer:
      shutil.copyfileobj(file.file, buffer)
    
    # Convert the image to WebP format
    image = Image.open(file_path)
    webp_path = os.path.splitext(file_path)[0] + ".webp"
    image.save(webp_path, "WebP")
    
    # Delete the original image
    os.remove(file_path)
    
    # Concatenate directory and filename
    directory = os.path.join(directorio, os.path.basename(webp_path))

    return JSONResponse({
        "error": "N",
        "mensaje": "File uploaded and converted to WebP format successfully",
        "objetos": directory
    })
  except Exception as e:
    return JSONResponse({"error": "S", "mensaje": str(e)})

@router.post("/registrar_archivo")
async def registrar_archivo(data: RegistrarModel):
  filepath = data.filepath
  try:
    with Session(engine) as session:
      sql = f"INSERT INTO archivo (id_detalle, path) VALUES(0, '{filepath}') returning id_archivo"
      rows = session.execute(text(sql)).fetchall()
      session.commit()
      objetos = [row._asdict() for row in rows]
      return {"error": "N", "mensaje": "", "objetos": objetos}  
  except Exception as e:
    return {"error": "S", "mensaje": str(e)} 
  
@router.delete("/eliminar_archivos")
async def eliminar_archivos():
  try:
    with Session(engine) as session:
      session.execute(text("DELETE FROM archivo WHERE id_detalle = 0"))
      session.commit()
      return {"error": "N", "mensaje": "Archivos con id = 0 eliminados"}
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}
  
@router.put("/actualizar_archivos")
async def actualizar_archivos(data: ArchivosModel):
  id_detalle = data.id_detalle
  id_archivo = data.id_archivo
  sql = f"UPDATE archivo SET id_detalle = '{id_detalle}' WHERE id_archivo = '{id_archivo}'"
  try:
    with Session(engine) as session:
      session.execute(text(sql))
      session.commit()
      return JSONResponse(content=jsonable_encoder({"error": "N", "mensaje": "Archivo actualizado"}))
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}  

@router.get("/obtener_archivos/{id_archivo}")
async def obtener_archivos(id_archivo):
  try:
    with Session(engine) as session:
      rows = session.execute(text(f"SELECT path FROM archivo WHERE id_archivo={id_archivo}")).fetchall()
      objetos = [row._asdict() for row in rows]
      return {"error": "N", "mensaje": "", "objetos": objetos}  
  except Exception as e:
      return {"error": "S", "mensaje": str(e)}  
    