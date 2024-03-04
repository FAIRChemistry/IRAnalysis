# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 12:18:35 2022

@author: Selina Itzigehl
"""

from sys import stderr
import matplotlib.pyplot as plt
from matplotlib import gridspec
import os
import pandas as pd
from pathlib import Path
import numpy as np
from scipy.signal import find_peaks, peak_widths
from scipy.optimize import curve_fit
from typing import List, Optional, Union


class GaussianFit:
    """
    Determination of initial parameters by peak finding.
    Parameter optimisation for Gaussian fit to data.
    """

    def __init__(
        self,
        path_to_directory: Optional[Union[str, bytes, os.PathLike]],
        threshold: float = 0.1,
    ) -> None:
        """Initialization of the class.

        Args:
            path_to_directory (Optional[Union[str, bytes, os.PathLike]]): path to directory
            threshold (float, optional): threshold for peak finding. Defaults to 0.1.
        """
        path = list(Path(path_to_directory).glob("*.csv"))
        self.path = path_to_directory
        self.input_files = {file.stem: file for file in path if file.is_file()}
        self.x_array = []
        self.y_array = []
        self.threshold = threshold
        self.height = []
        self.center = []
        self.width = []
        self.fwhm = []
        self.peaks = []
        self.number_of_sites = []
        self.opt_params = None
        self.pars_1 = None
        self.pars_2 = None
        self.pars_3 = None
        self.gauss_peak1 = None
        self.gauss_peak2 = None
        self.gauss_peak3 = None
        self.residual = None

    def available_files(self) -> List[str]:
        """Gives list of available files for processing

        Returns:
            List[str]: list of files
        """
        return {count: value for count, value in enumerate(self.input_files)}

    def extract_data(self, index: int) -> pd.DataFrame:
        """Extracts data from file to pd.DataFrame.

        Args:
            index (int): index of the file from list of files holding the
            data to be evaluated

        Returns:
            pd.DataFrame: extracted measurement data, "wavenumber" and
            "absorbance"
        """

        df = pd.read_csv(
            self.path / (list(self.input_files)[index] + ".csv"),
            usecols=[1, 2],
            names=["wavenumber", "absorbance"],
            header=1,
            engine="python",
        )

        self.x_array = df["wavenumber"]
        self.y_array = df["absorbance"]

        return self.x_array, self.y_array

    def _find_peaks(self) -> int:
        """Finds peaks in data above given threshold.

        Returns:
            int: number of peaks found
        """
        correction = ((max(self.x_array) - min(self.x_array)) + 1) / len(self.y_array)

        peaks, _ = find_peaks(self.y_array, height=self.threshold, distance=10)
        peak_stats = peak_widths(self.y_array, peaks, rel_height=0.05)

        width = [peak_stats[0][peak] * correction for peak in range(len(peaks))]
        height = [peak_stats[1][peak] for peak in range(len(peaks))]
        center = []
        fwhm = []
        for peak in range(len(peaks)):
            left = peak_stats[2][peak] * correction
            right = peak_stats[3][peak] * correction
            center.append(((left + right) / 2) + self.x_array[0])
            fwhm.append(right - left)

        self.height = height
        self.center = center
        self.width = width
        self.fwhm = fwhm

        return len(peaks)

    def _1gaussian(self, x, amp1, cen1, sigma1) -> function:
        """Definition of single Gaussian (for fitting one peak)

        Args:
            x (array): variable
            amp1 (float): initial height (amplitude)
            cen1 (float): initial center
            sigma1 (float): initial width (sigma)

        Returns:
            function: single Gaussian
        """
        return (
            amp1
            * (1 / (sigma1 * (np.sqrt(2 * np.pi))))
            * (np.exp((-1.0 / 2.0) * (((self.x_array - cen1) / sigma1) ** 2)))
        )

    def _2gaussian(self, x, amp1, cen1, sigma1, amp2, cen2, sigma2) -> function:
        """Definition of doule Gaussian (for fitting two peaks)

        Args:
            x (_type_): variable
            amp1 (_type_): initial hight (amplitude) of first Gaussian
            cen1 (_type_): initial center of first Gaussian
            sigma1 (_type_): initial width (sigma) of first Gaussian
            amp2 (_type_): initial hight (amplitude) of second Gaussian
            cen2 (_type_): initial center of second Gaussian
            sigma2 (_type_): initial width (sigma) of second Gaussian

        Returns:
            function: double Gaussian
        """
        return amp1 * (1 / (sigma1 * (np.sqrt(2 * np.pi)))) * (
            np.exp((-1.0 / 2.0) * (((self.x_array - cen1) / sigma1) ** 2))
        ) + amp2 * (1 / (sigma2 * (np.sqrt(2 * np.pi)))) * (
            np.exp((-1.0 / 2.0) * (((self.x_array - cen2) / sigma2) ** 2))
        )

    def _3gaussian(
        self, x, amp1, cen1, sigma1, amp2, cen2, sigma2, amp3, cen3, sigma3
    ) -> function:
        """Definition of trple Gaussian (for fitting three peaks)

        Args:
            x (_type_): variable
            amp1 (_type_): initial hight (amplitude) of first Gaussian
            cen1 (_type_): initial center of first Gaussian
            sigma1 (_type_): initial width (sigma) of first Gaussian
            amp2 (_type_): initial hight (amplitude) of second Gaussian
            cen2 (_type_): initial center of second Gaussian
            sigma2 (_type_): initial width (sigma) of second Gaussian
            amp3 (_type_): initial height (amplitude) of third Gaussian
            cen3 (_type_): initial center of third Gaussian
            sigma3 (_type_): initial widht (sigma) of third Gaussian
        Returns:
            function: triple Gaussian
        """
        return (
            amp1
            * (1 / (sigma1 * (np.sqrt(2 * np.pi))))
            * (np.exp((-1.0 / 2.0) * (((self.x_array - cen1) / sigma1) ** 2)))
            + amp2
            * (1 / (sigma2 * (np.sqrt(2 * np.pi))))
            * (np.exp((-1.0 / 2.0) * (((self.x_array - cen2) / sigma2) ** 2)))
            + amp3
            * (1 / (sigma3 * (np.sqrt(2 * np.pi))))
            * (np.exp((-1.0 / 2.0) * (((self.x_array - cen3) / sigma3) ** 2)))
        )

    def _gauss_fit2(self) -> list[float]:
        """Adaptation of initial parameters for double Gaussain to data

        Returns:
            list[float]: list of peaks
            list[float]: list of parameters
        """
        self._find_peaks()

        self.opt_params, covar = curve_fit(
            self._2gaussian,
            self.x_array,
            self.y_array,
            p0=[
                parameter
                for sublist in zip(self.height, self.center, self.width)
                for parameter in sublist
            ],
        )
        _stderr = np.sqrt(np.diag(covar))

        self.pars_1 = self.opt_params[0:3]
        self.pars_2 = self.opt_params[3:6]
        self.gauss_peak1 = self._1gaussian(self.x_array, *self.pars_1)
        self.gauss_peak2 = self._1gaussian(self.x_array, *self.pars_2)

        self.residual = self.y_array - (
            self._2gaussian(self.x_array, *(self.opt_params))
        )

        return self.peaks, (
            self.opt_params,
            self.pars_1,
            self.pars_2,
            self.gauss_peak1,
            self.gauss_peak2,
            self.residual,
        )

    def _gauss_fit3(self) -> list[float]:
        """Adaptation of initial parameters for triple Gaussain to data

        Returns:
            list[float]: list of peaks
            list[float]: list of parameters
        """
        self._find_peaks()

        self.opt_params, covar = curve_fit(
            self._3gaussian,
            self.x_array,
            self.y_array,
            p0=[
                parameter
                for sublist in zip(self.height, self.center, self.width)
                for parameter in sublist
            ],
        )
        _stderr = np.sqrt(np.diag(covar))

        self.pars_1 = self.opt_params[0:3]
        self.pars_2 = self.opt_params[3:6]
        self.pars_3 = self.opt_params[6:9]
        self.gauss_peak1 = self._1gaussian(self.x_array, *self.pars_1)
        self.gauss_peak2 = self._1gaussian(self.x_array, *self.pars_2)
        self.gauss_peak3 = self._1gaussian(self.x_array, *self.pars_3)

        self.residual = self.y_array - (
            self._3gaussian(self.x_array, *(self.opt_params))
        )

        return self.peaks, (
            self.opt_params,
            self.pars_1,
            self.pars_2,
            self.pars_3,
            self.gauss_peak1,
            self.gauss_peak2,
            self.gauss_peak3,
            self.residual,
        )

    def calc_n_sites(
        self,
        sample_area: float,
        sample_mass: float,
        abs_coeff: float,
        peaks: int = 3,
    ) -> list[float]:
        """
        Calculates the number of active sites from the coefficients
        obtained from fitting the peaks.

        Args:
            sample_mass (float): Sample mass used for the respective measurement.
            Given in grams.
            abs_coeff (float): Absorption coefficient of the measured material.
            Given in SI units.
            peaks (int): number of fitted peaks. Defaults to 3.

        Raises:
            ValueError: If either or both sample_mass and abs_coeff are not given.

        Returns:
           list[float]: number of active sites, both Bronsted and Lewis.
        """

        self._find_peaks()

        if sample_mass == None:
            raise ValueError("Sample mass must be given.")
        if abs_coeff == None:
            raise ValueError("Absorption coefficient must be given.")
        if sample_area == None:
            raise ValueError("Sample area (wafer size) must be given.")

        if peaks == 2:
            self._gauss_fit2()
            self.number_of_sites.clear()

            peak_area = [
                np.trapz(self.gauss_peak1),
                np.trapz(self.gauss_peak2),
            ]
            for peak in range(len(peak_area)):
                N = (sample_area * peak_area[peak]) / (sample_mass * abs_coeff)
                self.number_of_sites.append(N)
        else:
            self._gauss_fit3()
            self.number_of_sites.clear()

            peak_area = [
                np.trapz(self.gauss_peak1),
                np.trapz(self.gauss_peak2),
                np.trapz(self.gauss_peak3),
            ]
            for peak in range(len(self.height)):
                N = (sample_area * peak_area[peak]) / (sample_mass * abs_coeff)
                self.number_of_sites.append(N)

        return self.number_of_sites

    def get_init_parameters(self) -> dict:
        """Gets initial fitting parameters.

        Returns:
            dict: initial fitting parameters according to variable
        """
        return {
            "height": self.height,
            "center": self.center,
            "width": self.width,
            "fwhm": self.fwhm,
        }

    def get_parameters(self) -> pd.DataFrame:
        """Gets final fitting parameters.

        Returns:
            pd.DataFrame: amplitude, center, sigma and peak area of fits
        """
        self._gauss_fit()
        data = {
            "amplitude": self.height,
            "center": self.center,
            "sigma": self.width,
            "area": [
                np.trapz(self.gauss_peak1),
                np.trapz(self.gauss_peak2),
                np.trapz(self.gauss_peak3),
            ],
        }
        parameters = pd.DataFrame(data=data)
        return parameters

    def get_control_plot(self) -> None:
        """Produces plot of data and found peaks."""
        self._find_peaks()
        plt.plot(
            self.x_array,
            self.y_array,
            linestyle="None",
            marker=".",
            color="red",
        )
        plt.plot(
            self.center,
            self.height,
            linestyle="None",
            marker="v",
            color="g",
        )
        plt.xlim(1560, 1425)
        plt.show()

    def get_gaussian2_plot(self, name: str) -> None:
        """Produces plot with two Gaussian fits.

        Args:
            name (str): name of the saved file
        """
        self._find_peaks()
        self._gauss_fit2()
        fig = plt.figure(figsize=(6, 4.5))
        gs = gridspec.GridSpec(2, 1, height_ratios=[1, 0.25])
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        gs.update(hspace=0)

        ax1.plot(
            self.x_array,
            self.y_array,
            marker=".",
            linestyle="None",
            color="red",
        )
        ax1.plot(
            self.x_array,
            self._2gaussian(self.x_array, *self.opt_params),
            linestyle="--",
            color="black",
        )
        ax1.plot(self.x_array, self.gauss_peak1, color="g", alpha=0.5)
        ax1.fill_between(
            x=self.x_array,
            y1=self.gauss_peak1.min(),
            y2=self.gauss_peak1,
            facecolor="green",
            alpha=0.1,
        )
        ax1.plot(self.x_array, self.gauss_peak2, color="y", alpha=0.5)
        ax1.fill_between(
            x=self.x_array,
            y1=self.gauss_peak2.min(),
            y2=self.gauss_peak2,
            facecolor="yellow",
            alpha=0.1,
        )
        ax1.set_xlabel("$\\nu$ / cm$^{-1}$", fontsize=12)
        ax1.set_ylabel("$A$ / a.u.", fontsize=12)
        ax1.invert_xaxis()
        ax2.plot(
            self.x_array,
            self.residual,
            marker=".",
            linestyle="None",
            color="blue",
        )
        ax2.axhline(0, linestyle="-", linewidth=0.5, color="black")
        ax2.set_xlabel("$\\nu$ / cm$^{-1}$", fontsize=12)
        ax2.set_ylabel("$res.$", fontsize=12)
        ax2.invert_xaxis()
        ax2.set_ylim(-0.3, 0.3)
        fig.savefig(name + "_fit.png", dpi=400)
        fig.show()

    def get_gaussian3_plot(self, name: str) -> None:
        """Produces plot with three Gausian fits.

        Args:
            name (str): name of the saved file
        """
        self._find_peaks()
        self._gauss_fit3()
        fig = plt.figure(figsize=(6, 4.5))
        gs = gridspec.GridSpec(2, 1, height_ratios=[1, 0.25])
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        gs.update(hspace=0)

        ax1.plot(
            self.x_array,
            self.y_array,
            marker=".",
            linestyle="None",
            color="red",
        )
        ax1.plot(
            self.x_array,
            self._3gaussian(self.x_array, *self.opt_params),
            linestyle="--",
            color="black",
        )
        ax1.plot(self.x_array, self.gauss_peak1, color="g", alpha=0.5)
        ax1.fill_between(
            x=self.x_array,
            y1=self.gauss_peak1.min(),
            y2=self.gauss_peak1,
            facecolor="green",
            alpha=0.1,
        )
        ax1.plot(self.x_array, self.gauss_peak2, color="y", alpha=0.5)
        ax1.fill_between(
            x=self.x_array,
            y1=self.gauss_peak2.min(),
            y2=self.gauss_peak2,
            facecolor="yellow",
            alpha=0.1,
        )
        ax1.plot(self.x_array, self.gauss_peak3, color="b", alpha=0.5)
        ax1.fill_between(
            x=self.x_array,
            y1=self.gauss_peak3.min(),
            y2=self.gauss_peak3,
            facecolor="blue",
            alpha=0.1,
        )
        ax1.set_xlabel("$\\nu$ / cm$^{-1}$", fontsize=12)
        ax1.set_ylabel("$A$ / a.u.", fontsize=12)
        ax1.invert_xaxis()
        ax2.plot(
            self.x_array,
            self.residual,
            marker=".",
            linestyle="None",
            color="blue",
        )
        ax2.axhline(0, linestyle="-", linewidth=0.5, color="black")
        ax2.set_xlabel("$\\nu$ / cm$^{-1}$", fontsize=12)
        ax2.set_ylabel("$res.$", fontsize=12)
        ax2.invert_xaxis()
        ax2.set_ylim(-0.3, 0.3)
        fig.savefig(name + "_fit.png", dpi=400)
        fig.show()


if __name__ == "__main__":
    cwd = Path.cwd()
    name = "TO_P84-RT_5_250C"

    test = GaussianFit(cwd / "TO_P84-RT_5/corr")
    test.extract_data(2)

    print(test.get_control_plot())
