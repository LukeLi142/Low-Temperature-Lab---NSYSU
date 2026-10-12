import sys
from PyQt6.QtWidgets import (QMainWindow, QToolBar, QApplication, QFileDialog,
                             QPushButton, QMessageBox, QVBoxLayout, QWidget,
                             QHBoxLayout, QLineEdit, QLabel, QFormLayout,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QCheckBox,
                             QScrollArea)
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
        self.Position = toolbar.addAction("Position")
        self.Position.setToolTip("Plot Sum & Sqrt amplitude against the position after P_ in the filename.")

        # Checkbox
        self.showallgraph_checkbox = QCheckBox("Show All Graphs")
        self.showallgraph_checkbox.setChecked(True)  # Set default state to checked

        # file menu
        self.load_file = file_menu.addAction("open file")
        self.load_folder = file_menu.addAction("open folder")
        self.save_as = file_menu.addAction("save as")

        # create a figure
        self.figure = Figure(constrained_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.create_plot_axes()
        self.plot_scroll = QScrollArea()
        self.plot_scroll.setWidgetResizable(True)
        self.plot_scroll.setWidget(self.canvas)

        layout = QVBoxLayout()
        layout.addWidget(self.plot_scroll, stretch=1)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        layout.addWidget(self.showallgraph_checkbox)
        
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

    def create_plot_axes(self, count=1):
        """Create separate plots, keeping each row readable in the scroll area."""
        count = max(1, count)
        columns = 2 if count > 1 else 1
        rows = (count + columns - 1) // columns
        self.figure.clear()
        self.axes = [self.figure.add_subplot(rows, columns, index + 1)
                     for index in range(count)]
        self.ax = self.axes[0]
        self.canvas.setMinimumHeight(rows * 280)
        return self.axes
