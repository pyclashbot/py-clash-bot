import sys
from PySide6.QtWidgets import QApplication
from pyclashbot.interface.layout import (
    FrontEnd,
)  # Adjust the import based on the actual file name and location


def main():
    app = QApplication(sys.argv)
    frontend = FrontEnd()
    frontend.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
