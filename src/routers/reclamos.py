import json
import fastapi
from datetime import date
from fastapi import Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.sql import text 
import db_config

# Establish connections to PostgreSQL databases for "reclamos" and "apromed" respectively
db_uri1 = db_config.db_uri1
engine1 = create_engine(db_uri1)

db_uri2 = db_config.db_uri2
engine2 = create_engine(db_uri2)

# API Route Definitions
router = fastapi.APIRouter()

@router.get("/obtener_factura") 
async def obtener_factura(ruc_cliente: str, numero_factura: str):
  try:
    with Session(engine2) as session:
      sql = f"SELECT TEgreso.trn_compro AS no_factura, TEgreso.trn_fecreg AS fecha_factura, TReferente.clp_cedruc AS ruc_cliente, TReferente.clp_descri AS razon_social, TReferente.clp_contacto AS nombre_comercial, TReferente.clp_calles AS direccion, TReferente.ciu_descri AS ciudad, TReferente.celular AS telefonos, TReferente.email, TEgreso.trn_codigo FROM comun.TEgreso INNER JOIN referente.TReferente ON TEgreso.clp_codigo = TReferente.clp_codigo WHERE TRIM(TReferente.clp_cedruc) LIKE '{ruc_cliente}' AND TRIM(TEgreso.trn_compro) LIKE '{numero_factura}' AND TEgreso.doc_codigo = 1 AND TEgreso.trn_valido = 0"
      rows = session.execute(text(sql)).fetchall()   
      objetos = [row._asdict() for row in rows]
      return {"error": "N", "mensaje": "", "objetos": objetos}  
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}  

@router.get("/obtener_productos") 
async def obtener_productos(ruc_reclamante: str, no_factura: str):
  respuesta = await obtener_factura(ruc_reclamante, no_factura)
  print('[RESPUESTA]: ', respuesta)
  if respuesta["error"] == "S" or len(respuesta["objetos"]) == 0:
    return JSONResponse(respuesta)
  factura = respuesta['objetos']
  sql = f"SELECT TArticulo.art_codigo, TArticulo.art_codbar, TArticulo.art_nomlar, TDetEgre.dt_cant, TDetEgre.dt_lote, TDetEgre.dt_fecha, TDetEgre.conteo_pedido FROM articulo.TArticulo INNER JOIN comun.TDetEgre ON TArticulo.art_codigo = TDetEgre.art_codigo AND TDetEgre.trn_codigo = {factura[0]['trn_codigo']} ORDER BY TArticulo.art_nomlar"
  try: 
    with Session(engine2) as session:
      rows = session.execute(text(sql)).fetchall()
      objetos = [row._asdict() for row in rows]
      return {"error": "N", "mensaje": "", "objetos": objetos} 
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}  
  
@router.post("/detalle_reclamo")  
async def detalle_reclamo(id_reclamo, tipo, reclamos, ruc_reclamante, razon_social):
  sql = f"INSERT INTO detalle_reclamo VALUES(DEFAULT, '{id_reclamo}', '{tipo}', '{reclamos}', current_timestamp, '{ruc_reclamante}', '{razon_social}') RETURNING id_detalle" 
  try:
    with Session(engine1) as session:
      rows = session.execute(text(sql)).fetchall()
      session.commit()
      rows_response = rows[0]
      return JSONResponse({ "error": "N",
        "mensaje": "Reclamo agregado exitosamente",
        "objetos": rows_response['id_detalle'],
      })
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}  

@router.post("/insertar_detalle")
def insertar_detalle(id_reclamo, detalle, razon_social):
  sql = "INSERT INTO detalle_reclamo VALUES(DEFAULT, :id_reclamo, :tipo, :detalle_values, current_timestamp, :ruc_reclamante, :razon_social) RETURNING id_detalle"
  try:
    with Session(engine1) as session:
      rows = session.execute(text(sql), {
        'id_reclamo': id_reclamo,
        'tipo': detalle['tipo'],
        'detalle_values': detalle['reclamos'],
        'ruc_reclamante': detalle['ruc_reclamante'],
        'razon_social': razon_social
      }).fetchall()
      session.commit()
      objetos = [row._asdict() for row in rows]
      rows_response = objetos[0]
      return JSONResponse(content={
        "error": "N",
        "mensaje": "Reclamo agregado exitosamente",
        "objetos": rows_response['id_detalle'],
      })
  except Exception as e:
    return {"error": "S", "mensaje": str(e)}
  
@router.post("/crear_detalle")
async def crear_detalle(request: Request):
  detalle_str = await request.body()
  detalle = json.loads(detalle_str)
  respuesta = await obtener_factura(detalle["ruc_reclamante"], detalle["no_factura"])
  if respuesta['error'] == "S":
    return JSONResponse(content=respuesta)
  factura = respuesta['objetos'][0]
  sql = f"INSERT INTO reclamo (no_factura, fecha_reclamo, fecha_factura, ruc_cliente, razon_social, nombre_comercial, direccion, ciudad, telefonos, email, trn_codigo) VALUES('{factura['no_factura']}', current_timestamp, '{factura['fecha_factura']}', '{factura['ruc_cliente']}', '{factura['razon_social']}', '{factura['nombre_comercial']}', '{factura['direccion']}', '{factura['ciudad']}', '{factura['telefonos']}', '{factura['email']}', '{factura['trn_codigo']}') ON CONFLICT ON CONSTRAINT reclamo_unico DO UPDATE SET no_factura=EXCLUDED.no_factura RETURNING id_reclamo, estado, razon_social"

  try:
    with Session(engine1) as session:
      rows = session.execute(text(sql)).fetchall()
      session.commit()
      objetos = [row._asdict() for row in rows]
      rows_response = objetos[0]
      id_reclamo, estado, razon_social = rows_response['id_reclamo'], rows_response['estado'], rows_response['razon_social']
      
      if estado == 'FIN':
        return JSONResponse(content={
          'error': 'S',
          'mensaje': 'El reclamo ya está finalizado, no es posible agregar detalles',
          'objetos': {'id_reclamo': id_reclamo, 'estado': estado, 'razon_social': razon_social}
        })
      return insertar_detalle(id_reclamo, detalle, razon_social)   
  except Exception as e:
      return {"error": "S", "mensaje": str(e)}

@router.get("/reclamos_por_ruc/{ruc}")
async def reclamos_por_ruc(
  ruc: str,
  factura: str = None,
  estado: str = None,
  desde: str = None,
  hasta: str = None,
):
  sql = f"SELECT reclamo.estado, ruc_reclamante, reclamo.no_factura, reclamo.id_reclamo, reclamo.fecha_reclamo, reclamo.fecha_factura, nombre_reclamante, id_detalle, reclamo.nombre_usuario, reclamo.fecha_enproceso, reclamo.fecha_finalizado, reclamo.respuesta_finalizado, reclamos FROM detalle_reclamo JOIN reclamo ON detalle_reclamo.id_reclamo = reclamo.id_reclamo WHERE ruc_reclamante='{ruc}'"
        
  if factura not in [None, '']:
    sql += f" AND reclamo.no_factura LIKE '{factura}'"
  if estado not in [None, '']:
    sql += f" AND reclamo.estado LIKE '{estado}'"
  if desde not in [None, ''] and hasta not in [None, '']:
    sql += f" AND CAST(reclamo.fecha_reclamo AS DATE) BETWEEN '{desde}' AND '{hasta}'"
  sql += " ORDER BY id_reclamo"

  try:
    with Session(engine1) as session:
      rows = session.execute(text(sql)).fetchall()
      objetos = [row._asdict() for row in rows]
      detalles = objetos[0]
      if len(rows) > 0:
        reclamo = {
          "fecha_factura": detalles["fecha_factura"],
          "ruc_reclamante": detalles["ruc_reclamante"],
          "detalles": detalles,
        }
        return {"error": "N", "mensaje": "", "objetos": reclamo}
      else:
        return {"error": "N", "mensaje": "", "objetos": 0}
  except Exception as e:
    return {"error": "S", "mensaje": str(e)} 
  
@router.get("/reclamos_por_estado/{estado}")
async def reclamos_por_estado(estado: str, factura: str = None, ruc: str = None, desde: str = None, hasta: str = None):
    sql = f"SELECT id_detalle, reclamo.id_reclamo, reclamo.fecha_reclamo, nombre_reclamante, ruc_reclamante, reclamo.no_factura, reclamo.fecha_factura, reclamo.fecha_enproceso, reclamo.fecha_finalizado, reclamo.respuesta_finalizado, reclamo.nombre_usuario, reclamos FROM detalle_reclamo JOIN reclamo ON detalle_reclamo.id_reclamo = reclamo.id_reclamo WHERE reclamo.estado LIKE '{estado}'"

    if factura not in [None, '']:
      sql += f" AND reclamo.no_factura LIKE '{factura}'"
    if ruc not in [None, '']:
      sql += f" AND reclamo.ruc_cliente = '{ruc}'"
    if desde not in [None, ''] and hasta not in [None, '']:
      sql += f" AND CAST(reclamo.fecha_reclamo AS DATE) BETWEEN '{desde}' AND '{hasta}'"
    sql += " ORDER BY id_reclamo"

    try:
      with Session(engine1) as session:
        rows = session.execute(text(sql)).fetchall()
        if len(rows) > 0:
          reclamos = [row._asdict() for row in rows]
          return {"error": "N", "mensaje": "", "objetos": reclamos}
        else:
          return {"error": "N", "mensaje": "", "objetos": 0}
    except Exception as e:
      return {"error": "S", "mensaje": str(e)}  
    
    