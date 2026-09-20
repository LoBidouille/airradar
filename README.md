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

Altitude maximale de l'avion pour recevoir une alerte.

Exemple :

```text
5000 m
```

Un avion à 10 000 m ne déclenchera donc pas l'alerte si votre limite est réglée à 5 000 m.

---

### Fréquence d'interrogation

Fréquence à laquelle AirRadar interroge les données ADS-B.

Valeur recommandée :

```text
15 secondes
```

---

### Notifications

Les notifications peuvent être activées ou désactivées.

Pour envoyer directement une notification à un téléphone utilisant l'application Home Assistant, indiquez l'action de notification correspondante.

Exemple :

```text
notify.mobile_app_iphone
```

Vous pouvez retrouver le nom exact dans :

**Outils de développement → Actions**

Puis recherchez :

```text
notify.mobile_app
```

Le champ peut également être laissé vide.

AirRadar fonctionnera alors normalement et l'entité événement pourra être utilisée dans vos propres automatisations.

---

# Fonctionnement de la détection

Exemple avec :

```text
Distance d'alerte : 2 km
Altitude maximale : 5000 m
```

Un avion approche :

```text
3,2 km  → aucune alerte
2,4 km  → aucune alerte
1,9 km  → ✈️ ALERTE
1,4 km  → aucune nouvelle alerte
0,8 km  → aucune nouvelle alerte
1,5 km  → aucune nouvelle alerte
2,5 km  → aucune nouvelle alerte
3,1 km  → réarmement
```

AirRadar génère donc **une seule alerte par passage**.

Le réarmement est effectué lorsque l'avion sort au-delà de :

```text
distance d'alerte + 1 km
```

Cela évite de recevoir une notification toutes les quelques secondes pour le même avion.

---

# Exemple de notification

```text
✈️ Avion proche de la maison

AFR1234 — Air France
MRS → CDG · 1,42 km · 3850 m · 742 km/h
```

Les informations disponibles dépendent des données ADS-B et ADSBDB disponibles pour chaque vol.

---

# Sources des données

## ADSB.lol

Utilisé pour récupérer les informations ADS-B telles que :

* position
* altitude
* vitesse
* cap
* callsign
* immatriculation
* type d'avion

## ADSBDB

Utilisé pour compléter les informations lorsque celles-ci sont disponibles :

* compagnie aérienne
* origine du vol
* destination du vol

---

# Confidentialité

AirRadar utilise la position **Maison** configurée dans Home Assistant pour rechercher les avions situés à proximité.

Les coordonnées sont utilisées lors des requêtes nécessaires au fonctionnement de la détection ADS-B.

Aucun compte AirRadar spécifique n'est nécessaire.

---

# Limitations

La disponibilité et la précision des informations dépendent des données fournies par les services externes.

Certains avions peuvent ne pas fournir :

* de callsign
* d'immatriculation
* de modèle
* de compagnie
* d'origine ou de destination

La couverture ADS-B peut également varier selon la région.

AirRadar ne doit pas être utilisé pour des applications aéronautiques critiques ou liées à la sécurité.

---

# Mise à jour

Si AirRadar a été installé via HACS, les futures versions pourront être mises à jour directement depuis HACS.

---

# Désinstallation

Dans Home Assistant :

**Paramètres → Appareils et services → AirRadar → Supprimer**

Puis supprimez AirRadar depuis HACS si vous souhaitez également supprimer les fichiers de l'intégration.

---

# 🇬🇧 English

## Overview

**AirRadar** is a custom Home Assistant integration that monitors aircraft flying near your home and can send notifications based on their **distance** and **altitude**.

AirRadar uses:

* **ADSB.lol** for live ADS-B aircraft information.
* **ADSBDB** for airline and flight-route enrichment.

No local ADS-B receiver, additional Raspberry Pi, or RTL-SDR dongle is required.

---

## Features

* ✈️ Nearby aircraft detection
* 📍 Automatically uses the Home Assistant `Home` location
* 📏 Configurable alert distance
* 🛫 Configurable maximum alert altitude
* 🔔 Smartphone notifications
* 🚫 Notification duplicate protection
* 🔄 Automatic rearming after the aircraft leaves the area
* 🛰️ ADS-B data from ADSB.lol
* 🏢 Airline information
* 🗺️ Flight origin and destination when available
* 🔢 Aircraft registration
* ✈️ Aircraft type / model
* 📊 Number of detected aircraft
* 📡 Nearest aircraft
* 🕒 Last aircraft passage
* ⚡ Aircraft passage Event entity
* ⚙️ Full configuration from the Home Assistant UI
* 🏠 No local ADS-B hardware required
* 📦 HACS installation and updates

---

# Available entities

AirRadar can expose the following entities.

### Nearest aircraft

* Nearest aircraft
* Distance
* Altitude
* Speed
* Airline
* Route
* Registration
* Aircraft type / model

### Monitoring

* Detected aircraft count
* Aircraft inside alert zone
* Last passage
* Last passage distance

### Settings

* Alert distance
* Maximum alert altitude
* Aircraft notifications ON/OFF

### Event entity

AirRadar also creates an Event entity:

```text
event.airradar_passage_avion
```

It is updated whenever a new aircraft passage matches the configured criteria.

---

# Installation with HACS

## 1. Add the repository

In Home Assistant:

1. Open **HACS**
2. Go to **Integrations**
3. Open the **⋮** menu
4. Select **Custom repositories**
5. Enter this GitHub repository URL
6. Select **Integration**
7. Click **Add**

---

## 2. Install AirRadar

From HACS:

1. Search for **AirRadar**
2. Click **Download**
3. Restart Home Assistant

---

## 3. Add the integration

After restarting Home Assistant:

**Settings → Devices & services → Add integration**

Search for:

```text
AirRadar
```

Follow the configuration wizard.

---

# Configuration

AirRadar provides several configuration options.

### Alert distance

Maximum distance between your Home Assistant home location and the aircraft.

Example:

```text
2 km
```

The aircraft must be within **2 km or less** to trigger an alert.

---

### Maximum altitude

Maximum aircraft altitude allowed to trigger an alert.

Example:

```text
5000 m
```

An aircraft flying at 10,000 m will therefore not trigger an alert if your limit is set to 5,000 m.

---

### Polling interval

How often AirRadar retrieves ADS-B information.

Recommended value:

```text
15 seconds
```

---

### Notifications

Direct notifications can be enabled or disabled.

To send a notification directly to a phone using the Home Assistant Companion App, enter the corresponding notify action.

Example:

```text
notify.mobile_app_iphone
```

You can find the exact action under:

**Developer Tools → Actions**

Then search for:

```text
notify.mobile_app
```

This field can also be left empty.

AirRadar will continue working normally and the Event entity can be used in your own Home Assistant automations.

---

# Detection logic

Example configuration:

```text
Alert distance: 2 km
Maximum altitude: 5000 m
```

An aircraft approaches:

```text
3.2 km  → no alert
2.4 km  → no alert
1.9 km  → ✈️ ALERT
1.4 km  → no additional alert
0.8 km  → no additional alert
1.5 km  → no additional alert
2.5 km  → no additional alert
3.1 km  → rearmed
```

AirRadar therefore generates **only one alert per aircraft passage**.

The aircraft becomes eligible again once it moves farther away than:

```text
alert distance + 1 km
```

This prevents repeated notifications every few seconds for the same aircraft.

---

# Notification example

```text
✈️ Aircraft near home

AFR1234 — Air France
MRS → CDG · 1.42 km · 3850 m · 742 km/h
```

Available information depends on the ADS-B and ADSBDB data available for each flight.

---

# Data sources

## ADSB.lol

Used to retrieve ADS-B information such as:

* position
* altitude
* speed
* heading
* callsign
* registration
* aircraft type

## ADSBDB

Used to enrich flight information when available:

* airline
* flight origin
* flight destination

---

# Privacy

AirRadar uses the **Home** location configured in Home Assistant to search for nearby aircraft.

The coordinates are used when making the requests required for ADS-B detection.

No dedicated AirRadar account is required.

---

# Limitations

Aircraft and flight information depends on the availability and accuracy of external data providers.

Some aircraft may not provide:

* callsign
* registration
* aircraft model
* airline
* origin
* destination

ADS-B coverage may also vary depending on location.

AirRadar must not be used for safety-critical or operational aviation purposes.

---

# Updates

When installed through HACS, future AirRadar versions can be updated directly from HACS.

---

# Uninstallation

In Home Assistant:

**Settings → Devices & services → AirRadar → Delete**

Then remove AirRadar from HACS if you also want to remove the integration files.

---

# Credits

AirRadar relies on data provided by:

* ADSB.lol
* ADSBDB
* Home Assistant

AirRadar is an independent community project and is not affiliated with Home Assistant, ADSB.lol, ADSBDB, any airline, airport, or aviation authority.

---

# License

This project can be distributed under the **MIT License**.

Copyright © 2026
