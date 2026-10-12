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

def plot_fft(axes, result_groups, f_min, f_max):
    """
    Plot scans separately and overlay all file averages on one shared axes.
    """
    for ax, group in zip(axes, result_groups):
        ax.clear()
        is_average = group[0].get("type") == "average"
        curve_name = "Average" if is_average else f"Scan {group[0].get('scan_number', '?')}"

        for r in group:
            freqs = r["frequency"]
            amplitude = r["amplitude"]
            mask = (freqs >= f_min) & (freqs <= f_max)
            color = ("tab:orange" if len(group) == 1 else None) if is_average else "tab:blue"
            ax.plot(freqs[mask],
                    amplitude[mask],
                    label=r["file"] if is_average else curve_name,
                    linewidth=2.5 if is_average else 1.0,
                    color=color)

        ax.set_xlim(f_min, f_max)
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Amplitude")
        ax.set_title(curve_name)
        ax.grid(True)
        if is_average:
            ax.legend(fontsize="small")

# =========================
# Plot ME results
# =========================

def plot_me_results(ax, results):
    ax.clear()
   
    for r in results:
        AC_Vrms = r["AC_Vrms"]
        induced_m = r["calculated induced M"]
        ax.scatter(AC_Vrms, induced_m, label=f"{AC_Vrms:.0f} V", s=100)
        
    ax.set_xlabel("AC_rms(V)")
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
    ax.grid(True)


def plot_position_results(ax, results):
    """Plot the Sum & Sqrt amplitude of each scan and average by position."""
    ax.clear()
    for result_type, label, color, size in [
        ("individual", "Scans", "tab:blue", 40),
        ("average", "Average", "tab:orange", 100),
    ]:
        points = sorted((r for r in results if r.get("type") == result_type),
                        key=lambda r: r["Position"])
        if points:
            ax.scatter([r["Position"] for r in points],
                       [r["calculated induced M"] for r in points],
                       label=label, color=color, s=size)
    ax.set_xlabel("Sample position (cm)")
    ax.set_ylabel("Amplitude (mV)")
    ax.set_title("Amplitude vs Position")
    ax.legend()
    ax.grid(True)


