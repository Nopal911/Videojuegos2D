import sys
# Importar componentes con la capitalización correcta
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

# Crea una aplicación (Nota la A mayúscula)
app = QApplication(sys.argv)

# Crear ventana (Nota la W mayúscula)
ventana = QWidget()
ventana.setWindowTitle("mi primera app en PyQt") # Corregido: setWindowTitle (con una sola 't')
ventana.setGeometry(300,  300, 400, 250) 

# Crea un texto (Nota la L mayúscula)
texto = QLabel("Alejandro Hernández González", ventana) 
texto.move(115, 110) 

ventana.show() 
sys.exit(app.exec())