"""
c'est pour la contrôle des composants matériels : Servo, LED, Buzzer, PIR
"""
import RPi.GPIO as GPIO
import time

class ControleurMateriel:
    
    def __init__(self):
        # Configuration des broches GPIO
        self.BROCHE_SERVO = 18      # PWM pour servo
        self.BROCHE_LED_VERTE = 23
        self.BROCHE_LED_ROUGE = 24
        self.BROCHE_BUZZER = 25
        self.BROCHE_PIR = 17        # Entrée pour capteur PIR
        
        # Initialisation GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Configurer les broches
        GPIO.setup(self.BROCHE_SERVO, GPIO.OUT)
        GPIO.setup(self.BROCHE_LED_VERTE, GPIO.OUT)
        GPIO.setup(self.BROCHE_LED_ROUGE, GPIO.OUT)
        GPIO.setup(self.BROCHE_BUZZER, GPIO.OUT)
        GPIO.setup(self.BROCHE_PIR, GPIO.IN)
        
        # Initialiser le servo
        self.servo = GPIO.PWM(self.BROCHE_SERVO, 50)  # 50Hz
        self.servo.start(0)
        
        # Éteindre tout au démarrage
        self.eteindre_tout()
    
    def ouvrir_porte(self):
        """Ouvre la porte avec le servo moteur"""
        print("🚪 Ouverture de la porte...")
        
        # Allumer LED verte
        GPIO.output(self.BROCHE_LED_VERTE, GPIO.HIGH)
        
        # Positionner le servo à 90° (porte ouverte)
        self.servo.ChangeDutyCycle(7.5)  # 90°
        time.sleep(1)
        
        # Garder LED verte allumée pendant 5 secondes
        time.sleep(5)
        
        # Fermer la porte
        self.fermer_porte()
    
    def fermer_porte(self):
        """Ferme la porte"""
        print("🚪 Fermeture de la porte...")
        
        # Positionner le servo à 0° (porte fermée)
        self.servo.ChangeDutyCycle(2.5)  # 0°
        time.sleep(1)
        
        # Éteindre LED verte
        GPIO.output(self.BROCHE_LED_VERTE, GPIO.LOW)
    
    def declencher_alarme(self):
        """Déclenche l'alarme pour accès non autorisé"""
        print("🚨 ALARME : Accès non autorisé !")
        
        # Allumer LED rouge
        GPIO.output(self.BROCHE_LED_ROUGE, GPIO.HIGH)
        
        # Activer le buzzer (bip bip)
        for _ in range(3):
            GPIO.output(self.BROCHE_BUZZER, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.BROCHE_BUZZER, GPIO.LOW)
            time.sleep(0.5)
        
        # Éteindre LED rouge après 3 secondes
        time.sleep(3)
        GPIO.output(self.BROCHE_LED_ROUGE, GPIO.LOW)
    
    def eteindre_tout(self):
        """Éteint tous les composants"""
        GPIO.output(self.BROCHE_LED_VERTE, GPIO.LOW)
        GPIO.output(self.BROCHE_LED_ROUGE, GPIO.LOW)
        GPIO.output(self.BROCHE_BUZZER, GPIO.LOW)
    
    def lire_capteur_pir(self):
        """Lit l'état du capteur PIR"""
        return GPIO.input(self.BROCHE_PIR)
    
    def nettoyer(self):
        """Nettoie les broches GPIO à la fermeture"""
        self.eteindre_tout()
        self.servo.stop()
        GPIO.cleanup()
        print("✅ GPIO nettoyé")

# Instance globale
controleur_materiel = ControleurMateriel()
