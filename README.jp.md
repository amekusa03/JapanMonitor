# 気象庁 直接JSON監視モニター (JMA Qt Desktop Monitor)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Qt](https://img.shields.io/badge/Qt-PySide6-green.svg)](https://wiki.qt.io/Qt_for_Python)
[![Language](https://img.shields.io/badge/Language-日本語%20%7C%20English-orange.svg)](#)
[![OS](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#)

[日本語](README.jp.md) | [English (英語)](README.md)

---

気象庁公式サイト（`jma.go.jp`）が画面表示のために裏側で使用している非公開/公開内部JSONデータに直接アクセスし、リアルタイムで天気予報・気象警報・注意報・地震速報を監視・システムトレイ常駐通知するQt（PySide6）デスクトップアプリケーションです。

## 主な機能

1. **気象庁公式サイトの裏側JSON API直結**:
   - **全国エリア定義マスター**: `https://www.jma.go.jp/bosai/common/const/area.json`
   - **天気予報 (3日間/7日間)**: `https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json`
   - **気象警報・注意報・特別警報**: `https://www.jma.go.jp/bosai/warning/data/warning/{area_code}.json`
   - **リアルタイム地震速報一覧**: `https://www.jma.go.jp/bosai/quake/data/list.json`
2. **システムトレイ常駐 & デスクトップ通知**:
   - ウィンドウの「×」ボタンで閉じてもトレイアイコンに常駐し、バックグラウンドで監視を継続。
   - 気象警報（大雨警報、洪水警報、暴風警報など）や特別警報の新規発表時にOSデスクトップ通知を自動発信。
   - 最新地震発生時に震度・震源地・マグニチュード・津波有無を即時通知。
   - トレイアイコンの右クリックメニュー（画面表示、即時更新、終了）。
   - 警報発令状況に応じてトレイアイコンの色が動的に変化。
3. **日本語 / 英語のリアルタイム切り替え (i18n)**:
   - ヘッダーまたは設定画面から「日本語 / English」を1クリックで即時切り替え可能。
   - UIだけでなく、警報種別（大雨警報 ↔ Heavy Rain Warningなど）や震度表記も自動翻訳。
4. **生JSONインスペクター機能**:
   - 気象庁から受信した生のJSONデータをリアルタイムにフォーマット表示・クリップボードコピー可能。
5. **リッチなダークテーマUI**:
   - **ダッシュボード**: 今日の天気予報カード、降水確率、気温、発令中警報バッジ、最新地震カード
   - **警報・注意報詳細**: 自治体・エリア別の詳細発表一覧
   - **地震情報**: 最近の地震リスト（直近30件）と詳細ビュー
   - **設定**: 地域選択、監視ポーリング間隔、通知トリガー条件、言語設定、通知テスト


### ログイン時の自動起動（常駐）設定

アプリ内の設定画面、または手動設定のいずれかで簡単に自動常駐を設定できます。

#### 方法1: アプリの設定画面から設定（推奨）
1. アプリを起動し、**「設定」タブ**を開きます。
2. **「PCログイン時に自動起動してトレイ常駐 (Autostart)」** にチェックを入れます。
3. 次回OSログイン時より、画面を出さずに最初からシステムトレイへ静かに常駐します。

#### 方法2: ターミナルから手動で設定
自動起動用設定ファイル `~/.config/autostart/japan-monitor.desktop` を作成します：
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

## 起動方法

```bash
# 依存パッケージのインストール (必要に応じて)
pip3 install -r requirements.txt

# 起動スクリプトで実行
./run.sh

# または直接 python3 で起動
python3 main.py
```

## ファイル構成

- `main.py` : アプリケーションのエントリーポイント
- `main_window.py` : メインウィンドウ・トレイアイコン管理・UIロジック
- `config.json` : 地域・言語・監視間隔・通知設定の自動保存ファイル (自動生成)
- `i18n.py` : 日本語・英語の多言語翻訳管理モジュール
- `jma_api.py` : 気象庁内部JSON APIクライアント＆パーサー
- `monitor_service.py` : バックグラウンド定期監視・差分検知サービス
- `app_theme.py` : ダークテーマQSS・動的トレイアイコン描画
- `ui_components.py` : 天気カード・警報バッジ・地震カード・JSONビューア
- `run.sh` : 起動シェルスクリプト
- `README.md` : 英語ドキュメント (English documentation)
- `README.jp.md` : 日本語ドキュメント
