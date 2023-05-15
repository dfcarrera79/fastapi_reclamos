import os
import shutil
import fastapi
from PIL import Image
from fastapi import File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from pydantic import BaseModel
from fastapi.responses import JSONResponse
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

router = fastapi.APIRouter()

db_uri = "postgresql://postgres:01061979@localhost:5432/reclamos"
engine = create_engine(db_uri)

## Request
@router.post("/subir_archivo")
async def subir_archivo(file: UploadFile = File(...)):
  directorio = os.path.join(os.getcwd(), 'public', 'imagenes_reclamos')
  try:
    os.makedirs(directorio, exist_ok=True)
    # Save the original file
    with open(os.path.join(directorio, file.filename), "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert the image to WebP format
    image_path = os.path.join(directorio, file.filename)
    image = Image.open(image_path)
    webp_path = os.path.splitext(image_path)[0] + ".webp"
    image.save(webp_path, "WebP")
    
    # Delete the original image
    os.remove(image_path)
    
    # Concatenate directory and filename
    directory = os.path.join(directorio, os.path.basename(webp_path))

    return JSONResponse({
            "error": "N",
            "mensaje": "File uploaded and converted to WebP format successfully",
            "objetos": directory
        })
  except Exception as e:
    return JSONResponse({"error": "S", "mensaje": str(e)})
  
# @router.post("/subir_foto")
# async def subir_foto(file: UploadFile = File(...)):
# 	with open(file.filename, "wb") as buffer:
# 		shutil.copyfileobj(file.file, buffer)

# 	# Open the image file
# 	with Image.open(file.filename) as im:
# 		# Save the image in webp format with the same name
# 		webp_path = os.path.splitext(file.filename)[0] + ".webp"
# 		im.save(webp_path, "webp")
			
# 	# Delete the original file
# 	os.remove(file.filename)
	
# 	return {"filename": os.path.basename(webp_path)}

@router.post("/registrar_archivo")
async def registrar_archivo(data: RegistrarModel):
  filepath = data.filepath
  try:
    with Session(engine) as session:
      sql = f"INSERT INTO archivo (id_detalle, path) VALUES(0, '{filepath}') returning id_archivo"
      id_archivo = session.execute(text(sql)).fetchall()
      session.commit()
      return {"error": "N", "mensaje": "", "objetos": id_archivo}
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
  print(sql)
  
  try:
    with Session(engine) as session:
      session.execute(text(sql))
      session.commit()
      return JSONResponse(content=jsonable_encoder({"error": "N", "mensaje": "Archivo actualizado"}))
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}  

@router.post("/actualizar_archivo")
async def actualizar_archivo(data: ArchivoModel):
  id_detalle = data.id_detalle
  filepath = data.filepath
  sql = f"INSERT INTO archivo (id_detalle, path) VALUES({id_detalle}, '{filepath}')"
  print('[SQL ARCHIVOS]: ', sql)
  try:
    with Session(engine) as session:
      session.execute(text(sql))
      session.commit()
      return {"error": "N", "mensaje": "", "objetos": []}
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}  
   
@router.get("/obtener_archivos/{id_archivo}")
async def obtener_archivos(id_archivo):
  try:
    with Session(engine) as session:
      rows = session.execute(text(f"SELECT path FROM archivo WHERE id_archivo={id_archivo}")).fetchall()
      return {"error": "N", "mensaje": "", "objetos": rows}
  except Exception as e:
      return {"error": "S", "mensaje": str(e)}  