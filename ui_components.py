# -*- coding: utf-8 -*-
"""
カスタムUIコンポーネント (カード、バッジ、JSONビューア) - 多言語対応版
"""

import json
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QScrollArea, QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QClipboard
from i18n import t, get_i18n


class BadgeLabel(QLabel):
    """警報レベルに応じたカラーバッジ"""
    def __init__(self, text: str, level: str = "advisory", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("sans-serif", 10, QFont.Bold))
        self.set_badge(text, level)

    def set_badge(self, text: str, level: str = "advisory"):
        self.setText(text)
        if level == "special":
            bg, fg, border = "#7f1d1d", "#fecaca", "#ef4444"
        elif level == "warning":
            bg, fg, border = "#7c2d12", "#ffedd5", "#f97316"
        elif level == "advisory":
            bg, fg, border = "#713f12", "#fef08a", "#eab308"
        elif level == "ok":
            bg, fg, border = "#064e3b", "#a7f3d0", "#10b981"
        else:
            bg, fg, border = "#0c4a6e", "#bae6fd", "#0284c7"

        self.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
            border: 1px solid {border};
            border-radius: 6px;
            padding: 4px 10px;
        """)


class WeatherCard(QFrame):
    """天気予報カード"""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("WeatherCard")
        self.setProperty("class", "Card")
        self.setStyleSheet("""
            QFrame#WeatherCard {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 12px;
            }
        """)

        self.raw_weather = ""
        self.raw_wind = ""
        self.raw_pop = ""
        self.raw_temp = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # タイトル & エリア名
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("sans-serif", 14, QFont.Bold))
        self.title_label.setStyleSheet("color: #38bdf8;")
        layout.addWidget(self.title_label)

        # 天気概況
        self.weather_text = QLabel("--")
        self.weather_text.setFont(QFont("sans-serif", 12))
        self.weather_text.setWordWrap(True)
        self.weather_text.setStyleSheet("color: #f8fafc;")
        layout.addWidget(self.weather_text)

        # 風・波
        self.wind_text = QLabel("")
        self.wind_text.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(self.wind_text)

        # 気温 & 降水確率のステータスグリッド
        info_layout = QHBoxLayout()
        info_layout.setSpacing(12)

        self.temp_label = QLabel("-- ℃")
        self.temp_label.setFont(QFont("sans-serif", 16, QFont.Bold))
        self.temp_label.setStyleSheet("color: #fb923c;")

        self.pop_label = QLabel(t("pop_label_none"))
        self.pop_label.setFont(QFont("sans-serif", 12))
        self.pop_label.setStyleSheet("color: #60a5fa;")

        info_layout.addWidget(self.temp_label)
        info_layout.addStretch()
        info_layout.addWidget(self.pop_label)
        layout.addLayout(info_layout)

    def set_weather_info(self, weather_str: str, wind_str: str, pop_str: str, temp_str: str):
        self.raw_weather = weather_str
        self.raw_wind = wind_str
        self.raw_pop = pop_str
        self.raw_temp = temp_str
        self.update_display()

    def update_display(self):
        self.weather_text.setText(self.raw_weather if self.raw_weather else "--")
        self.wind_text.setText(f"{t('wind_prefix')}{self.raw_wind}" if self.raw_wind else "")
        if self.raw_pop:
            pop_clean = self.raw_pop.replace("%", "")
            self.pop_label.setText(t("pop_label", pop=pop_clean))
        else:
            self.pop_label.setText(t("pop_label_none"))
        self.temp_label.setText(self.raw_temp if self.raw_temp else "-- ℃")


class QuakeCard(QFrame):
    """地震速報カード"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("QuakeCard")
        self.setStyleSheet("""
            QFrame#QuakeCard {
                background-color: #1e293b;
                border: 1px solid #475569;
                border-radius: 12px;
            }
        """)

        self.cached_quake = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # ヘッダー (震度バッジ & 発生時刻)
        header_layout = QHBoxLayout()
        self.intensity_badge = BadgeLabel(t("intensity_unknown"), level="info")
        self.time_label = QLabel(t("origin_datetime", time="--"))
        self.time_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        header_layout.addWidget(self.intensity_badge)
        header_layout.addStretch()
        header_layout.addWidget(self.time_label)
        layout.addLayout(header_layout)

        # 震源地
        self.epicenter_label = QLabel(t("epicenter", name="--"))
        self.epicenter_label.setFont(QFont("sans-serif", 15, QFont.Bold))
        self.epicenter_label.setStyleSheet("color: #f1f5f9;")
        layout.addWidget(self.epicenter_label)

        # 詳細 (規模・深さ・津波)
        detail_layout = QHBoxLayout()
        self.mag_label = QLabel(t("magnitude", mag="--"))
        self.mag_label.setStyleSheet("color: #cbd5e1; font-size: 12px;")
        self.depth_label = QLabel(t("depth", depth="--"))
        self.depth_label.setStyleSheet("color: #cbd5e1; font-size: 12px;")
        self.tsunami_label = QLabel(t("tsunami_none"))
        self.tsunami_label.setStyleSheet("color: #4ade80; font-size: 12px; font-weight: bold;")

        detail_layout.addWidget(self.mag_label)
        detail_layout.addWidget(self.depth_label)
        detail_layout.addStretch()
        detail_layout.addWidget(self.tsunami_label)
        layout.addLayout(detail_layout)

    def set_quake_info(self, quake: dict):
        self.cached_quake = quake
        self.update_display()

    def update_display(self):
        if not self.cached_quake:
            return

        i18n = get_i18n()
        quake = self.cached_quake
        raw_int_disp = quake.get("intensityDisplay", "--")
        int_disp = i18n.translate_intensity(raw_int_disp)
        max_int = str(quake.get("maxIntensity", ""))

        if "5" in max_int or "6" in max_int or "7" in max_int:
            level = "special"
        elif "3" in max_int or "4" in max_int:
            level = "warning"
        elif "1" in max_int or "2" in max_int:
            level = "advisory"
        else:
            level = "info"

        self.intensity_badge.set_badge(int_disp, level=level)

        orig_time = quake.get("originTime", "--")
        self.time_label.setText(t("origin_datetime", time=orig_time))
        self.epicenter_label.setText(t("epicenter", name=quake.get("epicenter", "--")))
        self.mag_label.setText(t("magnitude", mag=quake.get("magnitude", "--")))
        self.depth_label.setText(t("depth", depth=quake.get("depth", "--")))
        
        tsunami = quake.get("tsunami", "")
        if "津波" in tsunami:
            self.tsunami_label.setText(tsunami)
            self.tsunami_label.setStyleSheet("color: #ef4444; font-size: 12px; font-weight: bold;")
        else:
            self.tsunami_label.setText(t("tsunami_none") if not tsunami else tsunami)
            self.tsunami_label.setStyleSheet("color: #4ade80; font-size: 12px; font-weight: bold;")


class JsonViewerWidget(QWidget):
    """気象庁から取得した裏側生JSONをインスペクト・コピーするウィジェット"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # コントロールバー (URL表示、コピーボタン)
        top_layout = QHBoxLayout()
        self.url_label = QLabel("Endpoint: --")
        self.url_label.setStyleSheet("color: #38bdf8; font-family: monospace; font-size: 11px;")
        
        self.copy_btn = QPushButton(t("copy_json"))
        self.copy_btn.setObjectName("SecondaryBtn")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)

        top_layout.addWidget(self.url_label, stretch=1)
        top_layout.addWidget(self.copy_btn)
        layout.addLayout(top_layout)

        # JSONテキストビューア
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlaceholderText(t("json_placeholder"))
        layout.addWidget(self.text_edit)

        self.current_raw_json = ""

    def set_json_content(self, url: str, raw_json_str: str):
        self.url_label.setText(f"API: {url}")
        self.current_raw_json = raw_json_str
        try:
            obj = json.loads(raw_json_str)
            formatted = json.dumps(obj, ensure_ascii=False, indent=2)
            self.text_edit.setPlainText(formatted)
        except Exception:
            self.text_edit.setPlainText(raw_json_str)

    def retranslate_ui(self):
        self.copy_btn.setText(t("copy_json"))
        self.text_edit.setPlaceholderText(t("json_placeholder"))

    def _copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())
        self.copy_btn.setText(t("copy_done"))
        QTimer.singleShot(2000, lambda: self.copy_btn.setText(t("copy_json")))
