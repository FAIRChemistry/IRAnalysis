import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
from .measurement import Measurement
from .analysis import Analysis
from .samplepreparation import SamplePreparation
from .result import Result
from .measurementtypes import MeasurementTypes
from .calculation import Calculation
from .dataset import Dataset


@forge_signature
class Experiment(sdRDM.DataModel):
    """This could be a very basic object that keeps track of the entire experiment."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("experimentINDEX"),
        xml="@id",
    )

    name: str = Field(
        ...,
        description="A descriptive name for the overarching experiment.",
    )

    sample_preparation: Optional[SamplePreparation] = Field(
        default=None,
        description="Synthesis and preparation parameters",
    )

    measurements: List[Measurement] = Field(
        description="Each single measurement is contained in one `measurement` object.",
        default_factory=ListPlus,
        multiple=True,
    )

    analysis: List[Analysis] = Field(
        description="Analysis procedure and parameters.",
        default_factory=ListPlus,
        multiple=True,
    )

    results: Optional[Result] = Field(
        default=None,
        description=(
            "List of final results calculated from measurements done for the"
            " experiment."
        ),
    )

    def add_to_measurements(
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
        This method adds an object of type 'Measurement' to attribute measurements

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
        self.measurements.append(Measurement(**params))
        return self.measurements[-1]

    def add_to_analysis(
        self,
        background_references: List[Measurement] = ListPlus(),
        sample_reference: Optional[Measurement] = None,
        corrected_data: Optional[Dataset] = None,
        calculations: List[Calculation] = ListPlus(),
        measurement_results: List[Result] = ListPlus(),
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Analysis' to attribute analysis

        Args:
            id (str): Unique identifier of the 'Analysis' object. Defaults to 'None'.
            background_references (): References to the IDs of background measurements used.. Defaults to ListPlus()
            sample_reference (): Reference to the ID of the sample measurement.. Defaults to None
            corrected_data (): Dataset based on a measured sample and corrected with one or more backgrounds.. Defaults to None
            calculations (): Calculations performed during the analysis.. Defaults to ListPlus()
            measurement_results (): List of final results calculated from one measurement.. Defaults to ListPlus()
        """
        params = {
            "background_references": background_references,
            "sample_reference": sample_reference,
            "corrected_data": corrected_data,
            "calculations": calculations,
            "measurement_results": measurement_results,
        }
        if id is not None:
            params["id"] = id
        self.analysis.append(Analysis(**params))
        return self.analysis[-1]
