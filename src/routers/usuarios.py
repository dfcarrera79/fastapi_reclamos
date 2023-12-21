import fastapi
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from utils import utils
import db_config

# Establish connections to PostgreSQL databases for "reclamos" and "apromed" respectively
db_uri1 = db_config.db_uri1
engine1 = create_engine(db_uri1)

db_uri2 = db_config.db_uri2
engine2 = create_engine(db_uri2)

# API Route Definitions
router = fastapi.APIRouter()

@router.get("/validar_usuario")
async def validar_usuario(id: str, clave: str, appCodigo: int):
  if(appCodigo == 1):
    return await validar_cliente(id, clave)
  elif(appCodigo == 2):
    return await usuario_sistema(id, clave)
  else:
    return JSONResponse({'error': "S", 'mensaje': "El código de aplicación no es correcto"})

@router.get("/validar_cliente")
async def validar_cliente(id: str, clave: str):
  sql = f"SELECT * FROM usuario WHERE TRIM(ruc_cliente) LIKE '{id.strip()}'"
  try:
    with Session(engine1) as session:
      rows = session.execute(text(sql)).fetchall()
      if len(rows) == 0:
        respuesta = cliente_sistema(id)
        if respuesta["error"] == "S":
          return respuesta
        usuario = respuesta["objetos"]
        return usuario
      else:
        clienteApp = rows[0]
        if clienteApp["clave"] == utils.codify(clave):
          return {"error": "N", "mensaje": "", "objetos": clienteApp}
        else:
          return {
            "error": "S",
            "mensaje": f"Hola {clienteApp['razon_social']}, tu clave de acceso ingresada no es correcta, no puede acceder al sistema",
            "objetos": rows,
          }
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}  

@router.get("/cliente_sistema")
async def cliente_sistema(id: str):
  sql = f"SELECT clp_cedruc AS ruc_cliente, clp_descri AS razon_social, clp_contacto AS nombre_comercial, '' AS clave WHERE clp_cedruc LIKE '{id.strip()}'"
  try:
    with Session(engine2) as session:
      rows = session.execute(text(sql)).fetchall()
      objetos = [row._asdict() for row in rows]
      if len(objetos) == 0:
        return {
          "error": "S",
          "mensaje": f"No existe un cliente con el RUC Nro. {id} registrado en el sistema contable",
        }
      else:
        return {
          "error": "N",
          "mensaje": "",
          "objetos": objetos[0],
        }    
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}   

@router.get("/usuario_sistema")  
async def usuario_sistema(id: str, clave: str):
  sql = f"SELECT usu_login AS ruc_cliente, usu_nomape AS razon_social, usu_nomape AS nombre_comercial, usu_clave AS clave FROM usuario.TUsuario WHERE TRIM(usu_login) LIKE '{id.strip()}'"
  try:
    with Session(engine2) as session:
      rows = session.execute(text(sql)).fetchall()
      objetos = [row._asdict() for row in rows]
      if len(objetos) == 0:
        return {
          "error": "S",
          "mensaje": "El login ingresado no está registrado en el sistema contable",
        }
      else:
        usuario = objetos[0]
        ok = usuario['clave'] == utils.codify(clave)
        return {
          'error': "N" if ok else "S",
          'mensaje': "" if ok else f"Hola {usuario['razon_social']}, la clave ingresada no es correcta",
          'objetos': usuario if ok else None,
        }        
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}    