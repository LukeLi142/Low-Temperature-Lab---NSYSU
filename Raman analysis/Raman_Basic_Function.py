import numpy as np

from scipy.optimize import curve_fit


# =========================================================
# Lorentzian
# =========================================================

def lorentzian(x, amplitude, center, fwhm):
    """
    Lorentzian peak.

    amplitude : peak height
    center    : peak center (cm^-1)
    fwhm      : full width at half maximum (cm^-1)
    """

    gamma = fwhm / 2.0

    return (
        amplitude
        * gamma**2
        / ((x - center)**2 + gamma**2)
    )


# =========================================================
# Linear background
# =========================================================

def linear_background(x, intercept, slope):
    """
    Linear background:
        y = intercept + slope * x
    """

    return intercept + slope * x


# =========================================================
# Total Raman model
# =========================================================

def raman_model(
    x,
    intercept,
    slope,
    amplitude,
    center,
    fwhm
):
    """
    Raman model:

        Linear background + Lorentzian
    """

    background = linear_background(
        x,
        intercept,
        slope
    )

    peak = lorentzian(
        x,
        amplitude,
        center,
        fwhm
    )

    return background + peak


# =========================================================
# Estimate initial background
# =========================================================

def double_raman_model(x, intercept, slope, *peak_parameters):
    """Two Lorentzian peaks sharing a linear background."""
    return (
        linear_background(x, intercept, slope)
        + lorentzian(x, *peak_parameters[:3])
        + lorentzian(x, *peak_parameters[3:])
    )


def prepare_initial_parameters(initial_parameters, defaults, lower, upper):
    """Validate a previous fit and keep its starting values within new bounds."""
    if initial_parameters is None:
        return defaults
    initial = np.asarray(initial_parameters, dtype=float)
    if initial.shape != (len(defaults),) or not np.all(np.isfinite(initial)):
        raise ValueError("Previous fit parameters have an invalid size or value.")
    return np.clip(initial, lower, upper).copy()


def fit_two_peaks(x, y, center_guesses, half_window=12.0,
                  center_tolerance=5.0, initial_parameters=None):
    """Fit both peaks jointly from the left center-window to the right+window.

    Peak identities are ordered by center; the midpoint separates their bounds.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    centers = np.sort(np.asarray(center_guesses, dtype=float))
    if centers.shape != (2,) or not np.all(np.isfinite(centers)):
        raise ValueError("Select exactly two finite peak positions.")
    if centers[0] == centers[1]:
        raise ValueError("Select two different peak positions.")
    if half_window <= 0.05 or center_tolerance <= 0:
        raise ValueError("Fitting window and center tolerance must be positive.")
    if x.ndim != 1 or y.shape != x.shape:
        raise ValueError("x and y must be matching one-dimensional arrays.")
    mask = (np.isfinite(x) & np.isfinite(y)
            & (x >= centers[0] - half_window)
            & (x <= centers[1] + half_window))
    order = np.argsort(x[mask])
    x_fit, y_fit = x[mask][order], y[mask][order]
    if len(np.unique(x_fit)) < 12:
        raise ValueError("Too few data points in fitting range (need at least 12).")
    if centers[0] < x_fit.min() or centers[1] > x_fit.max():
        raise ValueError("Selected peak positions must lie within the data range.")

    intercept, slope = estimate_background(x_fit, y_fit)
    signal = y_fit - linear_background(x_fit, intercept, slope)
    p0 = [intercept, slope]
    lower, upper = [-np.inf, -np.inf], [np.inf, np.inf]
    midpoint = np.mean(centers)
    for index, center in enumerate(centers):
        low = max(center - center_tolerance, x_fit.min(),
                  midpoint if index == 1 else -np.inf)
        high = min(center + center_tolerance, x_fit.max(),
                   midpoint if index == 0 else np.inf)
        local = (x_fit >= low) & (x_fit <= high)
        amplitude = max(float(np.max(signal[local])) if local.any() else 0.0,
                        float(np.ptp(y_fit)) * 0.1, 1e-6)
        p0.extend([amplitude, center, min(5.0, half_window)])
        lower.extend([0.0, low, 0.1])
        upper.extend([np.inf, high, half_window * 2.0])

    p0 = prepare_initial_parameters(initial_parameters, p0, lower, upper)
    parameters, covariance = curve_fit(
        double_raman_model, x_fit, y_fit, p0=p0,
        bounds=(lower, upper), maxfev=50000)
    errors = np.sqrt(np.diag(covariance))
    peaks = []
    for offset in (2, 5):
        amplitude, center, fwhm = parameters[offset:offset + 3]
        gradient = np.array([np.pi * fwhm / 2, np.pi * amplitude / 2])
        indices = [offset, offset + 2]
        area_variance = gradient @ covariance[np.ix_(indices, indices)] @ gradient
        peaks.append({
            "amplitude": amplitude, "amplitude_error": errors[offset],
            "center": center, "center_error": errors[offset + 1],
            "fwhm": fwhm, "fwhm_error": errors[offset + 2],
            "area": lorentzian_area(amplitude, fwhm),
            "area_error": np.sqrt(area_variance) if area_variance >= 0 else np.nan,
            "peak": lorentzian(x_fit, amplitude, center, fwhm),
        })
    fitted = double_raman_model(x_fit, *parameters)
    residual = y_fit - fitted
    return {
        "x_fit": x_fit, "y_fit": y_fit, "fit": fitted,
        "background": linear_background(x_fit, *parameters[:2]),
        "residual": residual, "rmse": np.sqrt(np.mean(residual**2)),
        "parameters": parameters, "covariance": covariance, "peaks": peaks,
    }


def estimate_background(x, y):
    """
    Estimate linear background using
    points from both edges of fitting region.
    """

    n = len(x)

    n_edge = max(3, n // 6)

    x_edge = np.concatenate(
        [
            x[:n_edge],
            x[-n_edge:]
        ]
    )

    y_edge = np.concatenate(
        [
            y[:n_edge],
            y[-n_edge:]
        ]
    )

    slope, intercept = np.polyfit(
        x_edge,
        y_edge,
        1
    )

    return intercept, slope


# =========================================================
# Lorentzian integrated area
# =========================================================

def lorentzian_area(amplitude, fwhm):
    """
    Integrated area of Lorentzian:

        Area = pi/2 * amplitude * FWHM
    """

    return (
        np.pi
        * amplitude
        * fwhm
        / 2.0
    )


# =========================================================
# Single peak fitting
# =========================================================

def fit_single_peak(
    x,
    y,
    center_guess,
    half_window=12.0,
    center_tolerance=5.0,
    initial_parameters=None
):

    # -----------------------------------------------------
    # Select fitting region
    # -----------------------------------------------------

    mask = (
        (x >= center_guess - half_window)
        &
        (x <= center_guess + half_window)
    )

    x_fit = x[mask]
    y_fit = y[mask]

    if len(x_fit) < 8:
        raise ValueError(
            "Too few data points in fitting range."
        )

    # -----------------------------------------------------
    # Background initial guess
    # -----------------------------------------------------

    intercept_guess, slope_guess = (
        estimate_background(
            x_fit,
            y_fit
        )
    )

    background_guess = linear_background(
        x_fit,
        intercept_guess,
        slope_guess
    )

    # -----------------------------------------------------
    # Amplitude initial guess
    # -----------------------------------------------------

    signal = y_fit - background_guess

    amplitude_guess = np.max(signal)

    if amplitude_guess <= 0:
        amplitude_guess = (
            np.max(y_fit)
            - np.min(y_fit)
        )

    # -----------------------------------------------------
    # FWHM initial guess
    # -----------------------------------------------------

    fwhm_guess = min(
        5.0,
        half_window
    )

    # -----------------------------------------------------
    # Initial parameters
    # -----------------------------------------------------

    p0 = [
        intercept_guess,
        slope_guess,
        amplitude_guess,
        center_guess,
        fwhm_guess
    ]

    # -----------------------------------------------------
    # Parameter bounds
    # -----------------------------------------------------

    lower_bounds = [
        -np.inf,                       # intercept
        -np.inf,                       # slope
        0.0,                           # amplitude
        center_guess-center_tolerance,
        0.1                            # FWHM
    ]

    upper_bounds = [
        np.inf,
        np.inf,
        np.inf,
        center_guess+center_tolerance,
        half_window * 2.0
    ]

    # -----------------------------------------------------
    # Fit
    # -----------------------------------------------------

    p0 = prepare_initial_parameters(
        initial_parameters, p0, lower_bounds, upper_bounds)
    popt, pcov = curve_fit(
        raman_model,
        x_fit,
        y_fit,
        p0=p0,
        bounds=(
            lower_bounds,
            upper_bounds
        ),
        maxfev=50000
    )

    # -----------------------------------------------------
    # Extract parameters
    # -----------------------------------------------------

    (
        intercept,
        slope,
        amplitude,
        center,
        fwhm
    ) = popt

    errors = np.sqrt(
        np.diag(pcov)
    )

    (
        intercept_error,
        slope_error,
        amplitude_error,
        center_error,
        fwhm_error
    ) = errors

    # -----------------------------------------------------
    # Calculate fitting curves
    # -----------------------------------------------------

    y_model = raman_model(
        x_fit,
        *popt
    )

    background = linear_background(
        x_fit,
        intercept,
        slope
    )

    peak = lorentzian(
        x_fit,
        amplitude,
        center,
        fwhm
    )

    residual = (
        y_fit
        - y_model
    )

    # -----------------------------------------------------
    # RMSE
    # -----------------------------------------------------

    rmse = np.sqrt(
        np.mean(
            residual**2
        )
    )

    # -----------------------------------------------------
    # Area
    # -----------------------------------------------------

    area = lorentzian_area(
        amplitude,
        fwhm
    )

    # -----------------------------------------------------
    # Area uncertainty
    #
    # Area = pi/2 * A * FWHM
    #
    # Include covariance between A and FWHM
    # -----------------------------------------------------

    d_area_d_amp = (
        np.pi
        * fwhm
        / 2.0
    )

    d_area_d_fwhm = (
        np.pi
        * amplitude
        / 2.0
    )

    area_variance = (
        d_area_d_amp**2
        * pcov[2, 2]

        +

        d_area_d_fwhm**2
        * pcov[4, 4]

        +

        2
        * d_area_d_amp
        * d_area_d_fwhm
        * pcov[2, 4]
    )

    if area_variance >= 0:
        area_error = np.sqrt(
            area_variance
        )
    else:
        area_error = np.nan

    # -----------------------------------------------------
    # Return everything
    # -----------------------------------------------------

    result = {

        "x_fit": x_fit,
        "y_fit": y_fit,

        "fit": y_model,
        "background": background,
        "peak": peak,

        "residual": residual,

        "intercept": intercept,
        "slope": slope,

        "amplitude": amplitude,
        "amplitude_error": amplitude_error,

        "center": center,
        "center_error": center_error,

        "fwhm": fwhm,
        "fwhm_error": fwhm_error,

        "area": area,
        "area_error": area_error,

        "rmse": rmse,

        "parameters": popt,
        "covariance": pcov
    }

    return result
