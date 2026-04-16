import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time

# Listas base
empleados = ['Juan Pérez', 'María González', 'Carlos López', 'Ana Martínez',
             'Luis Rodríguez', 'Carmen Silva', 'Pedro Torres', 'Laura Ramírez']
departamentos = ['Ventas', 'IT', 'RRHH', 'Finanzas']
estados = ['Presente', 'Tarde', 'Ausente', 'Permiso']

data = []
start_date = datetime(2024, 1, 1)

# Generamos datos para cada empleado
for empleado in empleados:
    # Asignamos un departamento fijo al empleado para que el análisis sea coherente
    depto = np.random.choice(departamentos)
    
    for i in range(90):  # 90 días de registros
        fecha = start_date + timedelta(days=i)
        
        if fecha.weekday() < 5:  # Lunes a Viernes (0-4)
            # Probabilidades: 80% Presente, 10% Tarde, 5% Ausente, 5% Permiso
            estado = np.random.choice(estados, p=[0.8, 0.1, 0.05, 0.05])
            
            if estado == 'Ausente':
                entrada = 'N/A'
                salida = 'N/A'
            else:
                # Si llegó tarde, entra después de las 8:30. Si no, a las 8:00 aprox.
                h_entrada = 8 if estado == 'Presente' else 9
                m_entrada = np.random.randint(0, 15) if estado == 'Presente' else np.random.randint(0, 30)
                entrada = f"{h_entrada:02d}:{m_entrada:02d}"
                
                # Salida entre las 17:00 y las 18:59
                salida = f"{17 + np.random.randint(0, 2):02d}:{np.random.randint(0, 60):02d}"
            
            data.append({
                'Empleado': empleado,
                'Fecha': fecha.strftime('%Y-%m-%d'),
                'Hora_Entrada': entrada,
                'Hora_Salida': salida,
                'Estado': estado,
                'Departamento': depto
            })

df = pd.DataFrame(data)
# Guardamos sin problemas de redondeo ya que son strings y fechas
df.to_csv('asistencias.csv', index=False)
print("Archivo 'asistencias.csv' creado correctamente.")