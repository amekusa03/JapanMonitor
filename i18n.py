# -*- coding: utf-8 -*-
"""
多言語 (日本語 / 英語) 国際化 (i18n) モジュール
"""

from typing import Dict, Any

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "ja": {
        # アプリ全体
        "app_title": "気象庁 直接JSON監視モニター",
        "app_subtitle": "jma.go.jp 内部API直結 / システムトレイ常駐通知",
        "region": "地域:",
        "refresh_now": "今すぐ更新",
        "connecting": "気象庁サーバーに接続中...",
        "data_updated": "気象庁JSONデータ更新完了",
        "error_prefix": "エラー:",
        "region_changed": "地域を変更しました: {name}",
        "interval_changed": "監視間隔を {interval} に設定しました",

        # タブ
        "tab_dashboard": "ダッシュボード",
        "tab_warnings": "警報・注意報詳細",
        "tab_quakes": "地震情報",
        "tab_json": "生JSONデータ",
        "tab_settings": "設定",

        # ダッシュボード
        "alert_summary_loading": "現在の気象警報・注意報: 取得中...",
        "alert_summary_none": "現在の気象警報・注意報: 発表なし (平常)",
        "alert_summary_active": "気象警報・注意報が発表されています ({count} エリア)",
        "badge_none": "発表なし",
        "weather_forecast_sec": "天気予報",
        "latest_quake_sec": "最新の地震情報",
        "pop_label": "降水確率: {pop}%",
        "pop_label_none": "降水確率: --%",
        "wind_prefix": "風: ",

        # 警報・注意報タブ
        "warning_list_header": "発表中の気象警報・注意報一覧",
        "warning_list_none": "現在、発表されている警報・注意報はありません。",
        "target_code": "対象コード",

        # 地震タブ
        "quakes_list_header": "最近発生した地震 (直近30件)",
        "origin_time": "発生時刻: {time}",
        "origin_datetime": "発生日時: {time}",
        "epicenter": "震源地: {name}",
        "magnitude": "規模: {mag}",
        "depth": "深さ: {depth}",
        "tsunami_none": "津波の心配なし",
        "intensity_unknown": "震度情報なし",

        # 生JSONタブ
        "json_desc": "気象庁公式サイト (jma.go.jp) から直接受信した生JSONデータ",
        "target_api": "対象API:",
        "copy_json": "JSONをコピー",
        "copy_done": "コピー完了!",
        "json_placeholder": "JSONデータがここに表示されます...",
        "api_forecast": "天気予報 JSON (/forecast/data/forecast/)",
        "api_warning": "警報・注意報 JSON (/warning/data/warning/)",
        "api_quake": "地震速報リスト JSON (/quake/data/list.json)",
        "api_area": "エリア定義マスター JSON (/common/const/area.json)",

        # 設定タブ
        "settings_title": "監視・通知・言語・常駐設定",
        "language_setting": "表示言語 (Language):",
        "polling_interval": "監視ポーリング間隔:",
        "interval_1m": "1分間隔",
        "interval_3m": "3分間隔",
        "interval_5m": "5分間隔 (推奨)",
        "interval_10m": "10分間隔",
        "interval_15m": "15分間隔",
        "notify_special": "特別警報発表時にデスクトップ通知",
        "notify_warning": "気象警報発表時にデスクトップ通知",
        "notify_advisory": "注意報発表時にデスクトップ通知",
        "notify_quake": "新規地震検知時にデスクトップ通知 (震度1以上)",
        "minimize_tray": "ウィンドウを閉じた時にトレイ常駐 (終了しない)",
        "autostart_login": "PCログイン時に自動起動してトレイ常駐 (Autostart)",
        "test_section": "通知動作テスト",
        "test_warn_btn": "テスト: 警報通知",
        "test_quake_btn": "テスト: 地震通知",

        # トレイメニュー & 常駐
        "tray_tooltip": "気象庁 JSON 監視モニター (常駐中)",
        "tray_open": "メイン画面を開く",
        "tray_refresh": "今すぐ気象データを更新",
        "tray_quit": "終了",
        "tray_resident_title": "気象庁モニター 常駐中",
        "tray_resident_msg": "バックグラウンドで気象警報と地震速報を監視しています。",

        # 通知テキスト
        "notify_warn_title": "気象警報通知: {kind}",
        "notify_warn_body": "{region} にて {kind} が【{status}】されました。",
        "notify_quake_title": "地震情報 ({intensity})",
        "notify_quake_body": "【震源地】{epicenter} ({magnitude})\n発生時刻: {time}",
        "test_warn_title": "【テスト】大雨警報 発表",
        "test_warn_body": "{region} に大雨警報が発表されました。(テスト通知)",
        "test_quake_title": "【テスト】地震情報 (震度4)",
        "test_quake_body": "【震源地】東京湾 (M4.8)\n発生時刻: 2026-09-18 07:45 (テスト通知)",
    },
    "en": {
        # App overall
        "app_title": "JMA Direct JSON Monitor",
        "app_subtitle": "Direct jma.go.jp Internal API / Tray Resident Notification System",
        "region": "Region:",
        "refresh_now": "Refresh Now",
        "connecting": "Connecting to JMA server...",
        "data_updated": "JMA JSON Data Updated",
        "error_prefix": "Error:",
        "region_changed": "Region changed to: {name}",
        "interval_changed": "Polling interval set to {interval}",

        # Tabs
        "tab_dashboard": "Dashboard",
        "tab_warnings": "Warnings & Advisories",
        "tab_quakes": "Earthquake Info",
        "tab_json": "Raw JSON Inspector",
        "tab_settings": "Settings",

        # Dashboard
        "alert_summary_loading": "Current Weather Alerts: Fetching...",
        "alert_summary_none": "Current Weather Alerts: None active (Clear)",
        "alert_summary_active": "Weather Alerts in effect ({count} areas)",
        "badge_none": "None",
        "weather_forecast_sec": "Weather Forecast",
        "latest_quake_sec": "Latest Earthquake",
        "pop_label": "Chance of Rain: {pop}%",
        "pop_label_none": "Chance of Rain: --%",
        "wind_prefix": "Wind: ",

        # Warnings Tab
        "warning_list_header": "Active Weather Warnings & Advisories",
        "warning_list_none": "No active weather warnings or advisories at this time.",
        "target_code": "Area Code",

        # Quakes Tab
        "quakes_list_header": "Recent Earthquakes (Last 30)",
        "origin_time": "Origin Time: {time}",
        "origin_datetime": "Origin Time: {time}",
        "epicenter": "Epicenter: {name}",
        "magnitude": "Magnitude: {mag}",
        "depth": "Depth: {depth}",
        "tsunami_none": "No tsunami threat",
        "intensity_unknown": "No Intensity Data",

        # JSON Tab
        "json_desc": "Raw JSON feed directly received from JMA (jma.go.jp)",
        "target_api": "Target API:",
        "copy_json": "Copy JSON",
        "copy_done": "Copied!",
        "json_placeholder": "JSON payload will be displayed here...",
        "api_forecast": "Forecast JSON (/forecast/data/forecast/)",
        "api_warning": "Warnings JSON (/warning/data/warning/)",
        "api_quake": "Earthquake List JSON (/quake/data/list.json)",
        "api_area": "Area Master JSON (/common/const/area.json)",

        # Settings Tab
        "settings_title": "Monitoring, Notification & Language Settings",
        "language_setting": "Display Language (表示言語):",
        "polling_interval": "Polling Interval:",
        "interval_1m": "1 minute",
        "interval_3m": "3 minutes",
        "interval_5m": "5 minutes (Recommended)",
        "interval_10m": "10 minutes",
        "interval_15m": "15 minutes",
        "notify_special": "Notify on Emergency Special Warnings",
        "notify_warning": "Notify on Weather Warnings",
        "notify_advisory": "Notify on Weather Advisories",
        "notify_quake": "Notify on new Earthquakes (Intensity 1+)",
        "minimize_tray": "Minimize to System Tray on close (Keep running)",
        "autostart_login": "Launch on system login (Start in tray)",
        "test_section": "Notification Test",
        "test_warn_btn": "Test: Warning Alert",
        "test_quake_btn": "Test: Earthquake Alert",

        # Tray Menu & Resident
        "tray_tooltip": "JMA JSON Monitor (Running in Tray)",
        "tray_open": "Open Dashboard",
        "tray_refresh": "Refresh Weather Data Now",
        "tray_quit": "Exit",
        "tray_resident_title": "JMA Monitor Running in Background",
        "tray_resident_msg": "Monitoring weather alerts and earthquakes in system tray.",

        # Notifications
        "notify_warn_title": "Weather Alert: {kind}",
        "notify_warn_body": "{kind} has been [{status}] for {region}.",
        "notify_quake_title": "Earthquake Alert ({intensity})",
        "notify_quake_body": "[Epicenter] {epicenter} ({magnitude})\nOrigin Time: {time}",
        "test_warn_title": "[Test] Heavy Rain Warning Issued",
        "test_warn_body": "Heavy Rain Warning issued for {region}. (Test Notification)",
        "test_quake_title": "[Test] Earthquake Alert (Intensity 4)",
        "test_quake_body": "[Epicenter] Tokyo Bay (M4.8)\nOrigin Time: 2026-09-18 07:45 (Test Notification)",
    }
}

# 警報名・震度の英語変換テーブル
WARNING_TRANSLATIONS_EN = {
    "解除": "Cleared / Cancelled",
    "発表": "Issued",
    "継続": "Continuing",
    "警報から注意報": "Downgraded to Advisory",
    "暴風雪警報": "Blizzard Warning",
    "大雨警報": "Heavy Rain Warning",
    "洪水警報": "Flood Warning",
    "暴風警報": "Gale / Storm Warning",
    "大雪警報": "Heavy Snow Warning",
    "波浪警報": "High Waves Warning",
    "高潮警報": "Storm Surge Warning",
    "大雨注意報": "Heavy Rain Advisory",
    "大雪注意報": "Heavy Snow Advisory",
    "風雪注意報": "Snowstorm Advisory",
    "雷注意報": "Thunderstorm Advisory",
    "強風注意報": "Gale Advisory",
    "波浪注意報": "High Waves Advisory",
    "融雪注意報": "Snowmelt Advisory",
    "洪水注意報": "Flood Advisory",
    "高潮注意報": "Storm Surge Advisory",
    "濃霧注意報": "Dense Fog Advisory",
    "乾燥注意報": "Dry Air Advisory",
    "なだれ注意報": "Avalanche Advisory",
    "低温注意報": "Low Temperature Advisory",
    "霜注意報": "Frost Advisory",
    "着氷注意報": "Icing Advisory",
    "着雪注意報": "Snow Accretion Advisory",
    "暴風雪特別警報": "Emergency Blizzard Warning",
    "大雨特別警報": "Emergency Heavy Rain Warning",
    "暴風特別警報": "Emergency Gale Warning",
    "大雪特別警報": "Emergency Heavy Snow Warning",
    "波浪特別警報": "Emergency High Waves Warning",
    "高潮特別警報": "Emergency Storm Surge Warning",
}

INTENSITY_TRANSLATIONS_EN = {
    "1": "Intensity 1",
    "2": "Intensity 2",
    "3": "Intensity 3",
    "4": "Intensity 4",
    "5-": "Intensity 5-Lower",
    "5+": "Intensity 5-Upper",
    "6-": "Intensity 6-Lower",
    "6+": "Intensity 6-Upper",
    "7": "Intensity 7",
    "震度1": "Intensity 1",
    "震度2": "Intensity 2",
    "震度3": "Intensity 3",
    "震度4": "Intensity 4",
    "震度5弱": "Intensity 5-Lower",
    "震度5強": "Intensity 5-Upper",
    "震度6弱": "Intensity 6-Lower",
    "震度6強": "Intensity 6-Upper",
    "震度7": "Intensity 7",
}


class I18nManager:
    """言語切り替え管理シングルトンクラス"""
    _instance = None
    _current_lang = "ja"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(I18nManager, cls).__new__(cls)
        return cls._instance

    @property
    def current_lang(self) -> str:
        return self._current_lang

    @current_lang.setter
    def current_lang(self, lang: str):
        if lang in TRANSLATIONS:
            self._current_lang = lang

    def t(self, key: str, **kwargs) -> str:
        """指定キーの翻訳文字列を取得"""
        lang_dict = TRANSLATIONS.get(self._current_lang, TRANSLATIONS["ja"])
        template = lang_dict.get(key, key)
        if kwargs:
            try:
                return template.format(**kwargs)
            except Exception:
                return template
        return template

    def translate_warning(self, kind: str) -> str:
        """警報・注意報名の翻訳"""
        if self._current_lang == "en":
            return WARNING_TRANSLATIONS_EN.get(kind, kind)
        return kind

    def translate_status(self, status: str) -> str:
        """発表ステータスの翻訳"""
        if self._current_lang == "en":
            return WARNING_TRANSLATIONS_EN.get(status, status)
        return status

    def translate_intensity(self, intensity_str: str) -> str:
        """震度表記の翻訳"""
        if self._current_lang == "en":
            return INTENSITY_TRANSLATIONS_EN.get(intensity_str, intensity_str)
        return intensity_str


# 便利ヘルパー
_i18n = I18nManager()

def t(key: str, **kwargs) -> str:
    return _i18n.t(key, **kwargs)

def get_i18n() -> I18nManager:
    return _i18n
