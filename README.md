# iot-smart-security-facial-recognition-system

# 🛡️ Système de Sécurité Intelligent IoT avec Reconnaissance Faciale

## 📋 Description
Système de contrôle d'accès intelligent basé sur la reconnaissance faciale, déployé sur Raspberry Pi avec des mécanismes anti-spoofing.

## ✨ Fonctionnalités

### 💻 Interface
- Interface graphique intuitive avec PyQt5
- Panneau d'administration sécurisé
- Gestion des utilisateurs (ajout/suppression)
- Journalisation complète des accès
  
### 🔐 Sécurité
- Reconnaissance faciale en temps réel
- Détection de vivacité (anti-spoofing) par clignement d'yeux
- Analyse de texture pour détecter les photos imprimées
- Alertes email instantanées pour les intrusions

### 🏗️ Infrastructure
- Base de données MongoDB pour le stockage
- Caméra Raspberry Pi avec traitement temps réel
- Intégration matérielle (PIR, servo, LED, buzzer)

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
