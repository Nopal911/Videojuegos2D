import pandas as pd

#definir diccionario de valores

data = {
    'Mensaje' : ["hola", "mundo"],
    'Pandas': ['funciona', 'bien']
}

#crear un DataFrame
df = pd.DataFrame(data)
print(df)

