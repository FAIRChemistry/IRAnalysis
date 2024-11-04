"""
This module contains classes and functions to collect IR data files and
to assign them a role for later analysis.
"""

from types import NoneType
from anyio import value
from sdRDM import DataModel
from datamodel.core import IRAnalysis, Experiment, Series, Dataset, Parameters, Value
import os, glob
from datetime import datetime
from typing import List, Optional, Union
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from astropy import units as u


class IRDataFiles:
    """
    The IRDataFiles class contains all spectra for a given experiment
    and the methods to assign them a role for later analysis.
    """

    def __init__(self, **kwargs):
        self.contributors = kwargs.get("contributors", "")
        self.directory = kwargs.get("file_directory", "./")
        self.kwargs = kwargs
        self.datamodel_directory = kwargs.get("datamodel_directory", "./datamodel/core")
        self.detection = kwargs.get("detection", "absorbance")
        self.varied_parameter = kwargs.get("varied_parameter", "measurement_no")
        self.varied_parameter_values = kwargs.get("varied_parameter_values", [])
        self.separator = kwargs.get("separator", ";")
        self.header = kwargs.get("header", None)
        self.column_sequence = kwargs.get(
            "column_sequence", ["wavenumber", "intensity"]
        )
        self.decimal_separator = kwargs.get("decimal", ",")
        self.file_extension = kwargs.get("extension", "csv")
        self._loaded_ir_files = self._load_files()
        self.datetime_created = str(datetime.now())
        self.experiment_name = kwargs.get("experiment_name", "UnspecifiedExperiment")
        self._background_df = pd.DataFrame({"wavenumber": [], "intensity": []})
        self._datamodel = self._initialize_datamodel()

    @property
    def files(self) -> List[str]:
        """This function returns all files found in the specified
        directory with the given file extension.

        Returns:
            List[str]: List of data file names.
        """
        return self._loaded_ir_files

    @files.setter
    def files(self, user_ir_files: List[str]):
        self._loaded_ir_files = user_ir_files
        self._initialize_datamodel()
        return self._loaded_ir_files

    def _load_files(self):
        """Function to load all files from the specified directory and save them
        in the _loaded_ir_files attribute."""
        directory = os.path.abspath(self.directory) # Absolute path to the directory
        return glob.glob(f"{directory}/*.{self.file_extension}")

    def show_raw_data(self, wavenumber_region=None, legend: bool = False):
        """
        This function generates one plot with every measurement from the
        dataset.
        Args:
            wavenumber_region (tuple, optional): Desired wavenumber
                region to show. Defaults to (1560, 1400).
            legend (bool, optional): Wheter to show a legend containing
                the corresponding filenames. Default is False.
        """
    
        fig, ax = plt.subplots()
        # Iterating over all measurements in the DataModel
        for measurement_object in self.datamodel.experiment.measurements:
            wavenumber = measurement_object.measurement_data.x_axis.data_array
            intensity = measurement_object.measurement_data.y_axis.data_array
            spectrum_df = pd.DataFrame({"wavenumber": wavenumber, 
                                        "intensity": intensity})
            # truncating spectrum to desired region
            if not isinstance(wavenumber_region, NoneType):
                wavenumber_region = np.array(wavenumber_region)
                spectrum_df = spectrum_df[
                    (spectrum_df["wavenumber"] < wavenumber_region.max())
                    & (spectrum_df["wavenumber"] > wavenumber_region.min())
                ]
                plt.xlim(wavenumber_region)
            ax.plot(spectrum_df["wavenumber"], spectrum_df["intensity"], 
                    label=measurement_object.name)
        ax.set_xlabel("wavenumber / cm$^{-1}$")
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

        # Creating an root instance of the DataModel
        datamodel_root = IRAnalysis(
            datetime_created=str(self.datetime_created),
        )
        # Creating an Experiment instance of the DataModel
        datamodel_root_experiment = Experiment(name=self.experiment_name,
                                               varied_parameter=self.varied_parameter,
    
                                     )
        # Counter for the measurement number
        n = 0
        # Instead of providing data files, data can also be provided as a list of DataFrames
        for spectrum in self._loaded_ir_files:
            if isinstance(spectrum, pd.DataFrame):
                spectrum_df = spectrum
                name = str(n)
            else:
                file_location = spectrum.lower()
                spectrum_df = pd.read_csv(
                    file_location,
                    delimiter=self.separator,
                    decimal=self.decimal_separator,
                    names=self.column_sequence,
                    header=self.header,
                )
                name = file_location.split("\\")[-1].split(f".{self.file_extension}")[0]
            # Creating individual Series and Dataset instance and fill
            # with spectral data
            wavenumber_series = Series(
                data_array=spectrum_df["wavenumber"].to_numpy(), unit="1 / cm"
            )
            intensity_series = Series(
                data_array=spectrum_df["intensity"].to_numpy(),
                unit="dimensionless",
            )
            dataset = Dataset(x_axis=wavenumber_series, y_axis=intensity_series)
            
            # determining the varied parameter value for the measurement
            try:
                varied_parameter_value = self.varied_parameter_values[n]
            except:
                print("Not enough values for the varied parameter provided. Using measurement number.")
                varied_parameter_value = str(n)
            n += 1
            # Turning varied parameter value into an astropy Quantity
            varied_parameter_value = u.Quantity(varied_parameter_value)
            # Adding a Measurement instance to the Experiment
            datamodel_root_experiment.add_to_measurements(
                name=name, 
                measurement_data=dataset,
                varied_parameter_value=Value(value=varied_parameter_value.value, 
                                             unit=f"{varied_parameter_value.unit}"),
                detection=self.detection,
            )
        datamodel_root.experiment = datamodel_root_experiment
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
        
        # Lower casing all names in the list for campatibility
        background_spectra = [spectrum.lower() for spectrum in background_spectra]
        measurements = self._datamodel.experiment.measurements  # type: ignore
        for spectrum in measurements:
            if spectrum.name in background_spectra:
                spectrum.measurement_type = "background"
                self._define_background(spectrum)
            else:
                spectrum.measurement_type = "sample"

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
    
    def fill_static_parameters(self, parameters_dict: dict, measurement_no: Optional[int] = None):
        """Fills Parameters object in the DataModel with data
        provided in parameters_dict.

        Args:
            preparation_dict (dict): Dict with keys matching the available
            measurement_no (int): Index of the measurement object. If int value is given,
                parameters will be saved for the measurement instead of the whole experiment.
        """
        # all available Fields of Parameters except ID
        available = list(Parameters.model_fields.keys())[1:]
        sample_object = Parameters()
        for attribute in parameters_dict:
            if attribute in available:
                # Checking whether a Value object is expected for the given attribute
                if (
                    sample_object.__annotations__[attribute].__args__[0].__name__
                    == "Value"
                ):
                    quantity = u.Quantity(parameters_dict[attribute])
                    value_object = Value(value=quantity.value, unit=f"{quantity.unit}")
                    setattr(sample_object, attribute, value_object)
                else:
                    setattr(sample_object, attribute, parameters_dict[attribute])
            else:
                print(f"{attribute} is an unknown field.")
        if isinstance(measurement_no, int):
            self._datamodel.experiment.measurements[measurement_no].static_parameters = sample_object
        else:
            #if no measurement_no is given, the parameters are saved for the experiment instead
            self._datamodel.experiment.static_parameters = sample_object