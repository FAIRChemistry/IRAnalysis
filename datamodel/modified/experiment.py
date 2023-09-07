import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator


from datamodel.core.correctedspectrum import CorrectedSpectrum
from datamodel.core.dataset import Dataset
from datamodel.core.measurementtypes import MeasurementTypes
from datamodel.core.measurement import Measurement


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

    measurements: List[Measurement] = Field(
        description="Each single measurement is contained in one `measurement` object.",
        default_factory=ListPlus,
        multiple=True,
    )

    corrected_spectra: List[CorrectedSpectrum] = Field(
        description="List of background-corrected spectra",
        default_factory=ListPlus,
        multiple=True,
    )

    def add_to_measurements(
        self,
        name: Optional[str] = None,
        measurement_type: Optional[MeasurementTypes] = None,
        measurement_data: Optional[Dataset] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Measurement' to attribute measurements

        Args:
            id (str): Unique identifier of the 'Measurement' object. Defaults to 'None'.
            name (): Descriptive name for the single measurement.. Defaults to None
            measurement_type (): Type of measurement.. Defaults to None
            measurement_data (): Series objects of the measured axes.. Defaults to None
        """

        params = {
            "name": name,
            "measurement_type": measurement_type,
            "measurement_data": measurement_data,
        }

        if id is not None:
            params["id"] = id

        self.measurements.append(Measurement(**params))

        return self.measurements[-1]

    def add_to_corrected_spectra(
        self,
        name: Optional[str] = None,
        background_references: List[Measurement] = ListPlus(),
        sample_reference: Optional[Measurement] = None,
        corrected_data: Optional[Dataset] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'CorrectedSpectrum' to attribute corrected_spectra

        Args:
            id (str): Unique identifier of the 'CorrectedSpectrum' object. Defaults to 'None'.
            name (): Descriptive name for the corrected spectrum.. Defaults to None
            background_references (): References to the IDs of background measurements used.. Defaults to ListPlus()
            sample_reference (): Reference to the ID of the sample measurement.. Defaults to None
            corrected_data (): Dataset based on a measured sample and corrected with one or more backgrounds.. Defaults to None
        """

        params = {
            "name": name,
            "background_references": background_references,
            "sample_reference": sample_reference,
            "corrected_data": corrected_data,
        }

        if id is not None:
            params["id"] = id

        self.corrected_spectra.append(CorrectedSpectrum(**params))

        return self.corrected_spectra[-1]

    def this_is_my_custom_method(self):
        ...
