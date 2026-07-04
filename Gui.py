import sys
from PyQt6.QtWidgets import (QMainWindow, QToolBar, QApplication, QFileDialog,
                             QPushButton, QMessageBox, QVBoxLayout, QWidget,
                             QHBoxLayout, QLineEdit, QLabel, QFormLayout,
                             QDialog, QDialogButtonBox, QDoubleSpinBox)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.resize(800, 500)
        self.setWindowTitle("ME Analysis Tool")
        

    def init_ui(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        
        # Toolbar
        toolbar = QToolBar() 
        self.addToolBar(toolbar)
        self.FFT = toolbar.addAction("FFT")   # FFT button
        self.Sum_sqrt = toolbar.addAction("Sum & Sqrt")  # Sum & Sqrt button
        self.MECurve = toolbar.addAction("ME Curve")  # ME Curve button
        self.MTCurve = toolbar.addAction("MT Curve")  # MT Curve button

        # file menu
        self.load_file = file_menu.addAction("open file")
        self.load_folder = file_menu.addAction("open folder")
        self.save_as = file_menu.addAction("save as")

        # create a figure
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
         # frequency range input
        self.f_min_input = QLineEdit("65")
        self.f_max_input = QLineEdit("75")
        
        # 新增輸入元件
        parameter_layout = QHBoxLayout()
        parameter_layout.addWidget(QLabel("f_min:"))  
        parameter_layout.addWidget(self.f_min_input)
        parameter_layout.addWidget(QLabel("f_max:"))
        parameter_layout.addWidget(self.f_max_input)
        layout.addLayout(parameter_layout)
