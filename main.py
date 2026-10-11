"""MediaShelf — десктопное приложение «Домашняя медиатека» (PySide6)."""
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QDialog

from models import Library
from storage import Storage
from widgets import LoginDialog, MainWindow


class Application:
    BASE_DIR = Path(__file__).resolve().parent
    DATA_FILE = BASE_DIR / "library.csv"
    REPORT_FILE = BASE_DIR / "report.txt"

    @staticmethod
    def run() -> int:
        app = QApplication(sys.argv)

        login_dialog = LoginDialog()
        if login_dialog.exec() != QDialog.DialogCode.Accepted:
            return 0

        items = Storage.load_items(Application.DATA_FILE)
        library = Library(items if items is not None else Library.seed())

        window = MainWindow(login_dialog.login, library,
                            Application.DATA_FILE, Application.REPORT_FILE)
        window.show()
        return app.exec()


if __name__ == "__main__":
    sys.exit(Application.run())
