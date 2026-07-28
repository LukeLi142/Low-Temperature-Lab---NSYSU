import load_data
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class Analysis:
    def __init__(self):
        self.data = None
        self.dt = None

    # 設定資料
    def set_data(self, data, dt):
        self.data = data
        self.dt = dt
        self.f = 1/self.dt # Hz
        self.N = len(self.data) # 數據長度
        self.freqs = None
        self.amplitude = None
        self.fft_vals = None

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


    # ==========================
    # Uniform frequency axis interpolation
    # ==========================

    def uniform_frequency_axis(self, all_freqs, all_amplitudes):
         """
         當有多組資料時，將它們的頻率軸統一，並對振幅進行插值
         ，以利我們進行振幅的平均。
         """
         # Find the common frequency range
         f_min = max([freqs[0] for freqs in all_freqs])
         f_max = min([freqs[-1] for freqs in all_freqs])
         if f_min >= f_max:
             raise ValueError("No overlapping frequency range found among datasets.")
         
         # First frequnecy data be used as the common frequency axis
         base_freqs = all_freqs[0]
         mask = (base_freqs >= f_min) & (base_freqs <= f_max)
         common_freqs = base_freqs[mask]
         interpolated_amplitudes = []
         
         for freqs, amplitude in zip(all_freqs, all_amplitudes): # zip() 函數將兩個列表打包成一個元組列表，這樣我們可以同時遍歷頻率和振幅
                # Interpolate amplitude to the common frequency axis
                interp_amplitude = np.interp(common_freqs, freqs, amplitude)
                interpolated_amplitudes.append(interp_amplitude)
                return common_freqs, interpolated_amplitudes