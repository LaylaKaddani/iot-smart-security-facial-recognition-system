import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

# Variables globales
image_capturee = None
encodages_visages_connus = []
noms_visages_connus = []
image_verification = None

def augmenter_images(image):
    """Crée des variations d'images pour améliorer l'entraînement"""
    augmentations = {}
    
    # Retournement horizontal
    augmentations["retourne"] = cv2.flip(image, 1)
    
    # Rotation de 15 degrés
    (h, w) = image.shape[:2]
    centre = (w // 2, h // 2)
    M_rot15 = cv2.getRotationMatrix2D(centre, 15, 1.0)
    augmentations["rotation15"] = cv2.warpAffine(image, M_rot15, (w, h))
    
    # Augmentation de luminosité
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    hsv[:, :, 2] = cv2.add(hsv[:, :, 2], 30)
    augmentations["luminosite"] = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    
    return augmentations

def charger_encodages_dossier(dossier="known_faces"):
    """
    Charge tous les encodages faciaux depuis un dossier
    """
    global encodages_visages_connus, noms_visages_connus
    
    if not os.path.exists(dossier):
        os.makedirs(dossier)
        return {}
    
    encodages_personnes = {}
    
    for nom_fichier in os.listdir(dossier):
        if not nom_fichier.lower().endswith((".jpg", ".png", ".jpeg")):
            continue
        
        # Extraire le nom de base
        base = nom_fichier.split("_aug_")[0]
        if base not in encodages_personnes:
            encodages_personnes[base] = []
        
        chemin_image = os.path.join(dossier, nom_fichier)
        image_connue = face_recognition.load_image_file(chemin_image)
        encodages = face_recognition.face_encodings(image_connue)
        
        if encodages:
            encodages_personnes[base].append(encodages[0])
    
    return encodages_personnes

def verifier_visage(image, encodages_personnes):
    """
    Vérifie si un visage est reconnu
    """
    try:
        # S'assurer que l'image est contiguë
        image_rgb = np.ascontiguousarray(image)
        
        # Détecter les visages
        emplacements_visages = face_recognition.face_locations(image_rgb)
        encodages_visages = face_recognition.face_encodings(image_rgb, emplacements_visages)
        
        if len(encodages_visages) == 0:
            return "Inconnu", None
        
        # Comparer chaque visage détecté
        for encodage_visage in encodages_visages:
            meilleur_nom = None
            meilleure_distance = 1.0
            
            for personne, encodages_liste in encodages_personnes.items():
                distances = face_recognition.face_distance(encodages_liste, encodage_visage)
                if len(distances) > 0:
                    distance_min = np.min(distances)
                    if distance_min < meilleure_distance:
                        meilleure_distance = distance_min
                        meilleur_nom = personne
            
            # Seuil de reconnaissance
            if meilleur_nom is not None and meilleure_distance < 0.6:
                return meilleur_nom, emplacements_visages[0]
        
        return "Inconnu", None
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification faciale: {e}")
        return "Inconnu", None

def sauvegarder_image_et_nom(dossier, nom, email, image):
    """
    Sauvegarde l'image et enregistre la personne
    """
    from base_de_donnees import inserer_employe
    from notification_email import expediteur_email
    
    try:
        if not os.path.exists(dossier):
            os.makedirs(dossier)
        
        # Sauvegarder l'image de base
        chemin_base = os.path.join(dossier, f"{nom}.jpg")
        cv2.imwrite(chemin_base, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        
        # Créer des images augmentées
        images_augmentees = augmenter_images(image)
        for nom_aug, image_aug in images_augmentees.items():
            chemin_aug = os.path.join(dossier, f"{nom}_aug_{nom_aug}.jpg")
            cv2.imwrite(chemin_aug, cv2.cvtColor(image_aug, cv2.COLOR_RGB2BGR))
        
        # Enregistrer dans la base de données
        inserer_employe(nom, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Envoyer un email de confirmation
        expediteur_email.envoyer_email_alerte(
            "Nouvel utilisateur enregistré",
            f"L'utilisateur '{nom}' a été enregistré dans le système de sécurité.",
            chemin_base,
            email,
            'admin@votre-entreprise.com'
        )
        
        print(f"✅ Utilisateur {nom} enregistré avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement: {e}")
        return False
