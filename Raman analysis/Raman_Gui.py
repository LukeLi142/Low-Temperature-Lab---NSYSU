import os
import numpy as np

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QDoubleSpinBox,
    QComboBox,
    QGroupBox,
    QFormLayout,
    QMessageBox
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas
)

from Raman_Data_Loader import load_raman_data

from Raman_Basic_Function import (
    fit_single_peak,
    fit_two_peaks,
    double_raman_model,
    lorentzian,
    raman_model,
    linear_background
)


class RamanWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # =================================================
        # Data
        # =================================================

        self.x = None
        self.y = None

        self.file_path = None

        # User-clicked position
        self.center_guess = None
        self.center_guesses = []

        # Fitting result
        self.fit_result = None
        self.initial_parameters = None

        # =================================================
        # Window
        # =================================================

        self.setWindowTitle(
            "Raman Analysis"
        )

        self.resize(
            1200,
            800
        )

        # =================================================
        # UI
        # =================================================

        self.init_ui()

    # =====================================================
    # UI
    # =====================================================

    def init_ui(self):

        central_widget = QWidget()

        main_layout = QVBoxLayout(
            central_widget
        )

        # =================================================
        # Top control panel
        # =================================================

        control_layout = QHBoxLayout()

        self.open_button = QPushButton(
            "Open File"
        )

        self.fit_button = QPushButton(
            "Fit Selected Peak"
        )

        self.next_button = QPushButton("Open Next && Fit")
        self.next_button.setEnabled(False)
        self.next_button.setToolTip(
            "Use this fit's parameters as initial values for the next spectrum.")

        self.full_button = QPushButton(
            "Show Full Spectrum"
        )

        self.fit_button.setEnabled(
            False
        )

        self.full_button.setEnabled(
            False
        )

        # Fitting window
        window_label = QLabel(
            "Fitting half-window:"
        )

        self.window_spinbox = (
            QDoubleSpinBox()
        )

        self.window_spinbox.setRange(
            2.0,
            100.0
        )

        self.window_spinbox.setValue(
            12.0
        )

        self.window_spinbox.setSingleStep(
            1.0
        )

        self.window_spinbox.setSuffix(
            " cm⁻¹"
        )

        control_layout.addWidget(
            self.open_button
        )

        self.peak_count = QComboBox()
        self.peak_count.addItems(["1 peak", "2 peaks"])
        control_layout.addWidget(self.peak_count)

        self.clear_button = QPushButton("Clear Selection")
        control_layout.addWidget(self.clear_button)

        control_layout.addWidget(
            self.fit_button
        )

        control_layout.addWidget(
            self.full_button
        )

        control_layout.addSpacing(
            20
        )

        control_layout.addWidget(
            window_label
        )

        control_layout.addWidget(
            self.window_spinbox
        )

        control_layout.addStretch()

        main_layout.addLayout(
            control_layout
        )

        sequential_layout = QHBoxLayout()
        sequential_layout.addWidget(self.next_button)
        self.seed_label = QLabel("Initial values: selected peak(s)")
        sequential_layout.addWidget(self.seed_label)
        sequential_layout.addStretch()
        main_layout.addLayout(sequential_layout)

        # =================================================
        # Figure
        # =================================================

        self.figure = Figure(
            figsize=(10, 7)
        )

        self.canvas = FigureCanvas(
            self.figure
        )

        self.ax_spectrum = (
            self.figure.add_subplot(
                211
            )
        )

        self.ax_residual = (
            self.figure.add_subplot(
                212
            )
        )

        main_layout.addWidget(
            self.canvas,
            stretch=1
        )

        # =================================================
        # Result box
        # =================================================

        result_group = QGroupBox(
            "Fitting Result"
        )

        result_layout = QFormLayout()

        self.clicked_label = QLabel(
            "-"
        )

        self.center_label = QLabel(
            "-"
        )

        self.fwhm_label = QLabel(
            "-"
        )

        self.amplitude_label = QLabel(
            "-"
        )

        self.area_label = QLabel(
            "-"
        )

        self.rmse_label = QLabel(
            "-"
        )

        result_layout.addRow(
            "Clicked position:",
            self.clicked_label
        )

        result_layout.addRow(
            "Peak center:",
            self.center_label
        )

        result_layout.addRow(
            "FWHM:",
            self.fwhm_label
        )

        result_layout.addRow(
            "Amplitude:",
            self.amplitude_label
        )

        result_layout.addRow(
            "Integrated area:",
            self.area_label
        )

        result_layout.addRow(
            "RMSE:",
            self.rmse_label
        )

        result_group.setLayout(
            result_layout
        )

        main_layout.addWidget(
            result_group
        )

        # =================================================
        # Connections
        # =================================================

        self.open_button.clicked.connect(
            self.open_file
        )

        self.peak_count.currentIndexChanged.connect(self.clear_selection)
        self.clear_button.clicked.connect(self.clear_selection)
        self.next_button.clicked.connect(self.open_next_and_fit)

        self.fit_button.clicked.connect(
            self.fit_selected_peak
        )

        self.full_button.clicked.connect(
            self.show_full_spectrum
        )

        self.window_spinbox.valueChanged.connect(
            self.update_selected_region
        )

        # Matplotlib mouse click
        self.canvas.mpl_connect(
            "button_press_event",
            self.on_plot_click
        )

        # =================================================

        self.setCentralWidget(
            central_widget
        )

        self.statusBar().showMessage(
            "Open a Raman file to begin."
        )

    # =====================================================
    # Open file
    # =====================================================

    def open_file(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Raman Data",
            "",
            "Text files (*.txt *.dat);;"
            "All files (*.*)"
        )

        if not file_path:
            return

        try:

            self.x, self.y = (
                load_raman_data(
                    file_path
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Load Error",
                str(error)
            )

            return

        self.file_path = file_path
        self.initial_parameters = None
        self.seed_label.setText("Initial values: selected peak(s)")

        self.center_guess = None
        self.center_guesses = []
        self.fit_result = None

        self.reset_result_labels()

        self.fit_button.setEnabled(
            False
        )

        self.full_button.setEnabled(
            True
        )

        self.show_full_spectrum()

        self.statusBar().showMessage(
            "Click a Raman peak on the spectrum."
        )

    def open_next_and_fit(self):
        """Only replace the current spectrum after the next fit succeeds."""
        if self.fit_result is None:
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Next Raman Spectrum",
            os.path.dirname(self.file_path) if self.file_path else "",
            "Text files (*.txt *.dat);;All files (*.*)")
        if not file_path:
            return
        previous = self.fit_result
        initial = previous["parameters"].copy()
        peaks = previous.get("peaks", [previous])
        centers = [float(peak["center"]) for peak in peaks]
        try:
            x, y = load_raman_data(file_path)
            if not len(x) or min(centers) < x.min() or max(centers) > x.max():
                raise ValueError("Previous peak centers are outside the next spectrum.")
            fit_function = fit_two_peaks if len(centers) == 2 else fit_single_peak
            result = fit_function(
                x, y, centers if len(centers) == 2 else centers[0],
                half_window=self.window_spinbox.value(),
                initial_parameters=initial)
        except Exception as error:
            QMessageBox.critical(self, "Sequential Fitting Error", str(error))
            return

        source = os.path.basename(self.file_path) if self.file_path else "previous fit"
        self.x, self.y = x, y
        self.file_path = file_path
        self.center_guesses = centers
        self.center_guess = centers[0]
        self.initial_parameters = initial
        self.fit_result = result
        self.clicked_label.setText(" / ".join(f"{c:.3f} cm⁻¹" for c in centers))
        self.seed_label.setText(f"Initial values from: {source}")
        self.plot_fit_result()
        self.update_result_labels()
        self.statusBar().showMessage(
            f"Sequential fit: {source} → {os.path.basename(file_path)}. "
            "Open Next & Fit to continue.")

    # =====================================================
    # Mouse click
    # =====================================================

    def on_plot_click(self, event):

        if self.x is None:
            return

        if event.inaxes != self.ax_spectrum:
            return

        if event.xdata is None:
            return

        # Only left mouse button
        if event.button != 1:
            return

        position = float(event.xdata)
        if not self.x.min() <= position <= self.x.max():
            return
        required = self.peak_count.currentIndex() + 1
        if len(self.center_guesses) == required:
            self.center_guesses = []
        if any(np.isclose(position, center, rtol=0, atol=1e-6)
               for center in self.center_guesses):
            self.statusBar().showMessage("Select a different peak position.")
            return
        self.center_guesses.append(position)
        self.initial_parameters = None
        self.seed_label.setText("Initial values: selected peak(s)")
        self.center_guesses.sort()
        self.center_guess = self.center_guesses[0]
        self.reset_result_labels()
        self.clicked_label.setText(" / ".join(
            f"{center:.3f} cm⁻¹" for center in self.center_guesses))
        ready = len(self.center_guesses) == required
        self.fit_button.setEnabled(ready)
        self.fit_result = None
        self.ax_residual.clear()
        self.ax_residual.set_visible(False)
        self.draw_selected_peak()
        self.statusBar().showMessage(
            "Selection ready. Press Fit." if ready
            else "First peak selected. Click the second peak."
        )

    def clear_selection(self, *_):
        self.initial_parameters = None
        self.seed_label.setText("Initial values: selected peak(s)")
        self.center_guess = None
        self.center_guesses = []
        self.fit_result = None
        self.reset_result_labels()
        self.fit_button.setEnabled(False)
        count = self.peak_count.currentIndex() + 1
        self.fit_button.setText("Fit Selected Peak" if count == 1
                                else "Fit Selected Peaks")
        self.show_full_spectrum()
        self.statusBar().showMessage(f"Click {count} peak(s) on the spectrum.")

    # =====================================================
    # Draw full spectrum
    # =====================================================

    def show_full_spectrum(self):

        if self.x is None:
            return

        self.ax_spectrum.clear()
        self.ax_residual.clear()

        self.ax_spectrum.plot(
            self.x,
            self.y,
            linewidth=1
        )

        self.ax_spectrum.set_xlabel(
            "Raman Shift (cm⁻¹)"
        )

        self.ax_spectrum.set_ylabel(
            "Intensity"
        )

        if self.file_path:

            filename = os.path.basename(
                self.file_path
            )

            self.ax_spectrum.set_title(
                filename
            )

        self.ax_residual.set_visible(
            False
        )

        if self.center_guess is not None:
            self.draw_selected_peak(
                redraw=False
            )

        self.figure.tight_layout()

        self.canvas.draw_idle()

    # =====================================================
    # Draw selected peak
    # =====================================================

    def draw_selected_peak(
        self,
        redraw=True
    ):

        if self.x is None:
            return

        if self.center_guess is None:
            return

        # Redraw full spectrum
        self.ax_spectrum.clear()

        self.ax_spectrum.plot(
            self.x,
            self.y,
            linewidth=1,
            label="Data"
        )

        half_window = (
            self.window_spinbox.value()
        )

        xmin = (
            min(self.center_guesses)
            - half_window
        )

        xmax = (
            max(self.center_guesses)
            + half_window
        )

        # Clicked position
        for index, center in enumerate(self.center_guesses, 1):
            self.ax_spectrum.axvline(
                center, linestyle="--", label=f"Selected peak {index}")

        # Fitting region
        self.ax_spectrum.axvspan(
            xmin,
            xmax,
            alpha=0.15,
            label="Fitting region"
        )

        self.ax_spectrum.set_xlabel(
            "Raman Shift (cm⁻¹)"
        )

        self.ax_spectrum.set_ylabel(
            "Intensity"
        )

        if self.file_path:

            filename = os.path.basename(
                self.file_path
            )

            self.ax_spectrum.set_title(
                filename
            )

        self.ax_spectrum.legend()

        if redraw:

            self.figure.tight_layout()

            self.canvas.draw_idle()

    # =====================================================
    # Update fitting region
    # =====================================================

    def update_selected_region(self):

        if self.center_guess is None:
            return

        self.fit_result = None
        self.reset_result_labels()
        self.clicked_label.setText(" / ".join(
            f"{center:.3f} cm⁻¹" for center in self.center_guesses))
        self.ax_residual.clear()
        self.ax_residual.set_visible(False)
        self.draw_selected_peak()

    # =====================================================
    # Fit
    # =====================================================

    def fit_selected_peak(self):

        if self.x is None:
            return

        if self.center_guess is None:
            return

        if len(self.center_guesses) != self.peak_count.currentIndex() + 1:
            return

        half_window = (
            self.window_spinbox.value()
        )

        try:

            fit_function = (fit_two_peaks if len(self.center_guesses) == 2
                            else fit_single_peak)
            selection = (self.center_guesses if len(self.center_guesses) == 2
                         else self.center_guess)
            result = fit_function(
                self.x,
                self.y,
                selection,
                half_window=half_window,
                initial_parameters=self.initial_parameters
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Fitting Error",
                str(error)
            )

            return

        self.fit_result = result
        self.next_button.setEnabled(True)

        self.plot_fit_result()

        self.update_result_labels()

        self.statusBar().showMessage(
            "Fitting completed."
        )

    # =====================================================
    # Plot fitting result
    # =====================================================

    def plot_fit_result(self):

        result = self.fit_result

        if result is None:
            return

        x_fit = result["x_fit"]
        y_fit = result["y_fit"]

        # Smooth x-axis for fitting curve
        x_dense = np.linspace(
            x_fit.min(),
            x_fit.max(),
            1000
        )

        parameters = (
            result["parameters"]
        )

        model = double_raman_model if "peaks" in result else raman_model
        y_dense = model(
            x_dense,
            *parameters
        )

        background_dense = (
            linear_background(
                x_dense,
                parameters[0],
                parameters[1]
            )
        )

        # =================================================
        # Main fitting figure
        # =================================================

        self.ax_spectrum.clear()

        self.ax_spectrum.plot(
            x_fit,
            y_fit,
            "o",
            markersize=4,
            label="Data"
        )

        self.ax_spectrum.plot(
            x_dense,
            y_dense,
            linewidth=2,
            label="Lorentzian Fit"
        )

        self.ax_spectrum.plot(
            x_dense,
            background_dense,
            linestyle="--",
            label="Linear Background"
        )

        peaks = result.get("peaks", [result])
        for index, (initial, peak) in enumerate(
                zip(self.center_guesses, peaks), 1):
            self.ax_spectrum.axvline(
                initial, linestyle=":", label=f"Initial Center {index}")
            self.ax_spectrum.axvline(
                peak["center"], linestyle="--", label=f"Fitted Center {index}")
            if len(peaks) == 2:
                component = lorentzian(
                    x_dense, peak["amplitude"], peak["center"], peak["fwhm"])
                self.ax_spectrum.plot(
                    x_dense, background_dense + component, linestyle="-.",
                    label=f"Peak {index} + Background")

        self.ax_spectrum.set_xlabel(
            "Raman Shift (cm⁻¹)"
        )

        self.ax_spectrum.set_ylabel(
            "Intensity"
        )

        self.ax_spectrum.set_title(
            (os.path.basename(self.file_path) + " — " if self.file_path else "")
            + ("Two Peak Lorentzian Fitting" if len(peaks) == 2
               else "Single Peak Lorentzian Fitting")
        )

        self.ax_spectrum.legend()

        # =================================================
        # Residual
        # =================================================

        self.ax_residual.set_visible(
            True
        )

        self.ax_residual.clear()

        self.ax_residual.plot(
            x_fit,
            result["residual"],
            "o-",
            markersize=3
        )

        self.ax_residual.axhline(
            0,
            linestyle="--"
        )

        self.ax_residual.set_xlabel(
            "Raman Shift (cm⁻¹)"
        )

        self.ax_residual.set_ylabel(
            "Residual"
        )

        self.figure.tight_layout()

        self.canvas.draw_idle()

    # =====================================================
    # Result labels
    # =====================================================

    def update_result_labels(self):

        result = self.fit_result

        if result is None:
            return

        if "peaks" in result:
            for key, label, unit in (
                ("center", self.center_label, " cm⁻¹"),
                ("fwhm", self.fwhm_label, " cm⁻¹"),
                ("amplitude", self.amplitude_label, ""),
                ("area", self.area_label, ""),
            ):
                label.setText("\n".join(
                    f"Peak {index}: {peak[key]:.4f} ± "
                    f"{peak[key + '_error']:.4f}{unit}"
                    for index, peak in enumerate(result["peaks"], 1)))
            self.rmse_label.setText(f"{result['rmse']:.4f}")
            return

        self.center_label.setText(
            (
                f"{result['center']:.4f} "
                f"± {result['center_error']:.4f} cm⁻¹"
            )
        )

        self.fwhm_label.setText(
            (
                f"{result['fwhm']:.4f} "
                f"± {result['fwhm_error']:.4f} cm⁻¹"
            )
        )

        self.amplitude_label.setText(
            (
                f"{result['amplitude']:.4f} "
                f"± {result['amplitude_error']:.4f}"
            )
        )

        self.area_label.setText(
            (
                f"{result['area']:.4f} "
                f"± {result['area_error']:.4f}"
            )
        )

        self.rmse_label.setText(
            f"{result['rmse']:.4f}"
        )

    # =====================================================
    # Reset labels
    # =====================================================

    def reset_result_labels(self):

        self.next_button.setEnabled(False)
        self.clicked_label.setText("-")
        self.center_label.setText("-")
        self.fwhm_label.setText("-")
        self.amplitude_label.setText("-")
        self.area_label.setText("-")
        self.rmse_label.setText("-")
