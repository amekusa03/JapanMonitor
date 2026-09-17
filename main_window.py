# -*- coding: utf-8 -*-
"""
気象庁内部JSONデータ直結 監視＆トレイ常駐通知 メインウィンドウ (設定永続化・多言語対応)
"""

import os
import json
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QComboBox, QScrollArea, QFrame,
    QListWidget, QListWidgetItem, QSystemTrayIcon, QMenu,
    QMessageBox, QCheckBox, QSpinBox, QStatusBar, QGridLayout, QApplication
)
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QIcon, QFont, QAction, QCloseEvent

from jma_api import JmaApiClient
from monitor_service import MonitorService
from app_theme import APP_STYLESHEET, create_status_icon
from ui_components import BadgeLabel, WeatherCard, QuakeCard, JsonViewerWidget
from i18n import t, get_i18n
from autostart import is_autostart_enabled, set_autostart

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config() -> dict:
    """保存された設定ファイルを読み込み"""
    default_cfg = {
        "office_code": "130000",
        "language": "ja",
        "polling_interval": 300,
        "notify_special": True,
        "notify_warning": True,
        "notify_advisory": False,
        "notify_quake": True,
        "minimize_to_tray": True
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_cfg.update(data)
        except Exception:
            pass
    return default_cfg


def save_config(cfg: dict):
    """設定をファイルに保存"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.i18n = get_i18n()
        self.config = load_config()

        # 設定の反映
        self.i18n.current_lang = self.config.get("language", "ja")
        self.current_office_code = self.config.get("office_code", "130000")
        poll_interval = self.config.get("polling_interval", 300)

        self.resize(1020, 740)
        self.setStyleSheet(APP_STYLESHEET)

        # 終了フラグ
        self.really_quit = False

        # API クライアント & 監視サービス初期化
        self.api_client = JmaApiClient()
        self.monitor_service = MonitorService(office_code=self.current_office_code, poll_interval_sec=poll_interval)

        # キャッシュデータ
        self.last_forecast_data = {}
        self.last_forecast_raw = ""
        self.last_warning_data = {}
        self.last_warning_raw = ""
        self.last_quake_raw = ""
        self.last_quakes_list = []
        self.offices_cache = []

        # UI構築
        self._init_ui()
        self._init_tray_icon()
        self._load_area_master()

        # シグナル接続
        self.monitor_service.forecast_updated.connect(self._on_forecast_updated)
        self.monitor_service.warning_updated.connect(self._on_warning_updated)
        self.monitor_service.quake_detected.connect(self._on_quake_detected)
        self.monitor_service.error_occurred.connect(self._on_error)
        self.monitor_service.data_refreshed.connect(self._on_refreshed)

        # 初期言語適用
        self.retranslate_ui()

        # 監視スタート
        self.monitor_service.start()

    def _save_current_config(self):
        """現在のUI状態を設定辞書にまとめて保存"""
        self.config["office_code"] = self.current_office_code
        self.config["language"] = self.i18n.current_lang
        self.config["polling_interval"] = self.interval_combo.currentData() or 300
        self.config["notify_special"] = self.cb_notify_special.isChecked()
        self.config["notify_warning"] = self.cb_notify_warning.isChecked()
        self.config["notify_advisory"] = self.cb_notify_advisory.isChecked()
        self.config["notify_quake"] = self.cb_notify_quake.isChecked()
        self.config["minimize_to_tray"] = self.cb_minimize_to_tray.isChecked()
        save_config(self.config)

    def _init_ui(self):
        """メインレイアウト構築"""
        central = QWidget(self)
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. ヘッダー
        header = QFrame()
        header.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)

        title_box = QVBoxLayout()
        self.app_title = QLabel()
        self.app_title.setObjectName("AppTitle")
        self.app_subtitle = QLabel()
        self.app_subtitle.setObjectName("AppSubtitle")
        title_box.addWidget(self.app_title)
        title_box.addWidget(self.app_subtitle)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # 言語切替
        self.lang_label = QLabel("🌐")
        self.lang_label.setStyleSheet("font-size: 14px;")
        header_layout.addWidget(self.lang_label)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("日本語", "ja")
        self.lang_combo.addItem("English", "en")
        
        # 設定された言語を選択
        if self.i18n.current_lang == "en":
            self.lang_combo.setCurrentIndex(1)
        else:
            self.lang_combo.setCurrentIndex(0)

        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        header_layout.addWidget(self.lang_combo)

        # 地域選択
        self.loc_label = QLabel()
        self.loc_label.setStyleSheet("color: #cbd5e1; font-weight: bold; margin-left: 8px;")
        header_layout.addWidget(self.loc_label)

        self.area_combo = QComboBox()
        self.area_combo.setMinimumWidth(180)
        self.area_combo.currentIndexChanged.connect(self._on_area_changed)
        header_layout.addWidget(self.area_combo)

        # 即時更新ボタン
        self.refresh_btn = QPushButton()
        self.refresh_btn.clicked.connect(self._on_manual_refresh)
        header_layout.addWidget(self.refresh_btn)

        main_layout.addWidget(header)

        # 2. タブウィジェット
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # タブページ作成
        self._create_dashboard_tab()
        self._create_warnings_tab()
        self._create_quakes_tab()
        self._create_json_inspector_tab()
        self._create_settings_tab()

        # 3. ステータスバー
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _create_dashboard_tab(self):
        """タブ1: ダッシュボード"""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(16, 16, 16, 16)
        tab_layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(16)

        # 警報サマリーバー
        self.alert_summary_frame = QFrame()
        self.alert_summary_frame.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 10px;
                padding: 12px;
            }
        """)
        summary_layout = QHBoxLayout(self.alert_summary_frame)
        self.alert_summary_label = QLabel()
        self.alert_summary_label.setFont(QFont("sans-serif", 12, QFont.Bold))
        self.alert_badges_layout = QHBoxLayout()
        summary_layout.addWidget(self.alert_summary_label)
        summary_layout.addStretch()
        summary_layout.addLayout(self.alert_badges_layout)
        scroll_layout.addWidget(self.alert_summary_frame)

        # 天気予報カードエリア
        self.weather_sec_label = QLabel()
        self.weather_sec_label.setFont(QFont("sans-serif", 14, QFont.Bold))
        self.weather_sec_label.setStyleSheet("color: #38bdf8;")
        scroll_layout.addWidget(self.weather_sec_label)

        self.weather_cards_layout = QHBoxLayout()
        self.weather_cards_layout.setSpacing(12)
        scroll_layout.addLayout(self.weather_cards_layout)

        # 最新地震速報カード
        self.quake_sec_label = QLabel()
        self.quake_sec_label.setFont(QFont("sans-serif", 14, QFont.Bold))
        self.quake_sec_label.setStyleSheet("color: #c084fc;")
        scroll_layout.addWidget(self.quake_sec_label)

        self.latest_quake_card = QuakeCard()
        scroll_layout.addWidget(self.latest_quake_card)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        tab_layout.addWidget(scroll)

        self.tabs.addTab(tab, "")

    def _create_warnings_tab(self):
        """タブ2: 警報・注意報詳細"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.warning_info_header = QLabel()
        self.warning_info_header.setFont(QFont("sans-serif", 14, QFont.Bold))
        self.warning_info_header.setStyleSheet("color: #f1f5f9;")
        layout.addWidget(self.warning_info_header)

        self.warning_list = QListWidget()
        layout.addWidget(self.warning_list)

        self.tabs.addTab(tab, "")

    def _create_quakes_tab(self):
        """タブ3: 地震履歴"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.quake_history_header = QLabel()
        self.quake_history_header.setFont(QFont("sans-serif", 14, QFont.Bold))
        self.quake_history_header.setStyleSheet("color: #c084fc;")
        layout.addWidget(self.quake_history_header)

        self.quake_list = QListWidget()
        self.quake_list.itemClicked.connect(self._on_quake_list_item_clicked)
        layout.addWidget(self.quake_list)

        # 選択された地震の詳細
        self.selected_quake_card = QuakeCard()
        layout.addWidget(self.selected_quake_card)

        self.tabs.addTab(tab, "")

    def _create_json_inspector_tab(self):
        """タブ4: 気象庁生JSONインスペクター"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.json_desc_label = QLabel()
        self.json_desc_label.setFont(QFont("sans-serif", 12, QFont.Bold))
        self.json_desc_label.setStyleSheet("color: #38bdf8;")
        layout.addWidget(self.json_desc_label)

        selector_layout = QHBoxLayout()
        self.target_api_label = QLabel()
        self.json_type_combo = QComboBox()
        self.json_type_combo.addItems(["", "", "", ""])
        self.json_type_combo.currentIndexChanged.connect(self._on_json_type_changed)
        selector_layout.addWidget(self.target_api_label)
        selector_layout.addWidget(self.json_type_combo, stretch=1)
        layout.addLayout(selector_layout)

        self.json_viewer = JsonViewerWidget()
        layout.addWidget(self.json_viewer)

        self.tabs.addTab(tab, "")

    def _create_settings_tab(self):
        """タブ5: 設定 & 常駐設定"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        self.settings_title = QLabel()
        self.settings_title.setFont(QFont("sans-serif", 14, QFont.Bold))
        self.settings_title.setStyleSheet("color: #38bdf8;")
        layout.addWidget(self.settings_title)

        card = QFrame()
        card.setProperty("class", "Card")
        card.setStyleSheet("QFrame { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 16px; }")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)

        # 言語設定行
        lang_setting_layout = QHBoxLayout()
        self.lang_setting_label = QLabel()
        self.settings_lang_combo = QComboBox()
        self.settings_lang_combo.addItem("日本語 (Japanese)", "ja")
        self.settings_lang_combo.addItem("English (英語)", "en")
        if self.i18n.current_lang == "en":
            self.settings_lang_combo.setCurrentIndex(1)
        else:
            self.settings_lang_combo.setCurrentIndex(0)
        self.settings_lang_combo.currentIndexChanged.connect(self._on_settings_lang_changed)
        lang_setting_layout.addWidget(self.lang_setting_label)
        lang_setting_layout.addWidget(self.settings_lang_combo)
        lang_setting_layout.addStretch()
        card_layout.addLayout(lang_setting_layout)

        # 定期監視間隔
        interval_layout = QHBoxLayout()
        self.polling_interval_label = QLabel()
        self.interval_combo = QComboBox()
        self.interval_combo.addItem("", 60)
        self.interval_combo.addItem("", 180)
        self.interval_combo.addItem("", 300)
        self.interval_combo.addItem("", 600)
        self.interval_combo.addItem("", 900)
        
        # 復元
        curr_int = self.config.get("polling_interval", 300)
        idx = self.interval_combo.findData(curr_int)
        if idx >= 0:
            self.interval_combo.setCurrentIndex(idx)
        else:
            self.interval_combo.setCurrentIndex(2)

        self.interval_combo.currentIndexChanged.connect(self._on_interval_changed)
        interval_layout.addWidget(self.polling_interval_label)
        interval_layout.addWidget(self.interval_combo)
        interval_layout.addStretch()
        card_layout.addLayout(interval_layout)

        # 通知条件
        self.cb_notify_special = QCheckBox()
        self.cb_notify_special.setChecked(self.config.get("notify_special", True))
        self.cb_notify_special.toggled.connect(self._save_current_config)
        card_layout.addWidget(self.cb_notify_special)

        self.cb_notify_warning = QCheckBox()
        self.cb_notify_warning.setChecked(self.config.get("notify_warning", True))
        self.cb_notify_warning.toggled.connect(self._save_current_config)
        card_layout.addWidget(self.cb_notify_warning)

        self.cb_notify_advisory = QCheckBox()
        self.cb_notify_advisory.setChecked(self.config.get("notify_advisory", False))
        self.cb_notify_advisory.toggled.connect(self._save_current_config)
        card_layout.addWidget(self.cb_notify_advisory)

        self.cb_notify_quake = QCheckBox()
        self.cb_notify_quake.setChecked(self.config.get("notify_quake", True))
        self.cb_notify_quake.toggled.connect(self._save_current_config)
        card_layout.addWidget(self.cb_notify_quake)

        # 常駐設定
        self.cb_minimize_to_tray = QCheckBox()
        self.cb_minimize_to_tray.setChecked(self.config.get("minimize_to_tray", True))
        self.cb_minimize_to_tray.toggled.connect(self._save_current_config)
        card_layout.addWidget(self.cb_minimize_to_tray)

        # ログイン時自動起動
        self.cb_autostart = QCheckBox()
        self.cb_autostart.setChecked(is_autostart_enabled())
        self.cb_autostart.toggled.connect(self._on_autostart_toggled)
        card_layout.addWidget(self.cb_autostart)

        layout.addWidget(card)

        # テスト通知ボタン群
        self.test_sec_label = QLabel()
        self.test_sec_label.setFont(QFont("sans-serif", 12, QFont.Bold))
        self.test_sec_label.setStyleSheet("color: #cbd5e1;")
        layout.addWidget(self.test_sec_label)

        test_btn_layout = QHBoxLayout()
        self.test_warn_btn = QPushButton()
        self.test_warn_btn.clicked.connect(self._test_warning_notification)
        self.test_quake_btn = QPushButton()
        self.test_quake_btn.setObjectName("SecondaryBtn")
        self.test_quake_btn.clicked.connect(self._test_quake_notification)

        test_btn_layout.addWidget(self.test_warn_btn)
        test_btn_layout.addWidget(self.test_quake_btn)
        test_btn_layout.addStretch()
        layout.addLayout(test_btn_layout)

        layout.addStretch()
        self.tabs.addTab(tab, "")

    def _init_tray_icon(self):
        """トレイアイコンの初期化と常駐設定"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(create_status_icon())

        self.tray_menu = QMenu(self)
        self.tray_menu.setStyleSheet("""
            QMenu {
                background-color: #1e293b;
                color: #f1f5f9;
                border: 1px solid #334155;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #0284c7;
            }
        """)

        self.tray_show_action = QAction(self)
        self.tray_show_action.triggered.connect(self._show_and_raise)
        self.tray_menu.addAction(self.tray_show_action)

        self.tray_refresh_action = QAction(self)
        self.tray_refresh_action.triggered.connect(self._on_manual_refresh)
        self.tray_menu.addAction(self.tray_refresh_action)

        self.tray_menu.addSeparator()

        self.tray_quit_action = QAction(self)
        self.tray_quit_action.triggered.connect(self._quit_application)
        self.tray_menu.addAction(self.tray_quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self._on_tray_icon_activated)
        self.tray_icon.show()

    def retranslate_ui(self):
        """全UI文字列の動的再翻訳"""
        self.setWindowTitle(t("app_title") + " - JMA Monitor")
        self.app_title.setText(t("app_title"))
        self.app_subtitle.setText(t("app_subtitle"))
        self.loc_label.setText(t("region"))
        self.refresh_btn.setText(t("refresh_now"))

        # タブタイトル
        self.tabs.setTabText(0, t("tab_dashboard"))
        self.tabs.setTabText(1, t("tab_warnings"))
        self.tabs.setTabText(2, t("tab_quakes"))
        self.tabs.setTabText(3, t("tab_json"))
        self.tabs.setTabText(4, t("tab_settings"))

        # ダッシュボード
        self.weather_sec_label.setText(t("weather_forecast_sec"))
        self.quake_sec_label.setText(t("latest_quake_sec"))

        # 警報タブ
        self.warning_info_header.setText(t("warning_list_header"))

        # 地震タブ
        self.quake_history_header.setText(t("quakes_list_header"))

        # 生JSONタブ
        self.json_desc_label.setText(t("json_desc"))
        self.target_api_label.setText(t("target_api"))
        self.json_type_combo.setItemText(0, t("api_forecast"))
        self.json_type_combo.setItemText(1, t("api_warning"))
        self.json_type_combo.setItemText(2, t("api_quake"))
        self.json_type_combo.setItemText(3, t("api_area"))
        self.json_viewer.retranslate_ui()

        # 設定タブ
        self.settings_title.setText(t("settings_title"))
        self.lang_setting_label.setText(t("language_setting"))
        self.polling_interval_label.setText(t("polling_interval"))
        self.interval_combo.setItemText(0, t("interval_1m"))
        self.interval_combo.setItemText(1, t("interval_3m"))
        self.interval_combo.setItemText(2, t("interval_5m"))
        self.interval_combo.setItemText(3, t("interval_10m"))
        self.interval_combo.setItemText(4, t("interval_15m"))

        self.cb_notify_special.setText(t("notify_special"))
        self.cb_notify_warning.setText(t("notify_warning"))
        self.cb_notify_advisory.setText(t("notify_advisory"))
        self.cb_notify_quake.setText(t("notify_quake"))
        self.cb_minimize_to_tray.setText(t("minimize_tray"))
        self.cb_autostart.setText(t("autostart_login"))

        self.test_sec_label.setText(t("test_section"))
        self.test_warn_btn.setText(t("test_warn_btn"))
        self.test_quake_btn.setText(t("test_quake_btn"))

        # トレイ
        self.tray_icon.setToolTip(t("tray_tooltip"))
        self.tray_show_action.setText(t("tray_open"))
        self.tray_refresh_action.setText(t("tray_refresh"))
        self.tray_quit_action.setText(t("tray_quit"))

        # 地域コンボボックスの再ラベル付け
        self._refresh_area_combo_labels()

        # ダッシュボードやカードの再描画
        self.latest_quake_card.update_display()
        self.selected_quake_card.update_display()

        for i in range(self.weather_cards_layout.count()):
            w = self.weather_cards_layout.itemAt(i).widget()
            if isinstance(w, WeatherCard):
                w.update_display()

        # 警報と地震リストの再描画
        if self.last_warning_data:
            self._render_warnings(self.last_warning_data)
        if self.last_quakes_list:
            self._render_quake_list(self.last_quakes_list)

    def _refresh_area_combo_labels(self):
        """地域コンボボックスの表示名を現在言語に合わせて更新"""
        if not self.offices_cache:
            return
        curr_code = self.current_office_code
        self.area_combo.blockSignals(True)
        self.area_combo.clear()
        is_en = (self.i18n.current_lang == "en")
        for item in self.offices_cache:
            if is_en and item.get("enName"):
                name = f"{item['enName']} ({item['name']})"
            else:
                name = f"{item['name']} ({item['officeName']})"
            self.area_combo.addItem(name, item["code"])

        idx = self.area_combo.findData(curr_code)
        if idx >= 0:
            self.area_combo.setCurrentIndex(idx)
        self.area_combo.blockSignals(False)

    def _on_autostart_toggled(self, checked: bool):
        set_autostart(checked)
        self.config["autostart"] = checked
        self._save_current_config()

    def _on_language_changed(self, index: int):
        lang = self.lang_combo.itemData(index)
        if lang and lang != self.i18n.current_lang:
            self.i18n.current_lang = lang
            self.settings_lang_combo.blockSignals(True)
            self.settings_lang_combo.setCurrentIndex(index)
            self.settings_lang_combo.blockSignals(False)
            self._save_current_config()
            self.retranslate_ui()

    def _on_settings_lang_changed(self, index: int):
        lang = self.settings_lang_combo.itemData(index)
        if lang and lang != self.i18n.current_lang:
            self.i18n.current_lang = lang
            self.lang_combo.blockSignals(True)
            self.lang_combo.setCurrentIndex(index)
            self.lang_combo.blockSignals(False)
            self._save_current_config()
            self.retranslate_ui()

    def _on_tray_icon_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            if self.isVisible():
                if self.isMinimized():
                    self.showNormal()
                    self.activateWindow()
                else:
                    self.hide()
            else:
                self._show_and_raise()

    def _show_and_raise(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _quit_application(self):
        self._save_current_config()
        self.really_quit = True
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent):
        self._save_current_config()
        if self.really_quit or not self.cb_minimize_to_tray.isChecked():
            self.tray_icon.hide()
            event.accept()
        else:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                t("tray_resident_title"),
                t("tray_resident_msg"),
                QSystemTrayIcon.Information,
                3000
            )

    def _load_area_master(self):
        try:
            self.offices_cache = self.api_client.get_offices_list()
            self._refresh_area_combo_labels()
        except Exception as e:
            self._on_error(f"{t('error_prefix')} {e}")

    def _on_area_changed(self):
        selected_code = self.area_combo.currentData()
        if selected_code and selected_code != self.current_office_code:
            self.current_office_code = selected_code
            self._save_current_config()
            self.status_bar.showMessage(t("region_changed", name=self.area_combo.currentText()))
            self.monitor_service.set_office_code(self.current_office_code)

    def _on_manual_refresh(self):
        self.status_bar.showMessage(t("connecting"))
        self.monitor_service.refresh_all()

    def _on_interval_changed(self):
        sec = self.interval_combo.currentData()
        if sec:
            self.monitor_service.set_interval(sec)
            self._save_current_config()
            self.status_bar.showMessage(t("interval_changed", interval=self.interval_combo.currentText()))

    # --- データ受信スロット ---
    @Slot(dict, str)
    def _on_forecast_updated(self, data: dict, raw_json: str):
        self.last_forecast_data = data
        self.last_forecast_raw = raw_json

        while self.weather_cards_layout.count():
            item = self.weather_cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        areas = data.get("areas", [])
        for area in areas[:3]:
            card = WeatherCard(title=area.get("name", "地域"))
            weathers = area.get("weathers", [])
            winds = area.get("winds", [])
            pops = area.get("pops", [])
            temps = area.get("temps", [])

            w_str = weathers[0] if weathers else ""
            wind_str = winds[0] if winds else ""
            pop_str = f"{pops[0]}%" if pops else ""
            temp_str = f"{temps[0]} ℃" if temps else ""

            card.set_weather_info(w_str, wind_str, pop_str, temp_str)
            self.weather_cards_layout.addWidget(card)

        if self.json_type_combo.currentIndex() == 0:
            self.json_viewer.set_json_content(data.get("endpoint", ""), raw_json)

    @Slot(dict, str, list)
    def _on_warning_updated(self, data: dict, raw_json: str, new_alerts: list):
        self.last_warning_data = data
        self.last_warning_raw = raw_json
        self._render_warnings(data)

        if new_alerts:
            for alert in new_alerts:
                level = alert.get("level")
                kind = alert.get("kind", "")
                kind_trans = self.i18n.translate_warning(kind)
                status_trans = self.i18n.translate_status(alert.get("status", ""))
                if (level == "special" and self.cb_notify_special.isChecked()) or \
                   (level == "warning" and self.cb_notify_warning.isChecked()) or \
                   (level == "advisory" and self.cb_notify_advisory.isChecked()):
                    self._send_notification(
                        t("notify_warn_title", kind=kind_trans),
                        t("notify_warn_body", region=self.area_combo.currentText(), kind=kind_trans, status=status_trans),
                        QSystemTrayIcon.Warning if level != "special" else QSystemTrayIcon.Critical
                    )

        if self.json_type_combo.currentIndex() == 1:
            self.json_viewer.set_json_content(data.get("endpoint", ""), raw_json)

    def _render_warnings(self, data: dict):
        while self.alert_badges_layout.count():
            item = self.alert_badges_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        has_warnings = data.get("hasWarnings", False)
        active_areas = data.get("activeAreas", [])

        has_special = False
        has_warn = False

        self.warning_list.clear()

        if not has_warnings:
            self.alert_summary_label.setText(t("alert_summary_none"))
            ok_badge = BadgeLabel(t("badge_none"), level="ok")
            self.alert_badges_layout.addWidget(ok_badge)
            self.warning_list.addItem(t("warning_list_none"))
        else:
            self.alert_summary_label.setText(t("alert_summary_active", count=len(active_areas)))
            
            unique_kinds = {}
            for area in active_areas:
                for w in area.get("warnings", []):
                    raw_kind = w.get("kind")
                    level = w.get("level")
                    trans_kind = self.i18n.translate_warning(raw_kind)
                    trans_status = self.i18n.translate_status(w.get("status", ""))
                    unique_kinds[trans_kind] = level
                    if level == "special":
                        has_special = True
                    elif level == "warning":
                        has_warn = True

                    self.warning_list.addItem(f"[{trans_status}] {trans_kind} ({t('target_code')}: {area.get('areaCode')})")

            for kind, level in unique_kinds.items():
                badge = BadgeLabel(kind, level=level)
                self.alert_badges_layout.addWidget(badge)

        self.tray_icon.setIcon(create_status_icon(has_warning=has_warn, has_special=has_special))

    @Slot(dict, str, bool)
    def _on_quake_detected(self, latest_quake: dict, raw_json: str, is_new: bool):
        self.last_quake_raw = raw_json
        self.latest_quake_card.set_quake_info(latest_quake)

        try:
            quakes_list = self.api_client._parse_quake_data(json.loads(raw_json))
            self.last_quakes_list = quakes_list
            self._render_quake_list(quakes_list)
        except Exception:
            pass

        if is_new and self.cb_notify_quake.isChecked():
            int_str = self.i18n.translate_intensity(latest_quake.get("intensityDisplay", ""))
            epicenter = latest_quake.get("epicenter", "")
            mag = latest_quake.get("magnitude", "")
            orig_t = latest_quake.get("originTime", "")
            self._send_notification(
                t("notify_quake_title", intensity=int_str),
                t("notify_quake_body", epicenter=epicenter, magnitude=mag, time=orig_t),
                QSystemTrayIcon.Information
            )

        if self.json_type_combo.currentIndex() == 2:
            self.json_viewer.set_json_content(self.api_client.QUAKE_URL, raw_json)

    def _render_quake_list(self, quakes_list: list):
        self.quake_list.clear()
        for q in quakes_list:
            int_trans = self.i18n.translate_intensity(q.get("intensityDisplay", ""))
            item_text = f"[{int_trans}] {q.get('originTime')} | {t('epicenter', name=q.get('epicenter'))} ({q.get('magnitude')}, {q.get('depth')})"
            item = QListWidgetItem(item_text)
            self.quake_list.addItem(item)

    def _on_quake_list_item_clicked(self, item):
        row = self.quake_list.row(item)
        if 0 <= row < len(self.last_quakes_list):
            self.selected_quake_card.set_quake_info(self.last_quakes_list[row])

    def _on_json_type_changed(self, index: int):
        if index == 0:
            self.json_viewer.set_json_content(f"{self.api_client.FORECAST_URL}/{self.current_office_code}.json", self.last_forecast_raw)
        elif index == 1:
            self.json_viewer.set_json_content(f"{self.api_client.WARNING_URL}/{self.current_office_code}.json", self.last_warning_raw)
        elif index == 2:
            self.json_viewer.set_json_content(self.api_client.QUAKE_URL, self.last_quake_raw)
        elif index == 3:
            areas = self.api_client.get_area_master()
            self.json_viewer.set_json_content(self.api_client.AREA_JSON_URL, json.dumps(areas, ensure_ascii=False, indent=2))

    @Slot()
    def _on_refreshed(self):
        from datetime import datetime
        now_str = datetime.now().strftime("%H:%M:%S")
        self.status_bar.showMessage(f"{t('data_updated')} ({now_str})")

    @Slot(str)
    def _on_error(self, err: str):
        self.status_bar.showMessage(f"{t('error_prefix')} {err}")

    def _send_notification(self, title: str, message: str, icon_type=QSystemTrayIcon.Information):
        self.tray_icon.showMessage(title, message, icon_type, 6000)

    def _test_warning_notification(self):
        self._send_notification(
            t("test_warn_title"),
            t("test_warn_body", region=self.area_combo.currentText()),
            QSystemTrayIcon.Warning
        )

    def _test_quake_notification(self):
        self._send_notification(
            t("test_quake_title"),
            t("test_quake_body"),
            QSystemTrayIcon.Information
        )
