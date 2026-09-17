"""
アプリケーションテーマ・スタイルシート・アイコン生成モジュール
"""

from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap, QPen, QBrush
from PySide6.QtCore import Qt, QRectF

APP_STYLESHEET = """
/* メインウィンドウ背景 */
QMainWindow, QWidget#CentralWidget {
    background-color: #0f172a;
    color: #f1f5f9;
    font-family: 'Segoe UI', 'Hiragino Sans', 'Meiryo', 'Noto Sans JP', sans-serif;
    font-size: 13px;
}

/* ヘッダーエリア */
QFrame#HeaderFrame {
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
    padding: 12px 16px;
}

QLabel#AppTitle {
    color: #38bdf8;
    font-size: 18px;
    font-weight: bold;
}

QLabel#AppSubtitle {
    color: #94a3b8;
    font-size: 11px;
}

/* タブバー */
QTabWidget::pane {
    border: none;
    background-color: #0f172a;
}

QTabBar::tab {
    background-color: #1e293b;
    color: #94a3b8;
    padding: 10px 22px;
    font-weight: 600;
    font-size: 13px;
    border: 1px solid #334155;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background-color: #38bdf8;
    color: #0f172a;
    border-color: #38bdf8;
}

QTabBar::tab:hover:!selected {
    background-color: #334155;
    color: #f8fafc;
}

/* カードコンポーネント */
QFrame.Card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px;
}

QFrame.Card:hover {
    border-color: #475569;
}

/* ボタン */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: bold;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton#SecondaryBtn {
    background-color: #334155;
    color: #f1f5f9;
}

QPushButton#SecondaryBtn:hover {
    background-color: #475569;
}

QPushButton#WarnBtn {
    background-color: #e11d48;
}

QPushButton#WarnBtn:hover {
    background-color: #be123c;
}

/* コンボボックス */
QComboBox {
    background-color: #1e293b;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 6px 12px;
    color: #f8fafc;
    font-size: 13px;
}

QComboBox:hover {
    border-color: #38bdf8;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #475569;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    color: #f8fafc;
    selection-background-color: #38bdf8;
    selection-color: #0f172a;
    border: 1px solid #475569;
}

/* スクロールエリア */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background-color: #0f172a;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* リスト・テキストエリア */
QListWidget {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #f8fafc;
    padding: 4px;
}

QListWidget::item {
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 2px;
}

QListWidget::item:hover {
    background-color: #334155;
}

QListWidget::item:selected {
    background-color: #0284c7;
    color: #ffffff;
}

QTextEdit, QPlainTextEdit {
    background-color: #090d16;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #38bdf8;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 8px;
}

/* ステータスバー */
QStatusBar {
    background-color: #1e293b;
    color: #94a3b8;
    border-top: 1px solid #334155;
    font-size: 11px;
}

/* チェックボックス */
QCheckBox {
    color: #f1f5f9;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #1e293b;
}

QCheckBox::indicator:checked {
    background-color: #38bdf8;
    border-color: #38bdf8;
}

/* スピンボックス */
QSpinBox {
    background-color: #1e293b;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 4px 8px;
    color: #f8fafc;
}
"""

def create_status_icon(has_warning: bool = False, has_special: bool = False, has_quake: bool = False) -> QIcon:
    """ステータスに応じたトレイ用動的アイコンを生成"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # 背景円
    if has_special:
        bg_color = QColor("#dc2626")  # 赤 (特別警報)
        ring_color = QColor("#f87171")
    elif has_warning:
        bg_color = QColor("#ea580c")  # オレンジ (警報)
        ring_color = QColor("#fb923c")
    elif has_quake:
        bg_color = QColor("#9333ea")  # 紫 (地震)
        ring_color = QColor("#c084fc")
    else:
        bg_color = QColor("#0284c7")  # 青 (平常/予報)
        ring_color = QColor("#38bdf8")

    # メインサークル
    painter.setBrush(QBrush(bg_color))
    painter.setPen(QPen(ring_color, 4))
    painter.drawEllipse(6, 6, 52, 52)

    # アイコンシンボル (JMA の J または 雲/警報マーク)
    painter.setPen(QPen(QColor("#ffffff"), 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setFont(QFont("sans-serif", 22, QFont.Bold))
    
    symbol = "!" if (has_special or has_warning) else ("J" if not has_quake else "Q")
    painter.drawText(QRectF(0, 0, 64, 64), Qt.AlignCenter, symbol)

    painter.end()
    return QIcon(pixmap)
