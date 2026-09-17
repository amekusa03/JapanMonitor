# -*- coding: utf-8 -*-
"""
クロスプラットフォーム (Windows / macOS / Linux) 自動起動管理モジュール
"""

import os
import sys
import platform

CURRENT_OS = platform.system()


def is_autostart_enabled() -> bool:
    """自動起動が有効になっているか確認"""
    if CURRENT_OS == "Linux":
        path = os.path.expanduser("~/.config/autostart/japan-monitor.desktop")
        return os.path.exists(path)

    elif CURRENT_OS == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            val, _ = winreg.QueryValueEx(key, "JmaMonitor")
            winreg.CloseKey(key)
            return bool(val)
        except Exception:
            return False

    elif CURRENT_OS == "Darwin":  # macOS
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.jma.monitor.plist")
        return os.path.exists(plist_path)

    return False


def set_autostart(enabled: bool) -> bool:
    """自動起動の有効化/無効化"""
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        py_exe = sys.executable
        main_script = os.path.join(app_dir, "main.py")

        if CURRENT_OS == "Linux":
            autostart_dir = os.path.expanduser("~/.config/autostart")
            path = os.path.join(autostart_dir, "japan-monitor.desktop")
            if enabled:
                os.makedirs(autostart_dir, exist_ok=True)
                desktop_content = f"""[Desktop Entry]
Type=Application
Name=JMA Monitor
Comment=Japan Meteorological Agency JSON Desktop Monitor
Exec={py_exe} "{main_script}" --minimized
Icon=weather-clouds
Terminal=false
Categories=Utility;
X-GNOME-Autostart-enabled=true
"""
                with open(path, "w", encoding="utf-8") as f:
                    f.write(desktop_content)
            else:
                if os.path.exists(path):
                    os.remove(path)
            return True

        elif CURRENT_OS == "Windows":
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_SET_VALUE
                )
                if enabled:
                    # pythonw.exe または python.exe でバックグラウンド起動
                    cmd = f'"{py_exe}" "{main_script}" --minimized'
                    winreg.SetValueEx(key, "JmaMonitor", 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(key, "JmaMonitor")
                    except FileNotFoundError:
                        pass
                winreg.CloseKey(key)
                return True
            except Exception as e:
                print(f"Windows Registry autostart error: {e}", file=sys.stderr)
                return False

        elif CURRENT_OS == "Darwin":  # macOS
            plist_dir = os.path.expanduser("~/Library/LaunchAgents")
            plist_path = os.path.join(plist_dir, "com.jma.monitor.plist")
            if enabled:
                os.makedirs(plist_dir, exist_ok=True)
                plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jma.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>{py_exe}</string>
        <string>{main_script}</string>
        <string>--minimized</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
                with open(plist_path, "w", encoding="utf-8") as f:
                    f.write(plist_content)
            else:
                if os.path.exists(plist_path):
                    os.remove(plist_path)
            return True

    except Exception as e:
        print(f"Failed to set autostart: {e}", file=sys.stderr)
        return False
    return False
