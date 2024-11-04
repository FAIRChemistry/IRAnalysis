"""
Module contains utility functions used in the IR analysis module
"""

from types import NoneType
import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from scipy.stats import norm, cauchy
from scipy.signal import find_peaks, peak_widths
from scipy.optimize import curve_fit
from astropy import units as u

from datamodel.core import fit
from datamodel.core.value import Value


def _dataframe_truncate(dataframe: pd.DataFrame, wavenumber_region) -> pd.DataFrame:
    """
    Function truncates dataframe to the specified wavenumber region

    Args:
        dataframe (pd.DataFrame): Dataframe containing wavenumber column
        wavenumber_region: Tuple, List, or ArrayLike containing minimum and maximum
            wavenumber values

    Returns:
        pd.DataFrame: Truncated dataframe
    """
    wavenumber_region = np.array(wavenumber_region)
    truncated_df = dataframe[
        (dataframe["wavenumber"] < wavenumber_region.max())
        & (dataframe["wavenumber"] > wavenumber_region.min())
    ]
    return truncated_df


def _single_gauss(
    self, wavenumber: ArrayLike, area: float, mean: float, std_dev: float
) -> np.ndarray:
    """Defines the function of a regular gaussian normal distribution
    (probability density funtion / pdf) with the factor "area" to
    scale the area under the peak (usually =! 1).

    Args:
        wavenumber (ArrayLike): wavenumber region of the peak
        area (float): Area of the peak, usually != 1.
        mean (float): Center of the peak
        std_dev (float): Standard deviation of the distribution

    Returns:
        np.ndarray: Absorption values of the gaussian distribution
    """
    return norm.pdf(wavenumber, loc=mean, scale=std_dev) * area


def _find_bands(spectrum_df: pd.DataFrame, 
                prominence:float = 0.01,
                rel_height:float = 0.96) -> pd.DataFrame:
    """Function to find peak centers and the region where the peak starts
    and ends.

    Args:
        spectrum (pd.DataFrame): DataFrame with wavenumber and absorbance
            columns
        prominence (float): Minimum prominence of the peak to be detected
        rel_height (float): Relative height of the base of the peak to be considered

    Returns:
        pd.DataFrame: Peak center, height of the peak base, peak start,
            peak end columns.
    """
    peaks, _ = find_peaks(spectrum_df["intensity"], prominence=prominence)
    widths = peak_widths(spectrum_df["intensity"], peaks, rel_height=rel_height)
    """
    peak_widths interpolates the starting and endpoint of the peak.
    The returned start and end values from peak_widths correspond to the 
    indices of wavenumber indices in the dataframe. Floats have to be 
    rounded for iloc to accept them.
    """
    peak_base_height = widths[1]
    peak_min = spectrum_df["wavenumber"].iloc[widths[2].round()].to_numpy()
    peak_max = spectrum_df["wavenumber"].iloc[widths[3].round()].to_numpy()
    bands_data = {
        "peaks": spectrum_df["wavenumber"].iloc[peaks.round()],
        "peak_base_height": peak_base_height,
        "peak_min": peak_min,
        "peak_max": peak_max,
    }
    return pd.DataFrame(bands_data)


def _gauss_lorentz_curve(
    x: np.ndarray, area: float, loc: float, scale: float, l_fraction: float
) -> np.ndarray:
    """Linear combination of a Gaussian and Lorentzian distribution

    Args:
        x (np.ndarray): x values where the curve values will be calculated as
        loc (float): mean
        scale (float): standard deviation
        area (float): area of the resulting curve
        l_fraction (float): Factor of the Lorentzian in the linear combination [0,1]

    Returns:
        np.ndarray: y values of the curve
    """
    beta = 1 / np.sqrt(2 * np.log(2))
    gauss = norm.pdf(x, loc=loc, scale=beta * scale)
    lorentz = cauchy.pdf(x, loc=loc, scale=scale)
    return area * (l_fraction * lorentz + (1 - l_fraction) * gauss)


def _fit_curve(
    data_df: pd.DataFrame,
    fit_model,
    fit_parameter_bounds,
    fit_parameter_guesses) -> tuple[np.ndarray, np.ndarray]:
    """Fits data with a gauss-lorentz curve and returns the found parameters

    Args:
        data_df (pd.DataFrame): DataFrame with wavenumber and intensity data
        curve_center (float): Predicted center of the curve as starting
            parameter for the algorithm

    Returns:
        np.ndarray: fitting parameters (mean, std.deviation, area, lorentz fraction)
    """
    popt_gl, pcov_gl = curve_fit(
        fit_model,
        data_df["wavenumber"],
        data_df["intensity"],
        p0=fit_parameter_guesses,
        bounds=fit_parameter_bounds,
    )
    return popt_gl, pcov_gl


def _get_quantity_object(value_object: Value, error=False, **kwargs) -> u.Quantity:
    """Creates an Astropy Quantity object from the value and unit of a
    value_object from the data model. Unit can be explicitly specified

    Args:
        value_object (Value): Value object from the IR data model
        error (bool), optional: Whether to use the error value or the actual value
        unit (string), optional: Desired unit of the value

    Returns:
        u.Quantity: Astropy Quantity object for the given value
    """
    unit = kwargs.get("unit", value_object.unit.to_unit_string())
    if error:
        quantity_object = u.Quantity(value_object.error, unit)
    else:
        quantity_object = u.Quantity(value_object.value, unit)
    return quantity_object


def _auto_assign_band(peak_location: Value, expected_peaks: pd.DataFrame) -> str:
    """Takes a band object from the data model, determines the smallest
    difference in peak location and returns the corresponding dict key.

    Args:
        peak_location (Value): Band object of the data model that has location data.
        expected_peaks (pd.DataFrame): DataFrame with expected peak locations and peak
            name as index
    Returns:
        str: Peak assignment closest to known values
    """
    difference_to_expected = np.array(
        [
            np.abs(exp_loc.value - peak_location.value)
            for exp_loc in expected_peaks["location"]
        ]
    )
    closest_to_expected = list(expected_peaks.index)[
        difference_to_expected.argmin()
    ]
    return closest_to_expected

def _value_to_string(value: Value) -> str:
    """Converts a value object to a string representation

    Args:
        value (Value): Value object from the data model

    Returns:
        str: LaTeX string representation of the value with its error
    """
    if value.error:
        # determine number of significant decimals
        significant_decimals = int(np.ceil(- np.log10(value.error)))
        #rounding
        significant_value = round(value.value, significant_decimals)
        significant_error = round(value.error, significant_decimals)
        return f"${significant_value} \pm {significant_error}$"
    else:
        significant_decimals = 3
        significant_value = round(value.value, significant_decimals)
        return f"${significant_value}$"