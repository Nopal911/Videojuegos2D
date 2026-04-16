
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 1. Configuraciones iniciales
paginas = ['/home', '/productos', '/contacto', '/blog', '/nosotros', 
           '/servicios', '/precios', '/faq', '/galeria', '/testimonios']
data = []
start_date = datetime(2024, 1, 1)

# 2. Generamos 300 registros de tráfico
print("Generando datos de tráfico web...")
for i in range(300):
    fecha = start_date + timedelta(days=np.random.randint(0, 90))
    
    # CORRECCIÓN: Usamos round(valor, decimales) de Python
    tasa_rebote = round(float(np.random.uniform(20, 80)), 1)
    
    data.append({
        'Fecha': fecha.strftime('%Y-%m-%d'),
        'Hora': f"{np.random.randint(0, 24):02d}:{np.random.randint(0, 60):02d}",
        'Página': np.random.choice(paginas),
        'Visitantes': np.random.randint(10, 500),
        'Sesiones': np.random.randint(15, 600),
        'Tiempo_Promedio_Seg': np.random.randint(30, 600), 
        'Tasa_Rebote_Porcentaje': tasa_rebote
    })

# 3. Creación del DataFrame y Limpieza
df = pd.DataFrame(data)

# Ordenamos por Fecha y Hora para que el histórico sea coherente
df = df.sort_values(['Fecha', 'Hora'])

# 4. Guardado y Feedback
df.to_csv('trafico_web.csv', index=False)

print("-" * 30)
print("¡Archivo 'trafico_web.csv' generado con éxito!")
print(f"Total de registros: {len(df)}")
print("\nVista previa de los datos:")
print(df.head())