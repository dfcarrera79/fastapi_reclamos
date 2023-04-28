def motivos_from_rows(rows):
  motivos = []
  for row in rows:
    motivo = {
      "id_motivo": row[0],
      "nombre_motivo": row[1],
      "prioridad": row[2],
    }
    motivos.append(motivo)
  return motivos