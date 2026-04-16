import urllib.request
import os

print("Descargando archivos del modelo DNN de OpenCV...")

# URLs oficiales del repositorio de OpenCV
url_proto = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
url_model = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"

# Descargar
if not os.path.exists("deploy.prototxt"):
    print("Descargando deploy.prototxt...")
    urllib.request.urlretrieve(url_proto, "deploy.prototxt")

if not os.path.exists("res10_300x300_ssd_iter_140000.caffemodel"):
    print("Descargando res10_300x300_ssd_iter_140000.caffemodel (Esto puede tardar unos segundos, son ~10MB)...")
    urllib.request.urlretrieve(url_model, "res10_300x300_ssd_iter_140000.caffemodel")

print("¡Descarga completa! Ya puedes ejecutar tu programa principal.")