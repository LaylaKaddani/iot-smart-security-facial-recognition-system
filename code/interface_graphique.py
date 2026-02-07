"""
Interface graphique PyQt5
"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from picamera2.previews.qt import QGlPicamera2
import cv2
import os

class DialogueEnregistrement(QtWidgets.QDialog):
    """Dialogue pour enregistrer une nouvelle personne"""
    
    def __init__(self, image_prechargee=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enregistrer une personne")
        self.setFixedSize(300, 150)
        
        # Widgets
        self.champ_nom = QtWidgets.QLineEdit(self)
        self.champ_nom.setPlaceholderText("Entrez le nom")
        self.champ_nom.setGeometry(50, 20, 200, 30)
        
        self.champ_email = QtWidgets.QLineEdit(self)
        self.champ_email.setPlaceholderText("Entrez l'email")
        self.champ_email.setGeometry(50, 60, 200, 30)
        
        self.bouton_charger = QtWidgets.QPushButton("Charger l'image", self)
        self.bouton_charger.setGeometry(100, 100, 100, 30)
        self.bouton_charger.clicked.connect(self.charger_et_sauvegarder)
        
        self.image = image_prechargee
    
    def charger_et_sauvegarder(self):
        """Charge une image et sauvegarde la personne"""
        from reconnaissance_faciale import sauvegarder_image_et_nom
        
        nom = self.champ_nom.text().strip()
        email = self.champ_email.text().strip()
        
        if not nom or self.image is None:
            QtWidgets.QMessageBox.critical(self, "Erreur", 
                                         "Veuillez saisir un nom et charger une image.")
            return
        
        # Sauvegarder l'utilisateur
        if sauvegarder_image_et_nom("known_faces", nom, email, self.image):
            QtWidgets.QMessageBox.information(self, "Succès", 
                                            "Enregistrement réussi !")
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Erreur", 
                                         "Échec de l'enregistrement.")

class DialogueSuppression(QtWidgets.QDialog):
    """Dialogue pour supprimer une personne"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Supprimer une personne")
        self.setFixedSize(300, 100)
        
        self.champ_nom = QtWidgets.QLineEdit(self)
        self.champ_nom.setPlaceholderText("Entrez le nom")
        self.champ_nom.setGeometry(50, 20, 200, 30)
        
        self.bouton_supprimer = QtWidgets.QPushButton("Supprimer", self)
        self.bouton_supprimer.setGeometry(100, 60, 100, 30)
        self.bouton_supprimer.clicked.connect(self.supprimer_personne)
    
    def supprimer_personne(self):
        """Supprime une personne de la base de données"""
        from base_de_donnees import supprimer_employe
        from notification_email import expediteur_email
        
        nom_personne = self.champ_nom.text().strip()
        
        if nom_personne:
            chemin_image = os.path.join("known_faces", f"{nom_personne}.jpg")
            
            if os.path.exists(chemin_image):
                # Supprimer les fichiers images
                os.remove(chemin_image)
                for fichier in os.listdir("known_faces"):
                    if fichier.startswith(f"{nom_personne}_aug_"):
                        os.remove(os.path.join("known_faces", fichier))
                
                # Supprimer de la base de données
                supprimer_employe(nom_personne)
                
                # Envoyer email de notification
                expediteur_email.envoyer_email_alerte(
                    "Utilisateur supprimé",
                    f"L'utilisateur '{nom_personne}' a été supprimé du système.",
                    chemin_image,
                    nom_personne,
                    'admin@votre-entreprise.com'
                )
                
                QtWidgets.QMessageBox.information(self, "Succès", 
                                                f"{nom_personne} supprimé avec succès.")
                self.accept()
            else:
                QtWidgets.QMessageBox.critical(self, "Erreur", 
                                             f"{nom_personne} non trouvé.")
        else:
            QtWidgets.QMessageBox.critical(self, "Erreur", 
                                         "Veuillez entrer un nom.")

class FenetrePrincipale(QtWidgets.QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        self.setWindowTitle("Système de Sécurité - Reconnaissance Faciale")
        self.setGeometry(100, 100, 820, 700)
        
        # Widget central
        widget_central = QtWidgets.QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QtWidgets.QVBoxLayout()
        widget_central.setLayout(layout_principal)
        
        # Prévisualisation caméra
        self.previsualisation_camera = QGlPicamera2(camera, width=800, height=600)
        layout_principal.addWidget(self.previsualisation_camera)
        
        # Barre d'outils
        barre_outils = QtWidgets.QToolBar()
        self.addToolBar(barre_outils)
        
        # Boutons
        self.bouton_verifier = QtWidgets.QPushButton("Vérifier")
        self.bouton_verifier.clicked.connect(self.verifier_visage)
        barre_outils.addWidget(self.bouton_verifier)
        
        self.bouton_admin = QtWidgets.QPushButton("Admin")
        self.bouton_admin.clicked.connect(self.authentifier_admin)
        barre_outils.addWidget(self.bouton_admin)
        
        # Démarrer la caméra
        camera.start()
    
    def verifier_visage(self):
        """Lance la vérification faciale"""
        # Cette fonction sera connectée au worker de vérification
        print("Vérification en cours...")
    
    def authentifier_admin(self):
        """Authentifie l'administrateur"""
        mot_de_passe, ok = QtWidgets.QInputDialog.getText(
            self,
            "Authentification Admin",
            "Entrez le mot de passe admin :",
            QtWidgets.QLineEdit.Password
        )
        
        if ok and mot_de_passe.strip() == "admin123":  # juste un exemple, Faut changer
            print("Authentification admin réussie")
            # Ouvrir le panneau admin
        else:
            QtWidgets.QMessageBox.critical(
                self,
                "Échec de l'authentification",
                "Mot de passe incorrect."
            )
    
    def fermer_evenement(self, event):
        """Gère la fermeture de la fenêtre"""
        self.camera.stop()
        super().closeEvent(event)
