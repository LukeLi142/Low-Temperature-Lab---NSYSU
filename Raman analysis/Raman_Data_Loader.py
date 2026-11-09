import numpy as np


def load_raman_data(file_path):
    """
    Load Raman data.

    Expected format:
        column 1: Raman shift (cm^-1)
        column 2: Intensity
    """

    data = np.loadtxt(file_path)

    if data.ndim != 2:
        raise ValueError("Data must be a 2D array.")

    if data.shape[1] < 2:
        raise ValueError(
            "Raman file must contain at least two columns."
        )

    x = data[:, 0].astype(float)
    y = data[:, 1].astype(float)

    # Remove invalid values
    valid = np.isfinite(x) & np.isfinite(y)

    x = x[valid]
    y = y[valid]

    # Make sure Raman shift is increasing
    order = np.argsort(x)

    x = x[order]
    y = y[order]

    return x, y