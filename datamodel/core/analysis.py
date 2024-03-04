import sdRDM

from typing import Optional, Union, List
from pydantic import Field, validator
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator

from astropy.units import UnitBase

from .dataset import Dataset
from .calculation import Calculation
from .band import Band
from .fit import Fit
from .series import Series
from .measurement import Measurement
from .value import Value
from .result import Result


@forge_signature
class Analysis(sdRDM.DataModel):

    """Contains all steps and parameters used to manipulate data and to calculate results from one sample measurement."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("analysisINDEX"),
        xml="@id",
    )

    background_reference: Union[Measurement, str, None] = Field(
        default=None,
        reference="Measurement.id",
        description="Reference to the IDs of background measurements used.",
    )

    sample_reference: Union[Measurement, str, None] = Field(
        default=None,
        reference="Measurement.id",
        description="Reference to the ID of the sample measurement.",
    )

    corrected_data: Optional[Dataset] = Field(
        default=Dataset(),
        description=(
            "Dataset based on a measured sample and corrected with the background"
            " measurement and optionally baseline corrected."
        ),
    )

    baseline: Optional[Series] = Field(
        default=Series(),
        description=(
            "Dataset containing the baseline values. Calculation is based on the"
            " classification algorithm FastChrom (Johnsen, L., et al., Analyst. 2013,"
            " 138, 3502-3511.)."
        ),
    )

    bands: List[Band] = Field(
        description="Bands assigned and quantified within the spectrum.",
        default_factory=ListPlus,
        multiple=True,
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

    def add_to_bands(
        self,
        assignment: Optional[str] = None,
        fit: Optional[Fit] = None,
        location: Optional[Value] = None,
        start: Optional[Value] = None,
        end: Optional[Value] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Band' to attribute bands

        Args:
            id (str): Unique identifier of the 'Band' object. Defaults to 'None'.
            assignment (): Assignment of the band. Defaults to None
            fit (): Calculated fit for the band.. Defaults to None
            location (): Location of the band maximum.. Defaults to None
            start (): First data point attributed to the band.. Defaults to None
            end (): Last data point attributed to the band.. Defaults to None
        """

        params = {
            "assignment": assignment,
            "fit": fit,
            "location": location,
            "start": start,
            "end": end,
        }

        if id is not None:
            params["id"] = id

        self.bands.append(Band(**params))

        return self.bands[-1]

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

        params = {
            "formula": formula,
            "parameters": parameters,
            "units": units,
        }

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

        params = {
            "name": name,
            "values": values,
            "units": units,
        }

        if id is not None:
            params["id"] = id

        self.measurement_results.append(Result(**params))

        return self.measurement_results[-1]

    @validator("background_reference")
    def get_background_reference_reference(cls, value):
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
