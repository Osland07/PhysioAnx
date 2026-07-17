import sys
import os
from PySide6.QtWidgets import QApplication
from models.database import init_db


def load_stylesheet(app):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    qss_path = os.path.join(current_dir, 'assets', 'styles', 'theme.qss')

    try:
        with open(qss_path, 'r') as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Peringatan: File theme.qss tidak ditemukan.")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    app = QApplication(sys.argv)
    load_stylesheet(app)

    init_db()

    from login_window import LoginWindow
    from main_window import MainWindow

    login = LoginWindow()

    def on_login_accepted():
        user = login.get_logged_in_user()
        login.close()
        window = MainWindow(current_user=user)
        window.show()

    login.accept_login = on_login_accepted
    login.show()

    sys.exit(app.exec())
