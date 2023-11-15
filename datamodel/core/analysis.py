import sdRDM

from typing import Optional, Union, List
from pydantic import Field, validator
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
from astropy.units import UnitBase
from .measurement import Measurement
from .result import Result
from .measurementtypes import MeasurementTypes
from .calculation import Calculation
from .dataset import Dataset


@forge_signature
class Analysis(sdRDM.DataModel):
    """Contains all steps and parameters used to manipulate data and to calculate results from one sample measurement.
    """

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("analysisINDEX"),
        xml="@id",
    )

    background_references: List[Union[Measurement, str]] = Field(
        reference="Measurement.id",
        description="References to the IDs of background measurements used.",
        default_factory=ListPlus,
        multiple=True,
    )

    sample_reference: Union[Measurement, str, None] = Field(
        default=None,
        reference="Measurement.id",
        description="Reference to the ID of the sample measurement.",
    )

    corrected_data: Optional[Dataset] = Field(
        default=Dataset(),
        description=(
            "Dataset based on a measured sample and corrected with one or more"
            " backgrounds."
        ),
    )

    calculations: List[Calculation] = Field(
        description="Calculations performed during the analysis.",
        default_factory=ListPlus,
        multiple=True,
    )

    measurement_results: List[Result] = Field(
        description="List of final results calculated from one measurement.",
        default_factory=ListPlus,
        multiple=True,
    )

    def add_to_background_references(
        self,
        name: str,
        geometry: Optional[str] = None,
        temperature: Optional[float] = None,
        pressure: Optional[float] = None,
        measurement_type: Optional[MeasurementTypes] = None,
        measurement_data: Optional[Dataset] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Measurement' to attribute background_references

        Args:
            id (str): Unique identifier of the 'Measurement' object. Defaults to 'None'.
            name (): Descriptive name for the single measurement..
            geometry (): Spectrometer geometry used for the measurement. Defaults to None
            temperature (): Temperature at which the measurement was performed.. Defaults to None
            pressure (): Pressure at which the measurement was performed.. Defaults to None
            measurement_type (): Type of measurement.. Defaults to None
            measurement_data (): Series objects of the measured axes.. Defaults to None
        """
        params = {
            "name": name,
            "geometry": geometry,
            "temperature": temperature,
            "pressure": pressure,
            "measurement_type": measurement_type,
            "measurement_data": measurement_data,
        }
        if id is not None:
            params["id"] = id
        self.background_references.append(Measurement(**params))
        return self.background_references[-1]

    def add_to_calculations(
        self,
        formula: str,
        parameters: List[float] = ListPlus(),
        units: List[UnitBase] = ListPlus(),
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Calculation' to attribute calculations

        Args:
            id (str): Unique identifier of the 'Calculation' object. Defaults to 'None'.
            formula (): Formula for the used calculation..
            parameters (): Parameters used for the given formula. Ordered chronologically as described in the formula definition.. Defaults to ListPlus()
            units (): Units of the values contained in `parameters`. Ordered chronologically as in the parameters list.. Defaults to ListPlus()
        """
        params = {"formula": formula, "parameters": parameters, "units": units}
        if id is not None:
            params["id"] = id
        self.calculations.append(Calculation(**params))
        return self.calculations[-1]

    def add_to_measurement_results(
        self,
        name: str,
        values: List[float] = ListPlus(),
        units: List[UnitBase] = ListPlus(),
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Result' to attribute measurement_results

        Args:
            id (str): Unique identifier of the 'Result' object. Defaults to 'None'.
            name (): Name of the calculated value.
            values (): Value(s) for the specified result.. Defaults to ListPlus()
            units (): Units of the values contained in `values`. Ordered chronologically as in the values list.. Defaults to ListPlus()
        """
        params = {"name": name, "values": values, "units": units}
        if id is not None:
            params["id"] = id
        self.measurement_results.append(Result(**params))
        return self.measurement_results[-1]

    @validator("background_references")
    def get_background_references_reference(cls, value):
        """Extracts the ID from a given object to create a reference"""
        from .measurement import Measurement

        if isinstance(value, Measurement):
            return value.id
        elif isinstance(value, str):
            return value
        elif value is None:
            return value
        else:
            raise TypeError(
                f"Expected types [Measurement, str] got '{type(value).__name__}'"
                " instead."
            )

    @validator("sample_reference")
    def get_sample_reference_reference(cls, value):
        """Extracts the ID from a given object to create a reference"""
        from .measurement import Measurement

        if isinstance(value, Measurement):
            return value.id
        elif isinstance(value, str):
            return value
        elif value is None:
            return value
        else:
            raise TypeError(
                f"Expected types [Measurement, str] got '{type(value).__name__}'"
                " instead."
            )
