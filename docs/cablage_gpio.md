# Câblage des Composants Matériels

## Connexions GPIO du Raspberry Pi 4

### Servo Moteur (porte)
- **Signal (orange)** → GPIO 18 (PWM)
- **Alimentation (+ rouge)** → 5V
- **Masse (- marron)** → GND

### LED Verte (accès autorisé)
- **Anode (+)** → GPIO 23
- **Cathode (-)** → GND
- **Résistance** : 220Ω en série

### LED Rouge (accès refusé)
- **Anode (+)** → GPIO 24
- **Cathode (-)** → GND
- **Résistance** : 220Ω en série

### Buzzer (alarme)
- **+** → GPIO 25
- **-** → GND
- **Résistance** : 100Ω en série (optionnel)

### Capteur PIR (détection mouvement)
- **VCC** → 5V
- **OUT** → GPIO 17
- **GND** → GND
