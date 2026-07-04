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
        self.real = np.real(self.fft_vals)
        self.imag = np.imag(self.fft_vals)
        self.magnitude = np.sqrt(self.real**2 + self.imag**2)
        self.amplitude = np.abs(self.fft_vals) / self.N
        self.amplitude[1:-1] *= 2 # Amplitude Normalization (retangle window)
        self.phase = np.degrees(np.arctan2(self.imag, self.real))
        self.phase = np.degrees(np.unwrap(np.angle(self.fft_vals)))
        self.power = (self.amplitude ** 2)/2
        self.power_db = 10 * np.log10(self.power + 1e-20) #避免log(0)
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

    # =========================
    # Gaussian fitting
    # =========================

    def gaussian(self, x, b0, b1, Area, f0, fwhm_gaussian):
        """
        bg: baseline
        Area: Area under the curve
        f0: center frequency
        fwhm_gaussian: full-width at half-maximum for Gaussian
        """
        bg = b0 + b1 * (x - f0)  # Simple linear baseline
        return bg + Area * np.exp((-4 * np.log(2) * (x - f0)**2) / (fwhm_gaussian**2) ) / (fwhm_gaussian * np.sqrt(np.pi / (4 * np.log(2))))  # Normalize area to A
    
    # =========================
    # Lorentzian fitting
    # =========================

    def lorentzian(self, x, b0, b1, Area, f0, fwhm_lorentzian):
        """
        bg: baseline
        Area: Area under the curve
        f0: center frequency
        fwhm_lorentzian: full-width at half-maximum for Lorentzian
        """
        bg = b0 + b1 * (x - f0)  # Simple linear baseline
        return bg + (2 * Area / np.pi) * (fwhm_lorentzian / ((4 * (x - f0)**2) + fwhm_lorentzian**2))  # Normalize area to A
    
    # =========================
    # Linear background fitting
    # =========================
    
    

    # =========================
    # Reduced Chi-Square
    # =========================

    def reduced_chi_square(self, y, y_fit, num_params):
        chi2 = np.sum((y - y_fit) ** 2)

        dof = len(y) - num_params

        if dof <= 0:
            return np.nan

        return chi2 / dof
    
    # =========================
    # Fitting peak
    # =========================

    def fit_peak(self, freqs, amplitude, f_min_fit, f_max_fit):

        """
        Use two different models to fit the fft peak and get the FWHM of the peak.
        We will compare two fitting results by reduced chi-square to determine which model is better,
        and return the fitting result of the better model.
        """
        fit_result = {}
        # Input data
        freqs = np.asarray(freqs)
        amplitude = np.asarray(amplitude)
        mask = (freqs >= f_min_fit) & (freqs <= f_max_fit)
        x_data = freqs[mask]
        y_data = amplitude[mask]
        df = np.mean(np.diff(x_data))  # Frequency resolution

        """
        Initial guess for the fitting parameters is crucial for the convergence of the fitting algorithm.
        """
        b0_guess = np.min(y_data)
        b1_guess = 0  # Assuming no initial slope
        Area_gaussian_guess = 10
        Area_lorentzian_guess = 1
        f0_guess = x_data[np.argmax(y_data)]
        fwhm_gaussian_guess = 4
        fwhm_lorentzian_guess = 2
        # bound of fitting parameters
        lower_bounds = [0, -np.inf, 0, f_min_fit, 0]  # b0 >= 0, Area >= 0, f0 >= f_min_fit, fwhm >= 0
        upper_bounds = [np.inf, np.inf, np.inf, f_max_fit, np.inf]  # f0 <= f_max_fit

        # ==========================
        # Gaussian Fit
        # ==========================
        try:
            p0_gaussian = [b0_guess, b1_guess, Area_gaussian_guess, f0_guess, fwhm_gaussian_guess]

            popt_g, pcov_g = curve_fit(self.gaussian, x_data, y_data, p0=p0_gaussian, bounds=(lower_bounds, upper_bounds), maxfev=10000)
            y_fit_gaussian = self.gaussian(x_data, *popt_g)
            chi2_gaussian = self.reduced_chi_square(y_data, y_fit_gaussian, len(popt_g))
            bg_gaussian = popt_g[0] + popt_g[1] * (x_data - popt_g[3])  # Linear background for Gaussian
            error_gaussian = np.sqrt(np.diag(pcov_g))

            
            # store Gaussian fit results
            fit_result["gaussian"] = {
                "model": "gaussian",
                "fit success": True,
                "chi2": chi2_gaussian,
                "x_fit": x_data.copy(),
                "y_data": y_data.copy(),
                "y_fit": y_fit_gaussian.copy(),
                "fwhm": popt_g[4],
                "fwhm error": error_gaussian[4],
                "fit induced M": np.sqrt(popt_g[2] / df),
                "fit induced M error": (error_gaussian[2] / df)
            }
        except RuntimeError:
            fit_result["gaussian"] = {
                "model": "gaussian",
                "fit success": False,
                "chi2": np.inf,
                "x_fit": x_data.copy(),
                "y_data": y_data.copy(),
                "y_fit": np.full_like(x_data, np.nan),
                "fwhm": np.nan,
                "fwhm error": np.nan,
                "fit induced M": np.nan,
                "fit induced M error": np.nan
            }

        # ==========================
        # Lorentzian Fit
        # ==========================
        try:
            p0_lorentzian = [b0_guess, b1_guess, Area_lorentzian_guess, f0_guess, fwhm_lorentzian_guess]
            popt_l, pcov_l = curve_fit(self.lorentzian, x_data, y_data, p0=p0_lorentzian, bounds=(lower_bounds, upper_bounds), maxfev=10000)
            y_fit_lorentzian = self.lorentzian(x_data, *popt_l)
            chi2_lorentzian = self.reduced_chi_square(y_data, y_fit_lorentzian, len(popt_l))
            lorentzian_bg = popt_l[0] + popt_l[1] * (x_data - popt_l[3])  # Linear background for Lorentzian
            error_lorentzian = np.sqrt(np.diag(pcov_l))

            # store Lorentzian fit results
            fit_result["lorentzian"] = {
                "model": "lorentzian",
                "fit success": True,
                "chi2": chi2_lorentzian,
                "x_fit": x_data.copy(),
                "y_data": y_data.copy(),
                "y_fit": y_fit_lorentzian.copy(),
                "fwhm": popt_l[4],
                "fwhm error": error_lorentzian[4],
                "fit induced M": np.sqrt(popt_l[2] / df),
                "fit induced M error": (error_lorentzian[2] / df)
            }
        except RuntimeError:
            fit_result["lorentzian"] = {
                "model": "lorentzian",
                "fit success": False,
                "chi2": np.inf,
                "x_fit": x_data.copy(),
                "y_data": y_data.copy(),
                "y_fit": np.full_like(x_data, np.nan),
                "fwhm": np.nan,
                "fwhm error": np.nan,
                "fit induced M": np.nan,
                "fit induced M error": np.nan
            }

        best_model = min(fit_result, key=lambda k: fit_result[k]["chi2"])
        fit_result["best_model"] = best_model
        return fit_result[best_model]
    
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
    # Linear background subtraction and sum & sqrt
    # ==========================

    def linear_bg_and_sum_sqrt(self, freqs, amplitude, f_min_fit, f_max_fit):
        # Linear background fitting
        mask = (freqs >= f_min_fit) & (freqs <= f_max_fit)
        x_data = freqs[mask]
        y_data = amplitude[mask]

        # linear background fitting
        slope, intercept = np.polyfit(x_data, y_data, 1)
        linear_bg = slope * x_data + intercept
        y_data_bg_subtracted = y_data - linear_bg

        # Sum and sqrt of background-subtracted amplitude
        sum_bg_subtracted = np.sum((abs(y_data_bg_subtracted) / 1000) ** 2)  # Convert to V and sum
        sqrt_sum_amplitude = np.sqrt(sum_bg_subtracted) * 1000  # Convert back to mV
            
        fit_result = {}
        fit_result["linear_bg"] = {
            "model": "linear_bg",
            "fit success": True,
            "chi2": None,
            "x_fit": x_data.copy(),
            "y_data": y_data.copy(),
            "y_fit": linear_bg.copy(),
            "fwhm": np.nan,
            "fwhm error": np.nan,
            "fit induced M": sqrt_sum_amplitude,
            "fit induced M error": np.nan
            }
        

        return fit_result["linear_bg"]
