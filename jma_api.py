"""
気象庁 (jma.go.jp) 内部 JSON API クライアント
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Tuple


class JmaApiClient:
    """気象庁の裏側JSON APIに直接アクセスするクライアント"""

    BASE_URL = "https://www.jma.go.jp/bosai"
    AREA_JSON_URL = f"{BASE_URL}/common/const/area.json"
    FORECAST_URL = f"{BASE_URL}/forecast/data/forecast"
    WARNING_URL = f"{BASE_URL}/warning/data/warning"
    QUAKE_URL = f"{BASE_URL}/quake/data/list.json"
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 QtJmaMonitor/1.0"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.cached_areas: Optional[Dict[str, Any]] = None

    def _fetch_json(self, url: str) -> Tuple[Any, str]:
        """URLからJSONを取得し、(パース済みデータ, 生のJSON文字列) のタプルを返す"""
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.USER_AGENT,
                "Accept": "application/json, text/plain, */*",
                "Cache-Control": "no-cache",
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            raw_text = response.read().decode("utf-8")
            data = json.loads(raw_text)
            return data, raw_text

    def get_area_master(self) -> Dict[str, Any]:
        """全国のエリアマスター（地方、都道府県/管区）を取得"""
        if self.cached_areas is None:
            data, _ = self._fetch_json(self.AREA_JSON_URL)
            self.cached_areas = data
        return self.cached_areas

    def get_offices_list(self) -> List[Dict[str, str]]:
        """選択用の都道府県/地域リスト（コードと名称）を整頓して返す"""
        areas = self.get_area_master()
        offices = areas.get("offices", {})
        result = []
        for code, info in offices.items():
            result.append({
                "code": code,
                "name": info.get("name", ""),
                "enName": info.get("enName", ""),
                "officeName": info.get("officeName", ""),
                "parent": info.get("parent", "")
            })
        result.sort(key=lambda x: x["code"])
        return result

    def get_forecast(self, office_code: str) -> Tuple[Dict[str, Any], str]:
        """指定地域の天気予報データを取得"""
        url = f"{self.FORECAST_URL}/{office_code}.json"
        data, raw_text = self._fetch_json(url)
        parsed = self._parse_forecast_data(data)
        parsed["endpoint"] = url
        return parsed, raw_text

    def _parse_forecast_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not data or not isinstance(data, list):
            return {"publishingOffice": "", "reportDatetime": "", "areas": []}

        result = {
            "publishingOffice": data[0].get("publishingOffice", "") if len(data) > 0 else "",
            "reportDatetime": data[0].get("reportDatetime", "") if len(data) > 0 else "",
            "areas": []
        }

        time_series = data[0].get("timeSeries", []) if len(data) > 0 else []
        if not time_series:
            return result

        weather_series = time_series[0] if len(time_series) > 0 else {}
        pop_series = time_series[1] if len(time_series) > 1 else {}
        temp_series = time_series[2] if len(time_series) > 2 else {}

        time_defines_weather = weather_series.get("timeDefines", [])

        for area_w in weather_series.get("areas", []):
            area_code = area_w.get("area", {}).get("code", "")
            area_name = area_w.get("area", {}).get("name", "")
            weathers = area_w.get("weathers", [])
            weather_codes = area_w.get("weatherCodes", [])
            winds = area_w.get("winds", [])
            waves = area_w.get("waves", [])

            pops = []
            for area_p in pop_series.get("areas", []):
                if area_p.get("area", {}).get("code") == area_code:
                    pops = area_p.get("pops", [])
                    break

            temps = []
            for area_t in temp_series.get("areas", []):
                if area_t.get("area", {}).get("code") == area_code:
                    temps = area_t.get("temps", [])
                    break

            result["areas"].append({
                "code": area_code,
                "name": area_name,
                "timeDefines": time_defines_weather,
                "weathers": weathers,
                "weatherCodes": weather_codes,
                "winds": winds,
                "waves": waves,
                "pops": pops,
                "temps": temps
            })

        return result

    def get_warnings(self, office_code: str) -> Tuple[Dict[str, Any], str]:
        """気象警報・注意報を取得"""
        url = f"{self.WARNING_URL}/{office_code}.json"
        data, raw_text = self._fetch_json(url)
        parsed = self._parse_warning_data(data)
        parsed["endpoint"] = url
        return parsed, raw_text

    def _parse_warning_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data or not isinstance(data, dict):
            return {"activeAreas": [], "hasWarnings": False, "reportDatetime": ""}

        report_dt = data.get("reportDatetime", "")
        active_warnings = []
        
        class20s = data.get("class20s", {})
        class10s = data.get("class10s", {})

        target_dict = class20s if class20s else class10s

        for area_code, info in target_dict.items():
            warn_items = []
            for item in info.get("warnings", []):
                status = item.get("status", "")
                code = item.get("code", "")
                if status and status not in ["解除", "発表警報・注意報はなし"]:
                    is_special = (code.startswith("3") or (int(code) >= 30 if code.isdigit() else False))
                    is_warning = not is_special and (code.startswith("0") or (int(code) < 10 if code.isdigit() else False))
                    warn_items.append({
                        "code": code,
                        "status": status,
                        "kind": self._get_warning_kind_name(code),
                        "level": "special" if is_special else ("warning" if is_warning else "advisory")
                    })
            if warn_items:
                active_warnings.append({
                    "areaCode": area_code,
                    "warnings": warn_items
                })

        return {
            "reportDatetime": report_dt,
            "targetAreaCount": len(target_dict),
            "activeAreas": active_warnings,
            "hasWarnings": len(active_warnings) > 0
        }

    def _get_warning_kind_name(self, code: str) -> str:
        code_map = {
            "00": "解除",
            "02": "暴風雪警報",
            "03": "大雨警報",
            "04": "洪水警報",
            "05": "暴風警報",
            "06": "大雪警報",
            "07": "波浪警報",
            "08": "高潮警報",
            "10": "大雨注意報",
            "12": "大雪注意報",
            "13": "風雪注意報",
            "14": "雷注意報",
            "15": "強風注意報",
            "16": "波浪注意報",
            "17": "融雪注意報",
            "18": "洪水注意報",
            "19": "高潮注意報",
            "20": "濃霧注意報",
            "21": "乾燥注意報",
            "22": "なだれ注意報",
            "23": "低温注意報",
            "24": "霜注意報",
            "25": "着氷注意報",
            "26": "着雪注意報",
            "32": "暴風雪特別警報",
            "33": "大雨特別警報",
            "35": "暴風特別警報",
            "36": "大雪特別警報",
            "37": "波浪特別警報",
            "38": "高潮特別警報",
        }
        return code_map.get(str(code), f"警報・注意報({code})")

    def get_quake_list(self) -> Tuple[List[Dict[str, Any]], str]:
        """最新の地震情報一覧を取得"""
        url = self.QUAKE_URL
        data, raw_text = self._fetch_json(url)
        parsed = self._parse_quake_data(data)
        return parsed, raw_text

    def _parse_quake_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data or not isinstance(data, list):
            return []

        parsed_list = []
        for item in data[:30]:
            eid = item.get("eid", "")
            rdt = item.get("rdt", "")
            max_int = item.get("maxI", item.get("maxInt", ""))
            epicenter = item.get("anm", item.get("epicenter", "調査中/不明"))
            mag = item.get("mag", "")
            depth = item.get("dep", "")
            at = item.get("at", rdt)
            tsunami = item.get("ift", "")

            int_display = self._format_intensity(max_int)

            parsed_list.append({
                "id": eid if eid else f"{at}_{epicenter}",
                "reportTime": rdt,
                "originTime": at,
                "epicenter": epicenter,
                "maxIntensity": str(max_int) if max_int is not None else "",
                "intensityDisplay": int_display,
                "magnitude": f"M{mag}" if mag else "M不明",
                "depth": f"深さ約{depth}" if depth else "深さ不明",
                "tsunami": tsunami,
                "raw": item
            })

        return parsed_list

    def _format_intensity(self, raw_int: Any) -> str:
        mapping = {
            "1": "震度1",
            "2": "震度2",
            "3": "震度3",
            "4": "震度4",
            "5-": "震度5弱",
            "5+": "震度5強",
            "6-": "震度6弱",
            "6+": "震度6強",
            "7": "震度7",
        }
        val = str(raw_int) if raw_int is not None else ""
        return mapping.get(val, f"震度{val}" if val else "震度情報なし")
