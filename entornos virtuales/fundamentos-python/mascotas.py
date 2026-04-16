#declaro una variable
nombre = "Firulais"
edad = 5
peso_kg = 2.5
esta_feliz = True
#Variable tipo lista
colores = ["dorado","blanco","negro"]

print(f"Mi mascota es {nombre} y su edad es {edad}.")
print("Mi mascota es", nombre, "y su edad es", edad, end=".\n")
print(f"Mi mascota pesa: {peso_kg}kg")
print(f"Mi mascota está:{ 'feliz' if esta_feliz else 'triste'}")
print(f"Mi mascota es de color:",end=" ")
for i, color in enumerate(colores):
    if i == len(colores)-1:
        print(color, end=".\n")
        break
    print(color, end=".")
    
#imprimir el tipo de cada una de las variables
print(f"mi variable nombre es de tipo: {type(nombre)}")
print(f"Mi variable edad es de tipo: {type(edad)}")
print(f"mi variable peso es de tipo {type(peso_kg)}")
print(f"mi variable esta feliz es de tipo{type(esta_feliz)}")
print(f"mi variable colores es de tipo {type(color)}")
print("=" *50)



#Crear la ficha de identificación de la mascota: nombre_mascota, tipo_mascota, 
# edad, edad_meses, esta_feliz, esta_vacunado, colores, 
# juguetes favoritos, peso_kg

nombre_mascota = "Beethoven"
tipo_mascota = "Perro"
edad = 11
edad_meses = edad * 12
esta_feliz = True
esta_vacunado = True
colores = ["café", "blanco"]
juguetes_favoritos = ["hueso de goma", "botella", "dona de goma"]
peso_kg = 22.5

print(f"Mi mascota es: {nombre_mascota}")
print(f"su edad en años es:{edad}, y su edad en meses es:{edad_meses}")
print(f"Mi mascota esta: {'feliz' if esta_feliz else 'triste'}")
print(F"Mi mascota esta vacunada: {'si' if esta_vacunado else 'no'}")
print(f"Mi mascota es de color:",end=" ")
for i, color in enumerate(colores):
    if i == len(colores)-1:
        print(color, end=".\n")
        break
    print(color, end=",")
print(f"Sus juguetes favoritos son:",end=" ")
for i, juguete in enumerate(juguetes_favoritos):
    if i == len(juguetes_favoritos)-1:
        print(juguete, end=".\n")
        break
    print(juguete, end=",")
print(f"Mi mascota pesa {peso_kg}kg \n")

#imprimir el tipo de cada una de las variables
print(f"mi variable nombre_mascota es de tipo: {type(nombre_mascota)}")
print(f"mi variable tipo_mascota es de tipo: {type(tipo_mascota)}")
print(f"mi variable edad es de tipo: {type(edad)}")
print(f"mi variable edad_meses es de tipo: {type(edad_meses)}")
print(f"mi variable esta_feliz es de tipo: {type(esta_feliz)}")
print(f"mi variable esta_vacunado es de tipo: {type(esta_vacunado)}")
print(f"mi variable colores es de tipo: {type(colores)}")
print(f"mi variable juguetes_favoritos es de tipo: {type(juguetes_favoritos)}")
print(f"mi variable peso_kg es de tipo: {type(peso_kg)}")