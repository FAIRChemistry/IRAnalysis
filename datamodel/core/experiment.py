import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator


from .dataset import Dataset
from .calculation import Calculation
from .analysis import Analysis
from .band import Band
from .measurementtypes import MeasurementTypes
from .series import Series
from .measurement import Measurement
from .value import Value
from .result import Result
from .samplepreparation import SamplePreparation


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
        temperature: Optional[Value] = None,
        pressure: Optional[Value] = None,
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
        background_reference: Optional[Measurement] = None,
        sample_reference: Optional[Measurement] = None,
        corrected_data: Optional[Dataset] = None,
        baseline: Optional[Series] = None,
        bands: List[Band] = ListPlus(),
        calculations: List[Calculation] = ListPlus(),
        measurement_results: List[Result] = ListPlus(),
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Analysis' to attribute analysis

        Args:
            id (str): Unique identifier of the 'Analysis' object. Defaults to 'None'.
            background_reference (): Reference to the IDs of background measurements used.. Defaults to None
            sample_reference (): Reference to the ID of the sample measurement.. Defaults to None
            corrected_data (): Dataset based on a measured sample and corrected with the background measurement and optionally baseline corrected.. Defaults to None
            baseline (): Dataset containing the baseline values. Calculation is based on the classification algorithm FastChrom (Johnsen, L., et al., Analyst. 2013, 138, 3502-3511.).. Defaults to None
            bands (): Bands assigned and quantified within the spectrum.. Defaults to ListPlus()
            calculations (): Calculations performed during the analysis.. Defaults to ListPlus()
            measurement_results (): List of final results calculated from one measurement.. Defaults to ListPlus()
        """

        params = {
            "background_reference": background_reference,
            "sample_reference": sample_reference,
            "corrected_data": corrected_data,
            "baseline": baseline,
            "bands": bands,
            "calculations": calculations,
            "measurement_results": measurement_results,
        }

        if id is not None:
            params["id"] = id

        self.analysis.append(Analysis(**params))

        return self.analysis[-1]
