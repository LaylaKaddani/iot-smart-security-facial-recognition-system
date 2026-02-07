import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import os
import cv2
import numpy as np
from datetime import datetime
import face_recognition
from PyQt5 import QtCore, QtGui, QtWidgets
from picamera2 import Picamera2

# Import des modules
from controle_materiel import controleur_materiel
from securite import detecteur_anti_spoofing, ValidateurSecurite
from base_de_donnees import *
from reconnaissance_faciale import *
from notification_email import expediteur_email
from interface_graphique import *
from utils import *

# ----------------------------------------------------------------------
# CONFIGURATION INITIALE
# ----------------------------------------------------------------------

# Initialiser la caméra
camera = Picamera2()
config_previsualisation = camera.create_preview_configuration({"size": (800, 768)})
camera.configure(config_previsualisation)

# ----------------------------------------------------------------------
# WORKER DE VÉRIFICATION (Thread)
# ----------------------------------------------------------------------

class WorkerVerification(QtCore.QObject):
    """Worker pour la vérification faciale dans un thread séparé"""
    
    resultat_pret = QtCore.pyqtSignal(str, object)  # nom, image
    termine = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
    
    @QtCore.pyqtSlot()
    def executer(self):
        """Exécute la vérification faciale"""
        global image_verification
        
        # Vérifier si le capteur PIR a détecté un mouvement
        # (optionnel : si tu veux que la vérification ne se déclenche que sur mouvement)
        # if not controleur_materiel.lire_capteur_pir():
        #     print("⚠️  Aucun mouvement détecté par le capteur PIR")
        #     self.resultat_pret.emit("__AUCUN_MOUVEMENT__", None)
        #     self.termine.emit()
        #     return
        
        # Capturer l'image
        image = capturer_image_camera(camera)
        image_verification = image
        
        if image is None:
            self.resultat_pret.emit("__CAPTURE_ECHOUEE__", None)
            self.termine.emit()
            return
        
        # Charger les encodages connus
        encodages_personnes = charger_encodages_dossier("known_faces")
        
        if not encodages_personnes:
            self.resultat_pret.emit("Inconnu", image)
            self.termine.emit()
            return
        
        # Vérifier le visage
        nom, zone_visage = verifier_visage(image, encodages_personnes)
        
        # Vérification de sécurité anti-spoofing
        if nom != "Inconnu":
            # Détecter les points du visage pour la vérification de vivacité
            image_rgb = np.ascontiguousarray(image)
            points_visage = face_recognition.face_landmarks(image_rgb)
            
            if points_visage:
                # Vérifier la vivacité
                resultat_vivacite = detecteur_anti_spoofing.verifier_vivacite_complete(
                    image, points_visage[0], zone_visage
                )
                
                if not resultat_vivacite["est_vivant"]:
                    print(f"⚠️  ALERTE ANTI-SPOOFING: {resultat_vivacite['raison_echec']}")
                    nom = "Inconnu"  # Rejeter même si reconnu
        
        self.resultat_pret.emit(nom, image)
        self.termine.emit()

# ----------------------------------------------------------------------
# FENÊTRE PRINCIPALE AVEC VÉRIFICATION
# ----------------------------------------------------------------------

class FenetrePrincipaleAvecVerification(FenetrePrincipale):
    """Fenêtre principale avec fonctionnalité de vérification"""
    
    def __init__(self, camera):
        super().__init__(camera)
        
    def verifier_visage(self):
        """Lance la vérification faciale dans un thread séparé"""
        self.worker = WorkerVerification()
        self.thread_worker = QtCore.QThread()
        
        self.worker.moveToThread(self.thread_worker)
        self.thread_worker.started.connect(self.worker.executer)
        self.worker.resultat_pret.connect(self.traiter_resultat_verification)
        self.worker.termine.connect(self.thread_worker.quit)
        
        self.thread_worker.start()
    
    def traiter_resultat_verification(self, nom, image):
        """Traite le résultat de la vérification"""
        if nom == "Inconnu":
            QtWidgets.QMessageBox.warning(self, "Non reconnu", 
                                        "Visage inconnu ou non détecté")
            
            # 🚨 DÉCLENCHER L'ALARME (LED rouge + buzzer)
            controleur_materiel.declencher_alarme()
            
            # Sauvegarder l'image non reconnue
            dossier_non_reconnus = "non_reconnues"
            if not os.path.exists(dossier_non_reconnus):
                os.makedirs(dossier_non_reconnus)
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            chemin_image = os.path.join(dossier_non_reconnus, 
                                      f"inconnu_{timestamp}.jpg")
            
            if image is not None:
                bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(chemin_image, bgr_image)
                
                # Insérer dans la base de données
                inserer_non_autorise(chemin_image, 
                                   datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                # Envoyer email d'alerte
                expediteur_email.envoyer_email_alerte(
                    "🚨 ALERTE: Personne non reconnue",
                    "Une personne non reconnue a été détectée par le système de sécurité.",
                    chemin_image,
                    None,  # Pas d'email utilisateur
                    'admin@votre-entreprise.com'  # Email admin
                )
        
        elif nom == "__CAPTURE_ECHOUEE__":
            QtWidgets.QMessageBox.critical(self, "Erreur caméra", 
                                         "La capture d'image a échoué")
        
        elif nom == "__AUCUN_MOUVEMENT__":
            # Optionnel : si tu utilises le PIR pour déclencher la vérification
            QtWidgets.QMessageBox.information(self, "Aucun mouvement", 
                                            "Aucun mouvement détecté par le capteur PIR.")
        
        else:
            QtWidgets.QMessageBox.information(self, "Reconnu", 
                                            f"✅ Bienvenue {nom} !")
            
            # 🚪 OUVRIR LA PORTE (servo + LED verte)
            controleur_materiel.ouvrir_porte()
            
            # Enregistrer l'accès autorisé
            inserer_verification(nom, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def fermer_evenement(self, event):
        """Gère la fermeture de la fenêtre"""
        # Arrêter la caméra
        self.camera.stop()
        
        # Nettoyer les broches GPIO
        controleur_materiel.nettoyer()
        
        print("✅ Système arrêté proprement")
        super().closeEvent(event)

# ----------------------------------------------------------------------
# FONCTION PRINCIPALE
# ----------------------------------------------------------------------

def main():
    """Fonction principale de l'application"""
    
    print("=" * 60)
    print("SYSTÈME DE SÉCURITÉ IoT - RECONNAISSANCE FACIALE")
    print("=" * 60)
    
    # Vérifier la sécurité du système
    validateur = ValidateurSecurite()
    rapport = validateur.generer_rapport_securite()
    
    print("\n🔍 Rapport de Sécurité Initial:")
    print("Points forts:")
    for point in rapport["points_forts"]:
        print(f"  ✓ {point}")
    
    print("\n⚠️  Recommandations critiques:")
    for recommandation in rapport["recommandations_critiques"][:3]:
        print(f"  • {recommandation}")
    
    print("\n" + "=" * 60)
    
    # Lancer l'application
    app = QtWidgets.QApplication(sys.argv)
    
    # Créer la fenêtre principale
    fenetre = FenetrePrincipaleAvecVerification(camera)
    fenetre.show()
    
    # Exécuter l'application
    code_sortie = app.exec_()
    
    # Nettoyer (fait dans fermer_evenement)
    print("\n✅ Application terminée")
    return code_sortie

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur")
        # Nettoyer en cas d'interruption
        controleur_materiel.nettoyer()
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        controleur_materiel.nettoyer()
