# AirRadar for Home Assistant

AirRadar is a Home Assistant custom integration that monitors aircraft around the Home Assistant home location using ADSB.lol, enriches flight information with ADSBDB, and can send mobile notifications when an aircraft enters configured distance and altitude thresholds.

## HACS installation

1. Add this GitHub repository to HACS as a **Custom repository**.
2. Select category **Integration**.
3. Install **AirRadar**.
4. Restart Home Assistant.
5. Go to **Settings > Devices & services > Add integration > AirRadar**.

## Configuration

AirRadar is configured entirely from the Home Assistant UI. No `configuration.yaml` entry is required.

Default values:
- Alert distance: 2 km
- Maximum altitude: 5000 m
- Polling interval: 15 seconds
- Direct notifications: enabled
- Notification action: optional, e.g. `notify.mobile_app_iphone`

## Features

- ADSB.lol aircraft polling
- ADSBDB airline and route enrichment
- Nearest aircraft sensors
- Adjustable alert distance and altitude
- Passage event entity
- Anti-duplicate passage logic with 1 km hysteresis
- Optional direct Home Assistant mobile notification
- No dependency on the CYD display
