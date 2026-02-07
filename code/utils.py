import cv2
import os
from PyQt5 import QtCore, QtGui, QtWidgets

def charger_image_vers_pixmap(chemin_image, largeur=None, hauteur=None):
    """
    Charge une image et la convertit en QPixmap avec les bonnes couleurs
    """
    if not os.path.exists(chemin_image):
        return None
    
    # Lire l'image avec OpenCV
    bgr = cv2.imread(chemin_image)
    if bgr is None:
        return None
    
    # Convertir BGR vers RGB
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape
    octets_par_ligne = ch * w
    
    # Créer QImage
    qimg = QtGui.QImage(rgb.data, w, h, octets_par_ligne, 
                        QtGui.QImage.Format_RGB888)
    
    # Convertir en QPixmap
    pixmap = QtGui.QPixmap.fromImage(qimg)
    
    # Redimensionner si nécessaire
    if largeur and hauteur:
        pixmap = pixmap.scaled(largeur, hauteur, 
                               QtCore.Qt.KeepAspectRatio, 
                               QtCore.Qt.SmoothTransformation)
    
    return pixmap

def capturer_image_camera(camera):
    """
    Capture une image depuis la caméra
    """
    try:
        array = camera.capture_array()
        image = array.copy()
        
        # Assurer le bon format
        if image.dtype != np.uint8:
            image = image.astype(np.uint8)
        
        # Supprimer le canal alpha si présent
        if image.ndim == 3 and image.shape[2] == 4:
            image = image[:, :, :3]
        
        return image
        
    except Exception as e:
        print(f"❌ Erreur lors de la capture: {e}")
        return None

def charger_image_fichier():
    """
    Charge une image depuis un fichier
    """
    options = QtWidgets.QFileDialog.Options()
    nom_fichier, _ = QtWidgets.QFileDialog.getOpenFileName(
        None, 
        "Charger une image", 
        "", 
        "Images (*.png *.jpg *.jpeg)", 
        options=options
    )
    
    if nom_fichier:
        image = cv2.imread(nom_fichier)
        if image is None:
            QtWidgets.QMessageBox.critical(None, "Erreur", 
                                         "Impossible de charger l'image.")
            return None
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    return None
