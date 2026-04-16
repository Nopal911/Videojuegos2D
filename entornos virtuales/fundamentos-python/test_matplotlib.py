import matplotlib.pyplot as plt

#datos de ejemplo
x = [0,1,2,3]
y = [0,1,4,9]

plt.bar(x,y, color='skyblue')
plt.title("grafica de barras")
plt.xlabel("categorias x")
plt.ylabel("valores y")

plt.show()
'''
#crear una figura y un eje
fig, ax = plt.subplots()
ax.plot(x, y, label='y = x^2')

#añadir titulo y etiquetas
ax.set_xlabel('x axis')
ax.set_ylabel('y axis')
ax.set_title('Simple Plot Example')
ax.legend()

#mostrar la grafica
plt.show()
'''