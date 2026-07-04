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
        self.Shift_peak = toolbar.addAction("Shift Peaks")   # Shift Peaks button
        self.Fit = toolbar.addAction("Fit")  # Fit button
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
        self.target_freq_input = QLineEdit("70")
        
        # 新增輸入元件
        parameter_layout = QHBoxLayout()
        parameter_layout.addWidget(QLabel("f_min:"))  
        parameter_layout.addWidget(self.f_min_input)
        parameter_layout.addWidget(QLabel("f_max:"))
        parameter_layout.addWidget(self.f_max_input)
        parameter_layout.addWidget(QLabel("Target Frequency:"))
        parameter_layout.addWidget(self.target_freq_input)
        layout.addLayout(parameter_layout)


        

class TemperatureRangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Temperature Range")
        self.init_ui()

    def init_ui(self):
        Layout = QFormLayout()

        self.t_min_label  = QLabel("T_min:")
        self.t_min_input = QDoubleSpinBox()     # T_min輸入(允許小數)
        self.t_min_input.setValue(180)     # 下限預設值
        self.t_min_input.setRange(0, 1000)  # 設定合理的範圍
        self.t_min_input.setSuffix(" K")  # 顯示單位
    
        self.t_max_label = QLabel("T_max:")
        self.t_max_input = QDoubleSpinBox()     # T_max輸入(允許小數)
        self.t_max_input.setValue(300)     # 上限預設值
        self.t_max_input.setRange(0, 1000)  # 設定合理的範圍
        self.t_max_input.setSuffix(" K")  # 顯示單位

        Layout.addRow(self.t_min_label, self.t_min_input)
        Layout.addRow(self.t_max_label, self.t_max_input)

        self.setLayout(Layout)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        Layout.addRow(buttons)

    def get_temperature_range(self):
        return self.t_min_input.value(), self.t_max_input.value()

        

    

        

