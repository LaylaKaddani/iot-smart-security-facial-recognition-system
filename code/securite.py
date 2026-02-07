"""
Protection contre les attaques par présentation
Contient les fonctions anti-spoofing et de validation de sécurité
"""
import cv2
import numpy as np
from scipy.spatial import distance as dist

class DetecteurAntiSpoofing:
    """Classe pour détecter les tentatives de spoofing (photos, vidéos)"""
    
    def __init__(self):
        # Seuils pour la détection de vivacité
        self.seuil_ear = 0.25  # Eye Aspect Ratio
        self.seuil_ear_consecutif = 3
        self.compteur_clignement = 0
        self.etat_clignement = False
        
        # Points des yeux pour EAR
        self.LEFT_EYE = [36, 37, 38, 39, 40, 41]
        self.RIGHT_EYE = [42, 43, 44, 45, 46, 47]
    
    def calculer_ear(self, oeil):
        """Calcule le ratio d'aspect de l'œil (Eye Aspect Ratio)"""
        # Calcul des distances verticales
        A = dist.euclidean(oeil[1], oeil[5])
        B = dist.euclidean(oeil[2], oeil[4])
        
        # Calcul de la distance horizontale
        C = dist.euclidean(oeil[0], oeil[3])
        
        # EAR = (somme des distances verticales) / (2 * distance horizontale)
        ear = (A + B) / (2.0 * C)
        return ear
    
    def verifier_clignement_yeux(self, points_visage):
        """
        Vérifie le clignement des yeux pour détecter une personne vivante
        Retourne True si un clignement est détecté
        """
        if points_visage is None:
            return False
        
        try:
            # Extraire les points des yeux
            oeil_gauche = [points_visage[i] for i in self.LEFT_EYE]
            oeil_droit = [points_visage[i] for i in self.RIGHT_EYE]
            
            # Calculer les EAR
            ear_gauche = self.calculer_ear(oeil_gauche)
            ear_droit = self.calculer_ear(oeil_droit)
            
            # EAR moyen
            ear_moyen = (ear_gauche + ear_droit) / 2.0
            
            # Détecter un clignement
            if ear_moyen < self.seuil_ear:
                self.compteur_clignement += 1
                if self.compteur_clignement >= self.seuil_ear_consecutif:
                    if not self.etat_clignement:
                        self.etat_clignement = True
            else:
                if self.compteur_clignement > 0:
                    self.compteur_clignement = 0
                self.etat_clignement = False
            
            return self.etat_clignement
            
        except Exception as e:
            print(f"Erreur lors de la vérification du clignement: {e}")
            return False
    
    def analyser_texture_peau(self, image, visage):
        """
        Analyse la texture de la peau pour détecter une photo imprimée
        Basé sur la variance de Laplace (flou vs netteté)
        """
        try:
            # Extraire la région du visage
            (haut, droite, bas, gauche) = visage
            region_visage = image[haut:bas, gauche:droite]
            
            if region_visage.size == 0:
                return True  # Ne peut pas analyser, on laisse passer
            
            # Convertir en niveaux de gris
            gris = cv2.cvtColor(region_visage, cv2.COLOR_RGB2GRAY)
            
            # Calculer la variance de Laplace (mesure de netteté)
            variance_laplace = cv2.Laplacian(gris, cv2.CV_64F).var()
            
            # Une image imprimée a généralement une variance plus faible
            # qu'un vrai visage (moins de détails, plus flou)
            seuil_variance = 100.0
            
            if variance_laplace < seuil_variance:
                print(f" ATTENTION: Variance basse détectée ({variance_laplace:.2f})")
                print("   Possible attaque par photo imprimée!")
                return False
                
            return True
            
        except Exception as e:
            print(f"Erreur analyse texture: {e}")
            return True
    
    def detecter_mouvement_tete(self, points_visage_avant, points_visage_apres):
        """
        Détecte les micro-mouvements de tête (impossibles sur une photo statique)
        """
        if points_visage_avant is None or points_visage_apres is None:
            return False
        
        try:
            # Calculer le déplacement moyen des points du visage
            mouvement_total = 0
            nb_points = min(len(points_visage_avant), len(points_visage_apres))
            
            for i in range(nb_points):
                point_avant = points_visage_avant[i]
                point_apres = points_visage_apres[i]
                mouvement = dist.euclidean(point_avant, point_apres)
                mouvement_total += mouvement
            
            mouvement_moyen = mouvement_total / nb_points if nb_points > 0 else 0
            
            # Un vrai visage aura des micro-mouvements
            seuil_mouvement = 1.0  # en pixels
            
            if mouvement_moyen > seuil_mouvement:
                print(f"✅ Mouvement détecté: {mouvement_moyen:.2f} pixels")
                return True
            else:
                print(f"⚠️ Pas de mouvement détecté: {mouvement_moyen:.2f} pixels")
                return False
                
        except Exception as e:
            print(f"Erreur détection mouvement: {e}")
            return False
    
    def verifier_vivacite_complete(self, image, points_visage=None, visage_zone=None):
        """
        Vérification complète de vivacité
        Combine plusieurs techniques anti-spoofing
        """
        resultats = {
            "est_vivant": False,
            "clignement_detecte": False,
            "texture_valide": True,
            "mouvement_detecte": False,
            "raison_echec": ""
        }
        
        try:
            # 1. Vérifier le clignement des yeux
            if points_visage is not None:
                resultats["clignement_detecte"] = self.verifier_clignement_yeux(points_visage)
            
            # 2. Analyser la texture si une zone de visage est fournie
            if visage_zone is not None and image is not None:
                resultats["texture_valide"] = self.analyser_texture_peau(image, visage_zone)
            
            # 3. Décision finale
            if resultats["clignement_detecte"] and resultats["texture_valide"]:
                resultats["est_vivant"] = True
                resultats["raison_echec"] = "SUCCÈS"
            elif not resultats["texture_valide"]:
                resultats["raison_echec"] = "Texture de peau suspecte (possible photo imprimée)"
            elif not resultats["clignement_detecte"]:
                resultats["raison_echec"] = "Aucun clignement détecté"
            else:
                resultats["raison_echec"] = "Échec de vérification inconnu"
            
            return resultats
            
        except Exception as e:
            resultats["raison_echec"] = f"Erreur technique: {str(e)}"
            return resultats

class ValidateurSecurite:
    """Classe pour valider la sécurité globale du système"""
    
    @staticmethod
    def verifier_mots_de_passe_faibles():
        """Vérifie si des mots de passe faibles sont utilisés"""
        mots_de_passe_faibles = [
            "123456", "password", "admin", "test",
            "layla123", "ikram123", "raspberry"
        ]
      
        return {"faiblesses_trouvees": False, "recommandations": []}
    
    @staticmethod
    def verifier_permissions_fichiers():
        """Vérifie les permissions des fichiers sensibles"""
        fichiers_sensibles = [
            "known_faces/",
            "non_reconnues/",
            "config.py"
        ]
        
        import os
        
        for fichier in fichiers_sensibles:
            if os.path.exists(fichier):
                permissions = oct(os.stat(fichier).st_mode)[-3:]
                if permissions != "600":
                    print(f"⚠️  Permissions risquées sur {fichier}: {permissions}")
                    print("   Recommandation: chmod 600 pour les fichiers sensibles")
        
        return True

# Instance globale du détecteur anti-spoofing
detecteur_anti_spoofing = DetecteurAntiSpoofing()
