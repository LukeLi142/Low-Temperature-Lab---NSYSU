import load_data 
import numpy as np
from analysis import Analysis
import plot_utils as plot
import sys
import glob
import pandas as pd
import os
from Gui import MainWindow
from PyQt6.QtWidgets import (QMainWindow, QToolBar, QApplication, QFileDialog,
                             QPushButton, QMessageBox, QVBoxLayout, QWidget,
                             QHBoxLayout, QLineEdit, QLabel)

class Controller:
    def __init__(self,gui):
        self.gui = gui
        self.files = []     

    # Set status
        self.current_mode = None

    # Connnect GUI signals to controller
        self.gui.load_file.triggered.connect(self.load_file)
        self.gui.FFT.triggered.connect(self.FFT)
        self.gui.load_folder.triggered.connect(self.load_folder)
        self.gui.save_as.triggered.connect(self.save_as)
        self.gui.Sum_sqrt.triggered.connect(self.sum_and_sqrt_amplitude)
        self.gui.MECurve.triggered.connect(self.ME_curve)
        self.gui.MTCurve.triggered.connect(self.MT_curve)
    # Connect input fields to update frequency range
        self.gui.f_min_input.returnPressed.connect(self.update_range)
        self.gui.f_max_input.returnPressed.connect(self.update_range)

    # Load files
    def load_file(self):
        files, _ = QFileDialog.getOpenFileNames(self.gui, "Select Files", "", "Text Files (*.txt )")
        
        self.files = files

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self.gui, "Select Folder")
        
        self.files = glob.glob(os.path.join(folder, "*.txt"))
    
    # =========================
    # FFT analysis
    # =========================

    def FFT(self):
        # Set status
        self.current_mode = "FFT"
        
        # Check if files are loaded
        if self.files is None or len(self.files) == 0:  
            QMessageBox.warning(self.gui, "No selected files", "Please load files before performing FFT analysis.")
            return
        
        # Get frequency range from input fields
        try:
            f_min = float(self.gui.f_min_input.text())
            f_max = float(self.gui.f_max_input.text())
        except ValueError:
            QMessageBox.warning(self.gui, "Invalid input", "Please enter valid numbers for f_min and f_max.")
            return
        
        # Validate frequency range
        if f_min >= f_max:
            QMessageBox.warning(self.gui, "Invalid input", "f_min should be less than f_max.")
            return
        
        self.results = []   # 儲存資料和分析結果的列表

        for file in self.files:
            data, duration = load_data.load_data(file) 
            DC_voltage = load_data.get_dc_voltage_from_filename(file)
            Temperature = load_data.get_temperature_from_filename(file)
            AC_voltage = DC_voltage / np.sqrt(2)  # 計算交流電壓
            analysis = Analysis(data, duration)
            freqs, amplitude = analysis.FFT()
                
            self.results.append({"file":file,
                                 "Temperature":Temperature,
                                 "DC voltage":DC_voltage,
                                 "AC voltage":AC_voltage,
                                 "freqs":freqs,
                                 "amplitude":amplitude,

                                 "data": data,
                                 "duration": duration,
                                 
                                 "shifted_freqs": None,
                                 "Analysis results": None})    # 儲存以計算過資料和分析結果的列表
        
        # plot results
        
        plot.plot_fft(self.gui.ax, self.results, f_min, f_max)
        self.gui.canvas.draw()  # Refresh the canvas to show the new plot    
        
    # =========================
    # Sum and square root of amplitude
    # =========================

    def sum_and_sqrt_amplitude(self):
        """
        Calculate the sum of amplitude within the specified frequency range and then take the square root.
        Then store the calculated M in the results for later use in ME curve plotting.
        """
        # Set status
        self.current_mode = "Sum & Sqrt"
        # Check FFT results
        if not hasattr(self, 'results') or len(self.results) == 0:
            QMessageBox.warning(self.gui, "No FFT results", "Please perform FFT analysis before calculating sum and square root of amplitude.")
            return
        # Get frequency range from input fields
        try:
            f_min_sum = float(self.gui.f_min_input.text())
            f_max_sum = float(self.gui.f_max_input.text())
        except ValueError:
            QMessageBox.warning(self.gui, "Invalid input", "Please enter valid numbers for f_min and f_max.")
            return
        # Validate frequency range
        if f_min_sum >= f_max_sum:
            QMessageBox.warning(self.gui, "Invalid input", "f_min should be less than f_max.")
            return
        for r in self.results:
            analysis = Analysis(r["data"], r["duration"])
            freqs = r["freqs"]
            amplitude = r["amplitude"]
            sum_sqrt_result = analysis.sum_and_sqrt_amplitude(freqs, amplitude, f_min_sum, f_max_sum)
            r["calculated induced M"] = sum_sqrt_result

    # =========================
    # ME Curve
    # =========================

    def ME_curve(self):
        # Set status
        self.current_mode = "ME Curve"
        # Check if calculated M results are available
        if not hasattr(self, 'results') or len(self.results) == 0 or "calculated induced M" not in self.results[0]:
            QMessageBox.warning(self.gui, "No calculated induced M results", "Please perform sum and square root of amplitude calculation before plotting ME curve.")
            return
        
        plot.plot_me_results(self.gui.ax, self.results)
        self.gui.canvas.draw()  # Refresh the canvas to show the new plot

    # =========================
    # MT Curve
    # =========================

    def MT_curve(self):
        # Set status
        self.current_mode = "MT Curve"
        

        plot.plot_mt_results(self.gui.ax, self.results)
        self.gui.canvas.draw()  # Refresh the canvas to show the new plot

    # 改輸出範圍
    def update_range(self):
        if not hasattr(self, 'results') or len(self.results) == 0:
            return  # No results to update
        try:
            f_min = float(self.gui.f_min_input.text())
            f_max = float(self.gui.f_max_input.text())
        except ValueError:
            QMessageBox.warning(self.gui, "Invalid input", "Please enter valid numbers for f_min and f_max.")
            return
        if f_min >= f_max:
            QMessageBox.warning(self.gui, "Invalid input", "f_min should be less than f_max.")
            return
        if self.current_mode =="FFT":
            plot.plot_fft(self.gui.ax, self.results, f_min, f_max)
            self.gui.canvas.draw()  # Refresh the canvas to show the updated plot

    # Shift frequency
    def shift_peaks(self, target_freqs):
        target_freqs = float(self.gui.target_freq_input.text())
        
    # Save Results
    def save_fft_results(self, f_min_save, f_max_save, file_path):
        """
        Save FFT results to a CSV file with the specified frequency range.
        """
        results = sorted(self.results, key=lambda r: r["DC voltage"])
        freqs = self.results[0]['freqs']  # 假設所有文件的頻率範圍相同
        mask = (freqs >= f_min_save) & (freqs <= f_max_save)
        
        df = pd.DataFrame()
        df['frequency'] = freqs[mask]

        # 將每個文件的振幅添加到DataFrame中
        for r in results:
            amplitude = r['amplitude'][mask]
            AC_voltage = r['AC voltage']
            df[f'{AC_voltage}V'] = amplitude
        df.to_csv(file_path, index=False)
    
    # Save ME curve results
    def save_me_results(self, file_path):
        """
        Save ME curve results to a CSV file.
        """
        results = sorted(self.results, key=lambda r: r["DC voltage"])
        rows = []

        for r in results:
            rows.append({
                "DC voltage": r["DC voltage"],
                "AC voltage": r["AC voltage"],
                "calculated induced M": r["calculated induced M"]
            })
        df = pd.DataFrame(rows)
        df.to_csv(file_path, index=False)

    # Save MT curve results
    def save_mt_results(self, file_path):
        """
        Save MT curve results to a CSV file.
        """
        results = sorted(self.results, key=lambda r: r["DC voltage"])
        rows = []

        for r in results:
            rows.append({
                "DC voltage": r["DC voltage"],
                "AC voltage": r["AC voltage"],
                "Temperature": r["Temperature"],
                "calculated induced M": r["calculated induced M"],
                
            })
        df = pd.DataFrame(rows)
        df.to_csv(file_path, index=False)



    def save_as(self):
        if not self.current_mode:
            QMessageBox.warning(self.gui, "No analysis to save", "Please perform an analysis before saving results.")
            return
        
        # Output frequency range
        try:
            f_min_save = float(self.gui.f_min_input.text())
            f_max_save = float(self.gui.f_max_input.text())
        except ValueError:
            QMessageBox.warning(self.gui, "Invalid input", "Please enter valid numbers for f_min and f_max.")
            return
        if f_min_save >= f_max_save:
            QMessageBox.warning(self.gui, "Invalid input", "f_min should be less than f_max.")
            return
        
        # Save file dialog
        file_path, _ = QFileDialog.getSaveFileName(self.gui, "Save Results", "", "CSV Files (*.csv)")
        
        # Save results based on current mode
        if self.current_mode == "FFT":
            self.save_fft_results(f_min_save, f_max_save, file_path)
            QMessageBox.information(self.gui, "Save Successful", f"FFT results saved to {file_path}")
        elif self.current_mode == "ME Curve":
            self.save_me_results(file_path)
            QMessageBox.information(self.gui, "Save Successful", f"ME curve results saved to {file_path}")
        elif self.current_mode == "MT Curve":
            self.save_mt_results(file_path)
            QMessageBox.information(self.gui, "Save Successful", f"MT curve results saved to {file_path}")


    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    controller = Controller(window)
    sys.exit(app.exec())