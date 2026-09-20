# ✈️ AirRadar for Home Assistant

**AirRadar** est une intégration personnalisée pour Home Assistant permettant de détecter les avions passant à proximité de votre domicile et de recevoir des notifications selon leur **distance** et leur **altitude**.

AirRadar utilise :

* **ADSB.lol** pour récupérer les positions ADS-B des avions.
* **ADSBDB** pour enrichir les informations avec la compagnie aérienne et le trajet du vol.

Aucun récepteur ADS-B local, Raspberry Pi supplémentaire ou clé RTL-SDR n'est nécessaire.

> 🇬🇧 English documentation is available below.

---

# 🇫🇷 Français

## Présentation

AirRadar surveille automatiquement l'espace aérien autour de la position **Maison** configurée dans Home Assistant.

Lorsqu'un avion entre dans la zone définie et respecte les critères configurés, AirRadar peut envoyer une notification sur votre téléphone.

Par exemple :

> ✈️ **Avion proche de la maison**
> AFR1234 — Air France
> MRS → CDG · 1,42 km · 3 850 m · 742 km/h

---

## Fonctionnalités

* ✈️ Détection des avions autour de votre domicile
* 📍 Utilisation automatique de la position `Home` de Home Assistant
* 📏 Distance maximale d'alerte réglable
* 🛫 Altitude maximale d'alerte réglable
* 🔔 Notifications smartphone
* 🚫 Anti-doublon des notifications
* 🔄 Réarmement automatique après la sortie de la zone
* 🛰️ Données ADS-B via ADSB.lol
* 🏢 Identification de la compagnie aérienne
* 🗺️ Origine et destination du vol lorsque disponibles
* 🔢 Immatriculation de l'avion
* ✈️ Type / modèle de l'appareil
* 📊 Nombre d'avions détectés
* 📡 Avion le plus proche
* 🕒 Informations sur le dernier passage
* ⚡ Entité événement `Passage avion`
* ⚙️ Configuration depuis l'interface Home Assistant
* 🏠 Aucun matériel ADS-B local nécessaire
* 📦 Installation et mises à jour possibles avec HACS

---

## Informations disponibles

AirRadar peut créer les entités suivantes dans Home Assistant :

### Avion le plus proche

* Avion le plus proche
* Distance
* Altitude
* Vitesse
* Compagnie
* Trajet
* Immatriculation
* Type / modèle

### Surveillance

* Nombre d'avions détectés
* Avion dans la zone d'alerte
* Dernier passage
* Distance du dernier passage

### Réglages

* Distance d'alerte
* Altitude maximale d'alerte
* Notifications avions ON/OFF

### Événement

AirRadar crée également une entité :

```text
event.airradar_passage_avion
```

Elle est mise à jour à chaque nouveau passage correspondant aux critères configurés.

---

# Installation avec HACS

## 1. Ajouter le dépôt

Dans Home Assistant :

1. Ouvrez **HACS**
2. Allez dans **Intégrations**
3. Cliquez sur le menu **⋮**
4. Sélectionnez **Dépôts personnalisés**
5. Ajoutez l'URL de ce dépôt GitHub
6. Sélectionnez la catégorie **Intégration**
7. Cliquez sur **Ajouter**

---

## 2. Installer AirRadar

Dans HACS :

1. Recherchez **AirRadar**
2. Cliquez sur **Télécharger**
3. Redémarrez Home Assistant

---

## 3. Ajouter l'intégration

Après redémarrage :

**Paramètres → Appareils et services → Ajouter une intégration**

Recherchez :

```text
AirRadar
```

Puis suivez l'assistant de configuration.

---

# Configuration

Lors de l'installation, AirRadar vous demande plusieurs paramètres.

### Distance d'alerte

Distance maximale entre votre domicile et l'avion.

Exemple :

```text
2 km
```

L'avion doit passer à **2 km ou moins** pour pouvoir déclencher une alerte.

---

### Altitude maximale

Altitude maximale de l'avion pour recevoir une
