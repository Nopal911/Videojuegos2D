import numpy as np

# Crear un array de numpy con los precios de tres productos
precios = np.array([100, 200, 300])

# Aplicar un descuento del 20% a cada precio
precios_con_descuento = precios * 0.8
print(f"{precios_con_descuento}")