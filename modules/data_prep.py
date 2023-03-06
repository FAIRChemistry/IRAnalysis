# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 15:49:35 2022

@author: Selina Itzigehl
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import pandas as pd
from pathlib import Path
from typing import List, Optional, Union


class IRDataHandler:
    """
    Preparation of pyridine absorption IR data for further evaluation.
    Extract, correct and save data as '.csv'
    """

    def __init__(
        self,
        path_to_directory: Optional[Union[str, bytes, os.PathLike]],
        folder: str,
        decimal: str,
    ) -> None:
        path = list(Path(path_to_directory).glob("*.csv"))
        self.path = path_to_directory
        self.folder = folder
        self.input_files = {file.stem: file for file in path if file.is_file()}
        self.bckgrnd_file = None
        self.sample_files = []
        self.sample_data_corr = []
        self.decimal = decimal

        if not self.decimal in (".", ","):
            raise ValueError(
                f"Decimal seperator '.' or ',' expected, got {self.decimal}"
            )

    def __repr__(self):
        return "IRDataHandler"

    def available_files(self) -> List[str]:
        """
        Gives list of available files for processing

        Returns:
            List[str]: list of files
        """
        return {count: value for count, value in enumerate(self.input_files)}

    def extract_background_data(self) -> pd.DataFrame:
        """
        Finds background data file and extracts data to pd.DataFrame

        Returns:
            pd.DataFrame: background data, 'wavenumber', 'absorbance'
        """
        for file in self.input_files:
            if not file.endswith("300min-450C"):
                pass
            else:
                self.bckgrnd_file = pd.read_csv(
                    self.path / (file + ".csv"),
                    delimiter=";",
                    usecols=[0, 1],
                    names=["wavenumber", "absorbance"],
                    header=None,
                    engine="python",
                    decimal=self.decimal,
                )

                if self.decimal == ".":
                    pass
                else:
                    self.bckgrnd_file["wavenumber"] = (
                        self.bckgrnd_file["wavenumber"]
                        .str.replace(",", ".")
                        .astype(float)
                    )
                    self.bckgrnd_file["absorbance"] = (
                        self.bckgrnd_file["absorbance"]
                        .str.replace(",", ".")
                        .astype(float)
                    )
                self.bckgrnd_file["absorbance"] -= self.bckgrnd_file[
                    "absorbance"
                ][1402]
        return self.bckgrnd_file

    def extract_sample_data(self) -> list[pd.DataFrame]:
        """
        extracts csv-files to pd.DataFrame

        Returns:
            pd.DataFrame: measurement data,'wavenumber', 'absorbance'
        """
        for file in self.input_files:
            if file.endswith("hydrated"):
                pass
            else:
                sample_file = pd.read_table(
                    self.path / (file + ".csv"),
                    delimiter=";",
                    usecols=[0, 1],
                    names=["wavenumber", "absorbance"],
                    header=None,
                    engine="python",
                    decimal=self.decimal,
                )
                if self.decimal == ".":
                    pass
                else:
                    sample_file["wavenumber"] = (
                        sample_file["wavenumber"]
                        .str.replace(",", ".")
                        .astype(float)
                    )
                    sample_file["absorbance"] = (
                        sample_file["absorbance"]
                        .str.replace(",", ".")
                        .astype(float)
                    )
                sample_file["absorbance"] -= sample_file["absorbance"][1402]
                self.sample_files.append(sample_file)
        return self.sample_files

    def get_data(
        self, list_of_df: list[pd.DataFrame] = None
    ) -> list[pd.DataFrame]:
        """
        Corrects raw data by background correction and truncated data to
        area of interest

        Args:
            list_of_df (list[pd.DataFrame], optional): list of
            'sample_files' containing data tobe corrected.
            Defaults to None.

        Returns:
            list[pd.DataFrame]: list of corrected sample files
        """
        self.extract_sample_data()
        self.extract_background_data()

        if list_of_df is None:
            list_of_df = self.sample_files

        bckgrnd_data = self.bckgrnd_file.truncate(1246, 1580)

        for data_set in list_of_df:
            sample_data = data_set.truncate(1246, 1580)

            x_array = sample_data["wavenumber"]
            y_raw = sample_data["absorbance"] - bckgrnd_data["absorbance"]
            y_array = y_raw + abs(y_raw[1505])

            data = {
                "wavenumber": x_array,
                "absorbance": y_array,
                "raw_abs": y_raw,
            }
            sample_data_corr = pd.DataFrame(data=data)

            self.sample_data_corr.append(sample_data_corr)
        return self.sample_data_corr

    def get_control_plot(self, index):
        """
        Draw plot of raw and corrected data to check for comparison.

        Args:
            index (int): file (from 'available_files') which is to be
            plotted
        """
        self.get_data()

        plt.plot(
            self.sample_data_corr[index]["wavenumber"].tolist(),
            self.sample_data_corr[index]["raw_abs"].tolist(),
            color="black",
            label="raw",
        )
        plt.plot(
            self.sample_data_corr[index]["wavenumber"].tolist(),
            self.sample_data_corr[index]["absorbance"].tolist(),
            color="red",
            label="corrected",
        )
        plt.axhline(y=0, color="grey", linestyle=":")
        plt.xlim(1560, 1400)
        plt.xlabel("$\\nu$ / cm$^{-1}$")
        plt.ylabel("$A$ / a.u.")
        plt.legend()
        plt.show()

    def get_plot(self, val1: int = 50, val2: int = 53):
        """
        Draw plot of all measurement files in one graph.

        Args:
            val1 (int, optional): Curve name from file name, first character. Defaults to 50.
            val2 (int, optional): Curve name from file name, last character. Defaults to 53.
        """
        self.get_data()

        cmap = mpl.cm.nipy_spectral.reversed()
        n_meas = len(self.sample_data_corr)

        fig, ax = plt.subplots()
        ax.set_xlim(1560, 1400)
        ax.set_xlabel("$\\nu$ / cm$^{-1}$")
        ax.set_ylabel("$A$ / a.u.")

        for index, measurement in enumerate(self.sample_data_corr):
            if not index == 0:
                name = f"{list(self.input_files)[index][val1:val2]} °C"
                print(f"Adding measurement {name} to figure.")

                ax.plot(
                    self.sample_data_corr[index]["wavenumber"].tolist(),
                    self.sample_data_corr[index]["absorbance"].tolist(),
                    color=cmap(index / float(n_meas)),
                    label=name,
                )
            else:
                pass
        (
            handles,
            labels,
        ) = plt.gca().get_legend_handles_labels()
        order = [4, 5, 6, 0, 1, 2, 3]

        plt.legend(
            [handles[index] for index in order],
            [labels[index] for index in order],
            frameon=False,
        )
        plt.savefig(self.folder + ".png", dpi=400)
        plt.show()

    def save_data_to_csv(self):
        """
        Turn corrected data for analysis into a pd.DataFrame and export
        as '.csv'
        """
        self.get_data()

        for index, dataframe in enumerate(self.sample_data_corr):
            file_name = list(self.input_files)[index]
            dataframe.to_csv(file_name + "_corr.csv")
        self.bckgrnd_file.to_csv(list(self.input_files)[-1] + "_corr.csv")


if __name__ == "__main__":
    cwd = Path.cwd()
    folder = "TO_P84-RT_1zu5"
    test = IRDataHandler(
        path_to_directory=cwd / folder, folder=folder, decimal=","
    )

    print(test.extract_background_data())
    print(type(test.extract_background_data()))
    # print(test.get_plot(val1=42, val2=45))
