import load_data
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class Analysis:
    def __init__(self, data, duration):
       self.data = data
       self.duration = duration
       self.dt = duration / 240000 # second
       self.f = 1/self.dt # Hz
       self.N = len(self.data) # 數據長度
       
       self.freqs = None
       self.amplitude = None
       self.fft_vals = None
       self.shifted_freqs = None
    # FFT分析
    def FFT(self):
        signal = self.data - np.mean(self.data)
        self.fft_vals = np.fft.rfft(signal) # rfft 取正頻率
        self.freqs = np.fft.rfftfreq(self.N, d=self.dt) # frequency bins
        self.amplitude = np.abs(self.fft_vals) / self.N
        self.amplitude[1:-1] *= 2 # Amplitude Normalization (retangle window)
        return self.freqs, self.amplitude



    # 在頻率範圍內自動找peak
    def find_and_shift_peak(self, f_min_peak, f_max_peak, target_freq):
        if self.freqs is None or self.amplitude is None:
                raise ValueError("Please run FFT() before finding peaks.")
        self.mask = (self.freqs >= f_min_peak) & (self.freqs <= f_max_peak)
        peak_index = np.argmax(self.amplitude[self.mask])
        peak_freq = self.freqs[self.mask][peak_index]
        shift = target_freq - peak_freq
        self.shifted_freqs = self.freqs + shift
        return self.shifted_freqs

    
    # ==========================
    # Sum and square root of amplitude
    # ==========================

    def sum_and_sqrt_amplitude(self, freqs, amplitude, f_min_sum, f_max_sum):
        mask = (freqs >= f_min_sum) & (freqs <= f_max_sum)

        # linear background subtraction
        x_data = freqs[mask]
        y_data = amplitude[mask]
        slope, intercept = np.polyfit(x_data, y_data, 1)
        linear_bg = slope * x_data + intercept
        y_data_bg_subtracted = y_data - linear_bg
        square_amplitude = (y_data_bg_subtracted / 1000) ** 2
        sum_amplitude = np.sum(square_amplitude)
        sqrt_sum_amplitude = np.sqrt(sum_amplitude) * 1000  # Convert back to mV
        return sqrt_sum_amplitude

