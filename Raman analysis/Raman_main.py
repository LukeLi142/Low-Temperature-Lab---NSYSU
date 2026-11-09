import sys

from PyQt6.QtWidgets import QApplication

from Raman_Gui import RamanWindow


def main():

    app = QApplication(
        sys.argv
    )

    window = RamanWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()