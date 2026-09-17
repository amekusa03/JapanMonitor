# -*- coding: utf-8 -*-
"""
クロスプラットフォーム (Windows / macOS / Linux) 自動起動管理モジュール
"""

import os
import sys
import platform

CURRENT_OS = platform.system()


def _get_app_info():
    """アプリケーションパスおよびPython実行パスを取得"""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    py_exe = sys.executable
    main_script = os.path.join(app_dir, "main.py")
    return app_dir, py_exe, main_script


def is_autostart_enabled() -> bool:
    """自動起動が現在のアプリパスで有効になっているか確認"""
    app_dir, py_exe, main_script = _get_app_info()

    if CURRENT_OS == "Linux":
        path = os.path.expanduser("~/.config/autostart/japan-monitor.desktop")
        if not os.path.exists(path):
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            # 現在のmain_scriptパスまたはapp_dirが含まれているか検証
            return (main_script in content or app_dir in content)
        except Exception:
            return False

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
            return bool(val) and (main_script in str(val) or app_dir in str(val))
        except Exception:
            return False

    elif CURRENT_OS == "Darwin":  # macOS
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.jma.monitor.plist")
        if not os.path.exists(plist_path):
            return False
        try:
            with open(plist_path, "r", encoding="utf-8") as f:
                content = f.read()
            return main_script in content
        except Exception:
            return False

    return False


def set_autostart(enabled: bool) -> bool:
    """自動起動の有効化/無効化"""
    try:
        app_dir, py_exe, main_script = _get_app_info()

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
Path={app_dir}
Icon=weather-clouds
Terminal=false
Categories=Utility;
StartupNotify=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=2
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


def sync_autostart_with_config(config_autostart: bool):
    """configの設定値と実態（.desktopやレジストリ等）の同期・修復を行う"""
    if config_autostart:
        # 有効設定かつパス不一致や未設定なら更新
        if not is_autostart_enabled():
            set_autostart(True)
    else:
        if is_autostart_enabled():
            set_autostart(False)
