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

from datamodel.core import measurement


class IRDataFiles:
    """
    The IRDataFiles class contails all spectra for a given experiment
    and the methods to assign them a role for later analysis.
    """

    def __init__(self, ir_file_directory: str, **kwargs):
        self.directory = ir_file_directory
        self.datamodel_directory = kwargs.get("datamodel_directory", "./")
        self.separator = kwargs.get("separator", ";")
        self.decimal_separator = kwargs.get("decimal", ",")
        self.file_extension = kwargs.get("extension", "csv")
        self._loaded_ir_files = []
        self._datamodel = DataModel
        self.datetime_created = str(datetime.now())
        self.experiment_name = kwargs.get("experiment_name", "UnspecifiedExperiment")

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

    def show_data(self, wavenumber_region=(1560, 1400), legend: bool=False):
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
            spectrum_df = pd.read_csv(file_location, header=None, 
                                      delimiter=self.separator, 
                                      decimal=self.decimal_separator)

            #truncating spectrum to desired region
            spectrum_df = spectrum_df[(spectrum_df[0] < wavenumber_region.max()) 
                                      & (spectrum_df[0] > wavenumber_region.min())]
            ax.plot(spectrum_df[0], spectrum_df[1], label=spectrum)
        plt.xlim(wavenumber_region)
        ax.set_xlabel("$\\nu$ / cm$^{-1}$")
        ax.set_ylabel("$A$ / a.u.")
        if legend:
            plt.legend(title="Filenames:", loc="upper left" , bbox_to_anchor=(-0.2,-0.2))
        plt.show()

    @property
    def datamodel (self):
        """Function to store raw measurement data from files as an IR 
        Measurement object.

        Returns:
            datamodel_root (DataModel): With added Measurement objects
        """
        #Loading of DataModel as specified in markdown
        os.chdir(self.datamodel_directory)
        datamodel_lib = DataModel.from_markdown("./specifications")
        #Creating an root instance of the DataModel
        datamodel_root = datamodel_lib.IRAnalysis(
            datetime_created = str(self.datetime_created),
            )
        #Creating an Experiment instance of the DataModel
        datamodel_root_experiment = datamodel_lib.Experiment(name=self.experiment_name)
        for spectrum in self.files:
            file_location = str(self.directory) + spectrum
            spectrum_df = pd.read_csv(file_location, header=None, 
                                      delimiter=self.separator, 
                                      decimal=self.decimal_separator)
            #Creating Dataset instance an fill with spectral data
            dataset = datamodel_lib.Dataset()
            dataset.x_axis.data_array = spectrum_df.to_numpy()[0:,0]
            dataset.y_axis.data_array = spectrum_df.to_numpy()[0:,1]
            #Adding a Measurement instance to the Experiment
            datamodel_root_experiment.add_to_measurements(name=spectrum,
                                                          measurement_data=dataset)
        datamodel_root.experiment.append(datamodel_root_experiment)
        self._datamodel = datamodel_root
        return self._datamodel
    
    @datamodel.setter
    def datamodel(self, datamodel):
        if isinstance(datamodel, DataModel):
            self._datamodel = datamodel