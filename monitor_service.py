"""
気象庁内部API 定期監視・差分検知サービス
"""

import time
from typing import Dict, Any, List, Set
from PySide6.QtCore import QObject, Signal, QTimer
from jma_api import JmaApiClient


class MonitorService(QObject):
    """気象庁APIを定期ポーリングして更新・警報・地震を検知するサービス"""

    # シグナル定義
    forecast_updated = Signal(dict, str)       # parsed_data, raw_json
    warning_updated = Signal(dict, str, list)   # parsed_data, raw_json, new_alerts_list
    quake_detected = Signal(dict, str, bool)    # latest_quake, raw_json, is_new
    data_refreshed = Signal()                   # 全データ更新完了
    error_occurred = Signal(str)                # エラーメッセージ

    def __init__(self, office_code: str = "130000", poll_interval_sec: int = 300, parent=None):
        super().__init__(parent)
        self.client = JmaApiClient()
        self.office_code = office_code
        self.poll_interval_sec = poll_interval_sec

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_all)

        # 差分追跡用キャッシュ
        self.last_known_warning_codes: Set[str] = set()
        self.last_known_quake_ids: Set[str] = set()
        self.is_first_check = True

        # 設定
        self.min_notify_intensity = 1  # 通知する最小震度 (1〜7)

    def set_office_code(self, code: str):
        """監視対象地域コードを変更"""
        if self.office_code != code:
            self.office_code = code
            self.last_known_warning_codes.clear()
            self.refresh_all()

    def set_interval(self, seconds: int):
        """監視間隔（秒）を変更"""
        self.poll_interval_sec = seconds
        if self.timer.isActive():
            self.timer.setInterval(self.poll_interval_sec * 1000)

    def start(self):
        """監視開始"""
        self.refresh_all()
        self.timer.start(self.poll_interval_sec * 1000)

    def stop(self):
        """監視停止"""
        self.timer.stop()

    def refresh_all(self):
        """全データを手動またはタイマーで即時取得"""
        try:
            # 1. 天気予報
            self._fetch_forecast()
            
            # 2. 警報・注意報
            self._fetch_warnings()
            
            # 3. 地震情報
            self._fetch_quakes()

            self.is_first_check = False
            self.data_refreshed.emit()
        except Exception as e:
            self.error_occurred.emit(f"データ取得エラー: {str(e)}")

    def _fetch_forecast(self):
        try:
            forecast_data, raw_forecast = self.client.get_forecast(self.office_code)
            self.forecast_updated.emit(forecast_data, raw_forecast)
        except Exception as e:
            self.error_occurred.emit(f"予報取得失敗 ({self.office_code}): {e}")

    def _fetch_warnings(self):
        try:
            warning_data, raw_warning = self.client.get_warnings(self.office_code)
            
            # 現在発令中の警報コードを抽出
            current_active_codes = set()
            new_alerts = []
            for area in warning_data.get("activeAreas", []):
                for w in area.get("warnings", []):
                    key = f"{area.get('areaCode')}_{w.get('code')}"
                    current_active_codes.add(key)
                    if not self.is_first_check and key not in self.last_known_warning_codes:
                        new_alerts.append({
                            "area": area.get("areaCode"),
                            "kind": w.get("kind"),
                            "level": w.get("level"),
                            "status": w.get("status")
                        })

            self.last_known_warning_codes = current_active_codes
            self.warning_updated.emit(warning_data, raw_warning, new_alerts)
        except Exception as e:
            self.error_occurred.emit(f"警報取得失敗 ({self.office_code}): {e}")

    def _fetch_quakes(self):
        try:
            quake_list, raw_quakes = self.client.get_quake_list()
            if not quake_list:
                return

            latest = quake_list[0]
            latest_id = latest.get("id")

            is_new = False
            if not self.is_first_check and latest_id and latest_id not in self.last_known_quake_ids:
                is_new = True

            # IDをセットに追加
            for q in quake_list:
                if q.get("id"):
                    self.last_known_quake_ids.add(q.get("id"))

            self.quake_detected.emit(latest, raw_quakes, is_new)
        except Exception as e:
            self.error_occurred.emit(f"地震情報取得失敗: {e}")
