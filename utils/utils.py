def codify(_value):
  _value = _value.strip()
  posicionRecorrido = 0
  longitudCadena = len(_value)
  valorLetraenCurso = 0
  claveEncriptada = ""
  while (posicionRecorrido < longitudCadena):
    valorLetraenCurso = ord(_value[posicionRecorrido])
    valorLetraenCurso = (valorLetraenCurso * 2) - 5
    letraCHR = chr(valorLetraenCurso)
    claveEncriptada = claveEncriptada + letraCHR
    posicionRecorrido += 1
  return claveEncriptada
  
def deCodify(_value):
  _value = _value.strip()
  posicionRecorrido = 0
  longitudCadena = len(_value)
  valorLetraenCurso = 0
  claveDesencriptada = ""
  while (posicionRecorrido < longitudCadena):
    valorLetraenCurso = ord(_value[posicionRecorrido])
    valorLetraenCurso = (valorLetraenCurso + 5) / 2
    letraCHR = chr(valorLetraenCurso)
    claveDesencriptada = claveDesencriptada + letraCHR
    posicionRecorrido += 1
  return claveDesencriptada  