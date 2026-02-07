# iot-smart-security-facial-recognition-system

# 🛡️ Système de Sécurité Intelligent IoT avec Reconnaissance Faciale

## 📋 Description
Système de contrôle d'accès intelligent basé sur la reconnaissance faciale, déployé sur Raspberry Pi avec des mécanismes anti-spoofing.

## ✨ Fonctionnalités

### 💻 Interface
- Interface graphique intuitive avec PyQt5
- Panneau d'administration sécurisé
- Gestion des utilisateurs (ajout/suppression)
- Visualisation des logs d'accès en temps réel
- Exportation des données au format CSV
  
### 🔐 Sécurité
- Reconnaissance faciale en temps réel
- Détection de vivacité (anti-spoofing) par clignement d'yeux
- Analyse de texture pour détecter les photos imprimées
- Alertes email instantanées pour les intrusions

### 🤖 Contrôle Matériel
- **Servo Moteur** : Ouverture/fermeture automatique de la porte
- **LEDs** : Feedback visuel (verte = accès autorisé, rouge = refusé)
- **Buzzer** : Alarme sonore en cas d'intrusion
- **Capteur PIR** : Détection de mouvement pour déclencher la vérification
- **Raspberry Pi 4** : Cœur du système embarqué

### 🏗️ Infrastructure
- Base de données MongoDB pour le stockage des utilisateurs et logs
- Caméra Raspberry Pi avec traitement d'image en temps réel
- Architecture modulaire et extensible

## 🚀 Installation

### Prérequis
- Raspberry Pi 4
- Caméra Raspberry Pi
- Python 3.8+

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer MongoDB
sudo systemctl start mongodb

# 4. Lancer l'application
python main.py
