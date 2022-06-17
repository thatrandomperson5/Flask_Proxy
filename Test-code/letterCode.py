import codecs

def Encode(object, **kwargs):
  try:
    restirctions = kwargs['restrictions']
  except KeyError:
    restirctions = ['$',';']
  object = object.encode()
  set = getset(restirctions, 'e')
  output = []
  n = 0

  object = str(object)
  object = object.replace("b'",'')[:-1]
  for x in object:
    
    output.append(set[x])
    n +=1
  return ''.join(output)
def Decode(object, **kwargs):
  try:
    restirctions = kwargs['restrictions']
  except KeyError:
    restirctions = ['$',';']
  set = getset(restirctions)
  output = []
  for i in range(0, len(object), 2):
    output.append(set[object[i:i+2]])
  output = str(''.join(output))
  print(output)
  output = codecs.encode(output, 'latin-1')
  
  
  
  #output = output.encode('latin-1')
  
  
  return output.decode()
def getset(restrictions, type='d'):
  list = []
  d = "'"
  e = "{}"
  values = f'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$&*(){d}"%-+=/;:,._^[]{e}|~\<>!? '
  set = {}
  for x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$;':
    if not x in restrictions:
      list.append(x)
  index = 0
  index2 = 0
  for x in values:
    
    t = list[index]
    t2 = list[index2]
    if type == 'e':
       set[x] = t+t2
    else:
       set[t+t2] = x
    if index2 == 35:
      index2 = 0
      index += 1
    index2 +=1
  return set
