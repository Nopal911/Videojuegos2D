import pandas as pd
import numpy as np

categorias = ['Electrónica', 'Hogar', 'Oficina', 'Deportes', 'Juguetes']
proveedores = ['Proveedor A', 'Proveedor B', 'Proveedor C']
data = []

for i in range(150):
    data.append({
        'Código': f'PROD{i+1:04d}',
        'Producto': f'Producto {i+1}',
        'Categoría': np.random.choice(categorias),
        'Stock': np.random.randint(0, 100),
        # CAMBIO AQUÍ: Usamos round(valor, decimales)
        'Precio': round(np.random.uniform(10, 500), 2), 
        'Proveedor': np.random.choice(proveedores)
    })

df = pd.DataFrame(data)
df.to_csv('inventario.csv', index=False)
print("Archivo 'inventario.csv' creado exitosamente.")