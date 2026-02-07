"""
Gestion de la base de données MongoDB
"""

from pymongo import MongoClient
from datetime import datetime

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["attendance_db"]
employees_collection = db["employees"]
verify_collection = db["verify"]
unauthorized_collection = db["unauthorized"]

def inserer_employe(nom, email, date_enregistrement):
    """Insère un nouvel employé dans la base de données"""
    try:
        employees_collection.insert_one({
            "nom": nom,
            "email": email,
            "date_enregistrement": date_enregistrement
        })
        print(f"✅ Employé {nom} inséré avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion : {e}")
        return False

def supprimer_employe(nom):
    """Supprime un employé de la base de données"""
    try:
        resultat = employees_collection.delete_one({"nom": nom})
        if resultat.deleted_count > 0:
            print(f"✅ Employé {nom} supprimé avec succès")
            return True
        else:
            print(f"⚠️  Employé {nom} non trouvé")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la suppression : {e}")
        return False

def inserer_verification(nom, date_verification):
    """Insère une vérification d'accès"""
    try:
        verify_collection.insert_one({
            "nom": nom,
            "date_verification": date_verification
        })
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion de vérification : {e}")
        return False

def inserer_non_autorise(chemin_image, date_detection):
    """Insère une détection non autorisée"""
    try:
        unauthorized_collection.insert_one({
            "chemin_image": chemin_image,
            "date_detection": date_detection
        })
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion non autorisée : {e}")
        return False

def obtenir_tous_employes():
    """Récupère tous les employés"""
    try:
        return list(employees_collection.find({}))
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des employés : {e}")
        return []

def obtenir_verifications():
    """Récupère toutes les vérifications"""
    try:
        return list(verify_collection.find({}))
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des vérifications : {e}")
        return []

def obtenir_non_autorises():
    """Récupère toutes les détections non autorisées"""
    try:
        return list(unauthorized_collection.find({}))
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des non autorisés : {e}")
        return []
