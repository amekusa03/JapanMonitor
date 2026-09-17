# JMA Direct JSON Monitor (Japan Weather & Earthquake Monitor)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Qt](https://img.shields.io/badge/Qt-PySide6-green.svg)](https://wiki.qt.io/Qt_for_Python)
[![Language](https://img.shields.io/badge/Language-English%20%7C%20日本語-orange.svg)](#)
[![OS](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#)

[English](README.md) | [日本語 (Japanese)](README.jp.md)

---

A Qt (PySide6) desktop application that directly connects to the internal JSON API endpoints used behind the scenes by the Japan Meteorological Agency (`jma.go.jp`) website, providing real-time weather forecasts, warning/advisory monitoring, earthquake alerts, and system tray resident notifications.

## Key Features

1. **Direct JMA Internal JSON API Feed**:
   - **Nationwide Area Master**: `https://www.jma.go.jp/bosai/common/const/area.json`
   - **Weather Forecast (Daily/Weekly)**: `https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json`
   - **Weather Warnings / Advisories / Emergency Warnings**: `https://www.jma.go.jp/bosai/warning/data/warning/{area_code}.json`
   - **Real-Time Earthquake Bulletins**: `https://www.jma.go.jp/bosai/quake/data/list.json`
2. **System Tray Residency & Desktop Notifications**:
   - Minimizes to the system tray on closing the window to keep background polling active.
   - Sends OS desktop notifications upon new Emergency Warnings, Warnings (Heavy Rain, Gale, Flood, etc.), or Advisories.
   - Instantly notifies new earthquake events with seismic intensity, epicenter, magnitude, and tsunami advisory status.
   - Right-click tray menu (Open Dashboard, Refresh Weather Data, Quit).
   - Dynamic tray icon color reflecting current alert status.
3. **Bilingual Support (English / Japanese)**:
   - Switch between English and Japanese seamlessly with one click from the header or settings tab.
   - All weather terms, alert kinds (e.g. "Heavy Rain Warning" ↔ "大雨警報"), and seismic intensity levels are fully translated.
4. **Raw JSON Inspector**:
   - Inspect formatted raw JSON payloads directly from JMA endpoints in real time with a quick clipboard copy button.
5. **Modern Dark Theme UI**:
   - **Dashboard**: Weather forecast cards, precipitation chances, temperatures, active alert badges, and latest earthquake overview.
   - **Warnings & Advisories**: Breakdown of active alerts by municipality/zone.
   - **Earthquake History**: List of the 30 most recent earthquakes with interactive details.
   - **Settings**: Prefecture/region selection, polling interval, notification conditions, language switcher, and test alerts.


### Autostart on System Login (Tray Resident)

You can easily configure the app to launch quietly into the system tray when logging in.

#### Method 1: Via the Settings Tab (Recommended)
1. Open the application and navigate to the **"Settings" (設定)** tab.
2. Check the box **"Launch on system login (Start in tray)"**.
3. On your next login, the app will launch directly into the system tray without opening the main window.

#### Method 2: Manual XDG Autostart Configuration
Create `~/.config/autostart/japan-monitor.desktop`:
```bash
mkdir -p ~/.config/autostart
cat << 'DESKTOP_EOF' > ~/.config/autostart/japan-monitor.desktop
[Desktop Entry]
Type=Application
Name=JMA Monitor
Comment=Japan Meteorological Agency JSON Desktop Monitor
Exec=/path/to/JapanMonitor/run.sh --minimized
Icon=weather-clouds
Terminal=false
Categories=Utility;
X-GNOME-Autostart-enabled=true
DESKTOP_EOF
```

## How to Run

```bash
# Install dependencies (if needed)
pip3 install -r requirements.txt

# Run via launcher script
./run.sh

# Or launch directly with python3
python3 main.py
```

## Project Structure

- `main.py` : Application entry point
- `main_window.py` : Main GUI window, system tray integration, and UI controller
- `config.json` : Auto-saved configuration (region, language, polling interval, notification preferences)
- `i18n.py` : Internationalization (Japanese/English translation dictionary & helper)
- `jma_api.py` : JMA internal JSON API fetching and parsing client
- `monitor_service.py` : Background timer-based polling and differential detector
- `app_theme.py` : Modern dark theme stylesheet (QSS) & dynamic tray icon renderer
- `ui_components.py` : Reusable UI cards, alert badges, and raw JSON inspector
- `run.sh` : Shell startup script
- `README.md` : English documentation
- `README.jp.md` : 日本語ドキュメント (Japanese documentation)
