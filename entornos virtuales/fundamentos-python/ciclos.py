#ejemplo promts
promts = ["Hola", "Dame un poema", "explicame python"]

for p in promts:
    print(f"procesando el promt: {p}")
    
    #imprimir un rango de valores del 0 al 4
    for i in range(5):
        print(i)
        
    #tabla de multiplicar
    for i in range(1,11):
        print(f"5*{i}={5*i}")
        
#imprimir multiplos de 3 del 3 al 1000
for i in range(3,1001, 3):
    print(i, end=",")
    
#imprimir si un numero del 1 al 100 es par o non|
for i in range(1,101):
    if i % 2 > 0:
        print(f"{i} es non", end=", ")
    else:
        print(f"{i} es par", end=", ")
