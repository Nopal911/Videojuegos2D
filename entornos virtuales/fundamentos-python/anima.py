#declara una variable llamda edad y dependiendo de
#ella clasifica en niño cuando edad menor a 15, joven menor a 25
# adulto menor a 45 y adulto mayor en caso contrario
edad = 30
if edad < 0 or edad > 130:
    print("ingresee una edad valida")
elif edad < 15:
    print("niño")
elif edad < 25:
    print("joven")
elif edad < 45:
    print("adulto")
else:
    print("adulto mayor")
