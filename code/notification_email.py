"""
Gestion des notifications par email
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os

class ExpediteurEmail:
    """Classe pour envoyer des emails avec pièces jointes"""
    
    def __init__(self):
        # ⚠️ À REMPLACER PAR DES VARIABLES D'ENVIRONNEMENT EN PRODUCTION
        self.expediteur = 'votre_email@gmail.com'
        self.mot_de_passe = 'votre_mot_de_passe_app'
        
    def envoyer_email_alerte(self, sujet, message, chemin_piece_jointe=None, 
                           email_utilisateur=None, email_admin=None):
        """
        Envoie un email d'alerte avec pièce jointe optionnelle
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.expediteur
            msg['Subject'] = sujet
            
            # Ajouter date et heure
            maintenant = datetime.now()
            date_string = maintenant.strftime("%Y-%m-%d %H:%M:%S")
            message_complet = f"{message}\n\n**Système de Sécurité IoT**\nDate et Heure: {date_string}"
            
            msg.attach(MIMEText(message_complet, 'plain'))
            
            # Ajouter pièce jointe si fournie
            if chemin_piece_jointe and os.path.exists(chemin_piece_jointe):
                with open(chemin_piece_jointe, 'rb') as piece:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(piece.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 
                              f'attachment; filename= {os.path.basename(chemin_piece_jointe)}')
                msg.attach(part)
            
            # Définir les destinataires
            destinataires = []
            if email_utilisateur:
                destinataires.append(email_utilisateur)
            if email_admin:
                destinataires.append(email_admin)
            
            if not destinataires:
                print("⚠️  Aucun destinataire spécifié pour l'email")
                return False
            
            msg['To'] = ', '.join(destinataires)
            
            # Envoyer l'email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.expediteur, self.mot_de_passe)
            server.sendmail(self.expediteur, destinataires, msg.as_string())
            server.quit()
            
            print(f"✅ Email envoyé avec succès à {destinataires}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi de l'email : {str(e)}")
            return False

# Instance globale
expediteur_email = ExpediteurEmail()
