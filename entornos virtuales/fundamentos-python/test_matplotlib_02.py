import matplotlib.pyplot as plt
import numpy as np

# Datos de ahorro y gasto de varios ahorradores
gasto_ahorradores = [10,15,20,25,30,12,18]
ahorro_ahorradores = [80,85,70,90,95,88,75]

# Datos de gasto y ahorro de varios compradores
gasto_compradores = [70,80,90,85,95,75,88]
ahorro_compradores = [20,15,10,25,5,18,12]

# Crear una figura para las gráficas
plt.figure(figsize=(8,5)) # Tamaño de la figura

# Graficar los datos de ahorradores y compradores
plt.scatter(gasto_ahorradores,ahorro_ahorradores, color='blue', label='ahorradores', s=100, edgecolors='black')
plt.scatter(gasto_compradores,ahorro_compradores, color='red', label='compradores', s=100, edgecolors='black')
plt.title("Segmentacion de clientes por IA", fontsize=14)
plt.xlabel("Gasto mensual", fontsize=12)
plt.ylabel("Ahorro mensual", fontsize=12)
plt.legend()
plt.show()