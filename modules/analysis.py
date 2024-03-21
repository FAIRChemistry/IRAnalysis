"""
This module contains the class to perform the necessary analysis on 
the measurement data that has been parsed by the ir_file_handler module.
"""

from matplotlib.style import available
from sdRDM import DataModel
from datamodel.core import Value, Fit, Series, SamplePreparation, Experiment
from modules.ir_file_handler import IRDataFiles
from modules import utils
from typing import List, Optional, Union
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from numpy.typing import ArrayLike
from astropy import units as u
from scipy.stats import norm
from pybaselines.classification import fastchrom

# defining inverse centimeters use across the file
inv_cm = "1 / cm"
# default extiontion coefficients from doi.org/10.1006/jcat.1993.1145
# more accurate coefficients may be obtained from doi.org/10.1016/j.jcat.2020.03.003
extinction_default = {
    "Lewis": u.Quantity(2.22e4, u.meter / u.mol),
    "Bronsted": u.Quantity(1.67e4, u.meter / u.mol),
}


class IRAnalysis(IRDataFiles):
    """
    Class containing necessary functions for IR data analysis, that has
    previously been parsed by the ir_file_handler module.
    """

    def __init__(self, measurement_files: IRDataFiles, **kwargs):
        """
        Args:
            measurement_files (IRDataFiles): IRDataFiles object created
            with file handler module
        """
        super().__init__(measurement_files.directory, **measurement_files.kwargs)
        self._measurements = measurement_files.datamodel.experiment[0].measurements
        self._background_df = measurement_files._background_df
        self._datamodel = measurement_files._datamodel
        self._background_object = self._set_background_object()
        self._analysis_objects = self._add_analysis_objects()
        self.region_of_interest = kwargs.get("region_of_interest", (1400, 1560))
        self._baseline_bool = kwargs.get("fit_baseline", True)
        self._prepare_analysis_data()
        self._extract_bands()
        self._extinction_coefficients = self._define_extinction_coefficients(
            kwargs.get("extinction_coefficients", extinction_default)
        )

    def _set_background_object(self):
        """Sets the variable _background_object to the background object
        defined in the IRDataFiles object. Only one "background" object
        is considered.

        Returns:
            Measurement Object: Measurement object that has the measurement
            type "Background".
        """
        for measurement_object in self._measurements:
            if measurement_object.measurement_type == "Background":
                return measurement_object

    def _add_analysis_objects(self):
        """Function add new analysis objects for the datamodel with
        sample and background references of the corresponding measurement
        object. Corrected data is equal to measured data in this first
        step. Updates _analysis_objects variable.

        Returns:
            ListPlus: ListPlus of all analysis objects in the experiment.
        """
        for measurement_object in self._measurements:
            if measurement_object.measurement_type == "Sample":
                self._datamodel.experiment[0].add_to_analysis(
                    sample_reference=measurement_object.id,
                    background_reference=self._background_object.id,
                    corrected_data=measurement_object.measurement_data,
                )
        return self._datamodel.experiment[0].analysis

    def _prepare_analysis_data(self):
        """Function substracts the background intensity from the sample
        measurement and truncates the data to the region of interest.
        """
        for analysis_object in self._analysis_objects:
            self._substract_background(analysis_object)
            self._truncate_data(analysis_object)
            if self._baseline_bool:
                self._baseline_correction(analysis_object)

    def _substract_background(self, analysis_object):
        """
        Function substracts the intensity of the background from all
        analysis objects.

        Args:
            analysis_object (datamodel.Analysis): Analysis object as
            specified in the sdRDM datamodel.
        """
        background_intensity = self._background_df["intensity"].to_numpy()
        analysis_object.corrected_data.y_axis.data_array -= background_intensity

    def _truncate_data(self, analysis_object):
        """This function truncates the backround corrected data to the
        specified region of interest.

        Args:
            analysis_object (datamodel.Analysis): Analysis object as
            specified in the sdRDM datamodel.
        """
        analysis_data = {
            "wavenumber": analysis_object.corrected_data.x_axis.data_array,
            "intensity": analysis_object.corrected_data.y_axis.data_array,
        }
        analysis_df = utils._dataframe_truncate(
            pd.DataFrame(analysis_data), self.region_of_interest
        )
        analysis_object.corrected_data.x_axis.data_array = analysis_df[
            "wavenumber"
        ].to_numpy()
        analysis_object.corrected_data.y_axis.data_array = analysis_df[
            "intensity"
        ].to_numpy()

    def _baseline_correction(self, analysis_object):
        """Function baseline corrects the previously background corrected
        and truncated intensity data and adds the updated data as well as
        the found baseline itself to the datamodel.
        """
        # prevent baseline correction to be executed on already corrected data
        if analysis_object.baseline != None:
            print(
                f"No baseline calculated for {analysis_object.id}. Baseline already corrected."
            )
            return f"No baseline calculated for {analysis_object.id}. Baseline already corrected."

        # read in background corrected data from datamodel
        corrected_intensity = analysis_object.corrected_data.y_axis.data_array
        corrected_wavenumber = analysis_object.corrected_data.x_axis.data_array
        # calculate baseline
        baseline, _ = fastchrom(corrected_intensity, xdata=corrected_wavenumber)
        # Create baseline dataset
        baseline_series = Series(
            data_array=baseline,
            unit="dimensionless",
        )
        # update corrected_data in datamodel and add baseline data
        analysis_object.corrected_data.y_axis.data_array = (
            corrected_intensity - baseline
        )
        analysis_object.baseline = baseline_series

    def _extract_bands(self):
        """Identifies bands within the corrected spectra and writes the band
        properties to the datmodel.
        """
        for analysis_object in self._analysis_objects:
            analysis_data = {
                "wavenumber": analysis_object.corrected_data.x_axis.data_array,
                "intensity": analysis_object.corrected_data.y_axis.data_array,
            }
            analysis_data_df = pd.DataFrame(analysis_data)
            bands = utils._find_bands(analysis_data_df)
            # Iterating over the rows in the bands dataframe and assingning units to the values
            for band_no in bands.index:
                peak = Value(value=bands.loc[band_no, "peaks"], unit=inv_cm)
                start = Value(value=bands.loc[band_no, "peak_min"], unit=inv_cm)
                end = Value(value=bands.loc[band_no, "peak_max"], unit=inv_cm)
                band_data = utils._dataframe_truncate(
                    analysis_data_df, (start.value, end.value)
                )
                fit = self._fit_band(band_data, band_center=peak.value)
                assignment = utils._auto_assign_band(peak)
                analysis_object.add_to_bands(
                    assignment=assignment, location=peak, start=start, end=end, fit=fit
                )

    def _fit_band(self, band_data: pd.DataFrame, band_center: float):
        """Fits a Gauss-Lorentz curve to given band data and returns the
        fitted data as a fit object as defined in the data model.

        Args:
            band_data (pd.DataFrame): corrected spectral data in the range of the band
            band_center (float): center of the band

        Returns:
            fit: fit_object as defined in the data model
        """
        popt = utils._fit_gl_curve(band_data, curve_center=band_center)
        fit_model = "Gauss-Lorentz"
        fit_formula = "..."
        fit_center = Value(value=popt[0], unit=inv_cm)
        fit_std_dev = Value(value=popt[1], unit=inv_cm)
        fit_area = Value(value=popt[2], unit=inv_cm)
        fit_l_fraction = Value(value=popt[3], unit="dimensionless")
        fit_parameters = [fit_center, fit_std_dev, fit_area, fit_l_fraction]
        fit_object = Fit(
            model=fit_model,
            formula=fit_formula,
            parameters=fit_parameters,
            area=fit_area,
        )
        return fit_object

    def fit_control_plot(self, spectrum_no: int, **kwargs):
        """Draws a plot to control the band identification of a given corrected spectrum.
        For each band, a line is drawn from its start to its end.

        Args:
            spectrum_no (int): Index of the sprectrum within analysis_objects
        """
        analysis_object = self._analysis_objects[spectrum_no]
        analysis_data = {
            "wavenumber": analysis_object.corrected_data.x_axis.data_array,
            "intensity": analysis_object.corrected_data.y_axis.data_array,
        }
        data_df = pd.DataFrame(analysis_data)
        plt.plot(
            data_df["wavenumber"],
            data_df["intensity"],
            color="C1",
            label="corrected data",
        )
        peak_df = utils._find_bands(data_df)
        plt.hlines(*peak_df.iloc[:, 1:].T.to_numpy(), color="C3", label="bands")
        plt.legend()
        plt.show()

    def plot(self, **kwargs):
        """Draws a 2D plot of all spectra in analysis_objects for controlling purposes."""
        fig, ax = plt.subplots(
            figsize=kwargs.get("figsize", (6.4, 4.8)), dpi=kwargs.get("dpi", 100)
        )
        for analysis_object in self._analysis_objects:
            sample_data = {
                "wavenumber": analysis_object.corrected_data.x_axis.data_array,
                "intensity": analysis_object.corrected_data.y_axis.data_array,
            }
            sample_data_df = pd.DataFrame(sample_data)
            sample_data_df = utils._dataframe_truncate(
                sample_data_df, self.region_of_interest
            )
            ax.plot(
                sample_data_df["wavenumber"],
                sample_data_df["intensity"],
                label=analysis_object.sample_reference,
            )
        plt.legend(title="Filenames:", loc="upper left", bbox_to_anchor=(-0.2, -0.2))
        plt.show()

    def plane_plot(self, **kwargs):
        """Draws a 3D plot of all the corrected spectra on a slightly
        angled plane for controlling purposes."""
        fig = plt.figure(
            figsize=kwargs.get("figsize", (17, 8)), dpi=kwargs.get("dpi", 120)
        )
        ax = fig.add_subplot(projection="3d")

        xticks = np.linspace(
            min(self.region_of_interest), max(self.region_of_interest), num=6
        )
        # if yticks is not given, each spectrum is numbered from 0 to n on the y axis
        yticks = kwargs.get("yticks", range(len(self._analysis_objects)))

        for analysis_object, ytick in zip(self._analysis_objects, yticks):
            sample_data = {
                "wavenumber": analysis_object.corrected_data.x_axis.data_array,
                "intensity": analysis_object.corrected_data.y_axis.data_array,
            }
            sample_data_df = pd.DataFrame(sample_data)
            sample_data_df = utils._dataframe_truncate(
                sample_data_df, self.region_of_interest
            )
            ax.plot(
                sample_data_df["wavenumber"],
                sample_data_df["intensity"],
                zs=ytick,
                zdir="y",
            )

        ax.set_xlabel("wavenumber / cm$^{-1}$")
        ax.set_ylabel("temperature / °C")
        ax.set_zlabel("intensity / arb. u.")

        # On the y-axis let's only label the discrete values.
        ax.set_yticks(yticks)
        ax.set_xticks(xticks)
        ax.set_zticks([])
        # Removing grid and background for cleaner look
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor("w")
        ax.yaxis.pane.set_edgecolor("w")
        ax.grid(False)
        ax.view_init(elev=10, azim=-80)  # "Camera" angle
        plt.show()

    def fit_plot(self, spectrum_no: int, **kwargs):
        """Creates a plot of the corrected spectrum and the fitted areas
        for controlling purposes.

        Args:
            spectrum_no (int): Index of the desired spectrum within
                analysis_objects
        """
        analysis_object = self._analysis_objects[spectrum_no]
        analysis_data = {
            "wavenumber": analysis_object.corrected_data.x_axis.data_array,
            "intensity": analysis_object.corrected_data.y_axis.data_array,
        }
        data_df = pd.DataFrame(analysis_data)
        data_df = utils._dataframe_truncate(data_df, self.region_of_interest)
        fig, ax = plt.subplots(
            figsize=kwargs.get("figsize", (9, 5)), dpi=kwargs.get("dpi", 150)
        )
        ax.plot(
            data_df["wavenumber"],
            data_df["intensity"],
            color="blue",
            label="corrected data",
        )

        # using the fit parameters from the datamodel to draw a fit for every band
        i = 1
        for band in analysis_object.bands:
            xfit = np.linspace(band.start.value, band.end.value)
            yfit = utils._gauss_lorentz_curve(
                xfit,
                loc=band.fit.parameters[0].value,
                scale=band.fit.parameters[1].value,
                area=band.fit.parameters[2].value,
                l_fraction=band.fit.parameters[3].value,
            )
            # We only want one legend label for the fittet curves. This is given to the last fit
            if i < len(analysis_object.bands):
                ax.fill_between(xfit, yfit, min(yfit), alpha=0.7, color="gray")
            else:
                ax.fill_between(
                    xfit,
                    yfit,
                    min(yfit),
                    alpha=0.7,
                    color="gray",
                    label="calculated fit",
                )

            i += 1

        ax.set_xlabel("wavenumber / cm$^{-1}$")
        ax.set_ylabel("intensity / arb. u.")
        plt.legend()
        plt.show()

    def _fill_sample_preparation(self, preparation_dict: dict):
        """Fills SamplePreparation object in the DataModel with data
        provided in preparation_dict

        Args:
            preparation_dict (dict): Dict with keys matching available
            fields in the data model.
        """
        # all available Fields of SamplePreparation except ID
        available = list(SamplePreparation.model_fields.keys())[1:]
        sample_object = SamplePreparation()
        for attribute in preparation_dict:
            if attribute in available:
                # Checking whether a Value object is expected for the given attribute
                if (
                    sample_object.__annotations__[attribute].__args__[0].__name__
                    == "Value"
                ):
                    quantity = u.Quantity(preparation_dict[attribute])
                    value_object = Value(value=quantity.value, unit=f"{quantity.unit}")
                    setattr(sample_object, attribute, value_object)
                else:
                    setattr(sample_object, attribute, preparation_dict[attribute])
            else:
                print(f"{attribute} is an unknown field.")
        self._datamodel.experiment[0].sample_preparation = sample_object

    def _define_extinction_coefficients(self, coefficients: dict) -> dict:
        if not isinstance(coefficients, dict):
            raise TypeError(
                "Coefficients must be a dict. Keys are name of Band e.g. Lewis or Bronsted"
            )
        for key in coefficients:
            if not isinstance(coefficients[key], u.Quantity):
                print("Si units m * mol-1 were assumed for", key)
                coefficients[key] = u.Quantity(coefficients[key], u.m / u.mol)
        return coefficients

    def _quantify_from_area(self, peak_area, extinction_coefficient):
        """Returns the quantity of the desired species calculated form peak area,
        sample area, the extinction coefficient and the sample mass.

        Args:
            peak_area (float or u.Quantity): peak area as calculated from the band fit
            extinction_coefficient (float or u.Quantity): molar extinction coefficient for the species

        Returns:
           u.Quantity: Species quantity usually in dimension mol / kg
        """
        sample_mass = utils._get_quantity_object(
            self._datamodel.experiment[0].sample_preparation.mass
        )
        sample_area = utils._get_quantity_object(
            self._datamodel.experiment[0].sample_preparation.area
        )
        return (sample_area * peak_area) / (sample_mass * extinction_coefficient)

    """def quantify(self, **kwargs):
        extinction_coefficients = kwargs.get('extinction_coefficients', self._extinction_coefficients)
        for analysis_object in self._analysis_objects:
            for band in analysis_object.bands:
                if band.assignment in extinction_coefficients:
                    extinction_coefficient = extinction_coefficients[band.assignment]
                else:
    """
