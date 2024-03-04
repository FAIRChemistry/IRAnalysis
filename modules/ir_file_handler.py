"""
This module contains classes and functions to collect IR data files and
to assign them a role for later analysis.
"""

from sdRDM import DataModel
from datamodel.core import *
import os, glob
from datetime import datetime
from typing import List, Optional, Union
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from astropy import units as u


class IRDataFiles:
    """
    The IRDataFiles class contails all spectra for a given experiment
    and the methods to assign them a role for later analysis.
    """

    def __init__(self, ir_file_directory: str, **kwargs):
        self.directory = ir_file_directory
        self.kwargs = kwargs
        self.datamodel_directory = kwargs.get("datamodel_directory", "./")
        self.detection = kwargs.get("detection", "absorbance")
        self.separator = kwargs.get("separator", ";")
        self.header = kwargs.get("header", None)
        self.column_sequence = kwargs.get(
            "column_sequence", ["wavenumber", "intensity"]
        )
        self.decimal_separator = kwargs.get("decimal", ",")
        self.file_extension = kwargs.get("extension", "csv")
        self._loaded_ir_files = []
        self._datamodel = None
        self._datamodel_lib = DataModel.from_markdown(
            f"{self.datamodel_directory}/specifications"
        )
        self.datetime_created = str(datetime.now())
        self.experiment_name = kwargs.get("experiment_name", "UnspecifiedExperiment")
        self._background_df = pd.DataFrame({"wavenumber": [], "intensity": []})

    @property
    def files(self) -> List[str]:
        """This function returns all files found in the specified
        directory with the given file extension.

        Returns:
            List[str]: List of data file names.
        """
        os.chdir(self.directory)
        self._loaded_ir_files = glob.glob(f"*.{self.file_extension}")
        return self._loaded_ir_files

    @files.setter
    def files(self, user_ir_files: List[str]):
        self._loaded_ir_files = user_ir_files
        return self._loaded_ir_files

    def show_raw_data(self, wavenumber_region=(1560, 1400), legend: bool = False):
        """
        This function generates one plot with every measurement from the
        dataset.
        Args:
            wavenumber_region (tuple, optional): Desired wavenumber
                region to show. Defaults to (1560, 1400).
            legend (bool, optional): Wheter to show a legend containing
                the corresponding filenames. Default is False.
        """
        files = self.files
        wavenumber_region = np.array(wavenumber_region)
        fig, ax = plt.subplots()
        for spectrum in files:
            file_location = str(self.directory) + spectrum
            spectrum_df = pd.read_csv(
                file_location,
                delimiter=self.separator,
                decimal=self.decimal_separator,
                names=self.column_sequence,
                header=self.header,
            )

            # truncating spectrum to desired region
            spectrum_df = spectrum_df[
                (spectrum_df["wavenumber"] < wavenumber_region.max())
                & (spectrum_df["wavenumber"] > wavenumber_region.min())
            ]
            ax.plot(spectrum_df["wavenumber"], spectrum_df["intensity"], label=spectrum)
        plt.xlim(wavenumber_region)
        ax.set_xlabel("$\\nu$ / cm$^{-1}$")
        ax.set_ylabel(f"{self.detection} / a.u.")
        if legend:
            plt.legend(
                title="Filenames:", loc="upper left", bbox_to_anchor=(-0.2, -0.2)
            )
        plt.show()

    @property
    def datamodel(self):
        if self._datamodel == None:
            self._initialize_datamodel()
            return self._datamodel
        else:
            return self._datamodel

    @datamodel.setter
    def datamodel(self, datamodel):
        if isinstance(datamodel, DataModel):
            self._datamodel = datamodel

    def _initialize_datamodel(self) -> DataModel:
        """Function to generate new DataModel on basis of raw measurement
            data from files.

        Returns:
            datamodel_root (DataModel): With added Measurement objects
        """

        # Loading of DataModel as specified in markdown
        # os.chdir(self.datamodel_directory)
        # self._datamodel_lib = DataModel.from_markdown("./specifications")

        # Creating an root instance of the DataModel
        datamodel_root = self._datamodel_lib.IRAnalysis(
            datetime_created=str(self.datetime_created),
        )
        # Creating an Experiment instance of the DataModel
        datamodel_root_experiment = self._datamodel_lib.Experiment(
            name=self.experiment_name
        )
        for spectrum in self.files:
            file_location = str(self.directory) + spectrum
            spectrum_df = pd.read_csv(
                file_location,
                delimiter=self.separator,
                decimal=self.decimal_separator,
                names=self.column_sequence,
                header=self.header,
            )
            # Creating individual Series and Dataset instance and fill
            # with spectral data
            wavenumber_series = self._datamodel_lib.Series(
                data_array=spectrum_df["wavenumber"].to_numpy(), unit=u.cm ** (-1)
            )
            intensity_series = self._datamodel_lib.Series(
                data_array=spectrum_df["intensity"].to_numpy(),
                unit=u.dimensionless_unscaled,
            )
            dataset = self._datamodel_lib.Dataset(
                x_axis=wavenumber_series, y_axis=intensity_series
            )
            # Adding a Measurement instance to the Experiment
            datamodel_root_experiment.add_to_measurements(
                name=spectrum, measurement_data=dataset
            )
        datamodel_root.experiment.append(datamodel_root_experiment)
        self._datamodel = datamodel_root
        return self._datamodel

    def set_background(self, background_spectra: List):
        """
        Function takes a list names of measurements within the DataModel
        and sets the enumeration for the measurement_type. Measurements
        within the List are background the others are set to sample
        automatically.

        Args:
            background_spectra (List): List of names of background
            measurements within the DataModel.

        Returns:
            DataModel: DataModel with updated measurement_type for each
                measurement
        """
        # Initialize DataModel if not already initialized
        if self._datamodel == None:
            self._initialize_datamodel()

        measurements = self._datamodel.experiment[0].measurements  # type: ignore
        for spectrum in measurements:
            if spectrum.name in background_spectra:
                spectrum.measurement_type = "Background"
                self._define_background(spectrum)
            else:
                spectrum.measurement_type = "Sample"
        return self._datamodel

    def _define_background(self, measurement_object) -> pd.DataFrame:
        """
        Function sets the _background_df variable as a DataFrame with the
        measurement_data from the background measurement object.

        Args:
            measurement_object (Measurement): Measurement object containing
                the background measurement data

        Returns:
            background_df (pd.DataFrame): DataFrame with wavenumber and
                intensity values of the background measurement object.
        """
        background_df_data = {
            "wavenumber": measurement_object.measurement_data.x_axis.data_array,
            "intensity": measurement_object.measurement_data.y_axis.data_array,
        }
        self._background_df = pd.DataFrame(background_df_data)
        return self._background_df
