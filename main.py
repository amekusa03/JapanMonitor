# -*- coding: utf-8 -*-
"""
気象庁内部JSON直結 監視＆トレイ常駐通知 アプリケーション
エントリーポイント
"""

import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from app_theme import create_status_icon


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JmaMonitor")
    app.setApplicationDisplayName("気象庁 直接JSON監視モニター")
    app.setWindowIcon(create_status_icon())

    # トレイ常駐アプリのため、最後のウィンドウを閉じてもアプリケーションを終了しない
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()

    # コマンドライン引数に --minimized または --tray が含まれる場合はウィンドウを表示せず最初からトレイ常駐
    if "--minimized" not in sys.argv and "--tray" not in sys.argv:
        window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
