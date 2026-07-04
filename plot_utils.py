import os
import numpy as np
import matplotlib.pyplot as plt
from analysis import Analysis
import load_data

# =========================
# Plot Raw data
# =========================

def plot_raw(ax, results):
    """
    Plot raw data to check data is fine.
    """
    ax.clear() # Clear the axes before plotting
    
# =========================
# Plot FFT results
# =========================

def plot_fft(ax, results, f_min, f_max):
    """
    Plot FFT results on the given axes.
    """
    ax.clear()  # Clear the axes before plotting

    for r in results:
        freqs = r["freqs"]
        amplitude = r["amplitude"]
        voltage = r["AC voltage"]
        
        freqs = r["shifted_freqs"] if r["shifted_freqs"] is not None else r["freqs"]
        mask = (freqs >= f_min) & (freqs <= f_max)

        ax.plot(freqs[mask],
                 amplitude[mask],
                 label=f"{voltage} V")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Amplitude")
    ax.set_title("FFT Overlay")
    ax.legend()
    ax.grid(True)

# =========================
# Plot best fitting results
# =========================

def plot_fitting_results(ax, results, f_min, f_max):
    ax.clear()

    for r in results:
        freqs = r["shifted_freqs"] if r["shifted_freqs"] is not None else r["freqs"]
        amplitude = r["amplitude"]
        AC_voltage = r["AC voltage"]
        fit_result = r["Fit results"]

        mask = (freqs >= f_min) & (freqs <= f_max)
        ax.plot(
            freqs[mask],
            amplitude[mask],
            label=f"{AC_voltage} V - Data",
            linestyle="dashed"
        )

        if fit_result is not None:
            ax.plot(
                fit_result["x_fit"],   # 或改成 x_fit
                fit_result["y_fit"],
                linewidth=2,
                label=f"{AC_voltage} V - {fit_result['model']} fit"
            )

    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Fitting Results")
    ax.legend()
    ax.grid(True)

# =========================
# Plot ME results
# =========================

def plot_me_results(ax, results):
    ax.clear()
   
    for r in results:
        AC_voltage = r["AC voltage"]
        induced_m = r["calculated induced M"]
        ax.scatter(AC_voltage, induced_m, label=f"{AC_voltage:.0f} V", s=100)
        
    ax.set_xlabel("AC Voltage (V)")
    ax.set_ylabel("Induced Magnetization (a.u.)")
    ax.set_title("Induced Magnetization vs AC Voltage")
    ax.legend()
    ax.grid(True)

# =========================
# Plot MT results
# =========================

def plot_mt_results(ax, results):
    ax.clear()

    for r in results:
        Temperature = r["Temperature"]
        #induced_m = r["Fit results"]["fit induced M"] if r["Fit results"] is not None else np.nan
        induced_m = r["calculated induced M"]
        ax.scatter(Temperature, induced_m, s=100)
    ax.set_xlabel("Temperature (K)")
    ax.set_ylabel("Induced Magnetization (a.u.)")
    ax.set_title("Induced Magnetization vs Temperature")
    ax.legend()
    ax.grid(True)



