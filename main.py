import sys
from PySide6.QtWidgets import QApplication

from ui.icons import preparar_assets_qss
from ui.main_window import FileFlowWindow
from ui.theme import gerar_stylesheet


def main():
    app = QApplication(sys.argv)
    assets = preparar_assets_qss()
    app.setStyleSheet(gerar_stylesheet(assets))

    janela = FileFlowWindow()
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()