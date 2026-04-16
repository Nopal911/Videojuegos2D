# bloque try -except
try:
    resultado = 10 / 1
except Exception as e:
    print(f"Se ha producido un error: {e}")
finally:
    print("Ejecución finalizada.")
