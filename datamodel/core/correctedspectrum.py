import sdRDM

from typing import Optional, Union, List
from pydantic import Field, validator
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator


from .dataset import Dataset
from .measurement import Measurement
from .measurementtypes import MeasurementTypes


@forge_signature
class CorrectedSpectrum(sdRDM.DataModel):

    """Lorem ipsum."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("correctedspectrumINDEX"),
        xml="@id",
    )

    name: Optional[str] = Field(
        default=None,
        description="Descriptive name for the corrected spectrum.",
    )

    background_references: List[Union[Measurement, str]] = Field(
        reference="Measurement.id",
        description="References to the IDs of background measurements used.",
        default_factory=ListPlus,
        multiple=True,
    )

    sample_reference: Union[Measurement, str, None] = Field(
        default=Measurement(),
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

    def add_to_background_references(
        self,
        name: Optional[str] = None,
        measurement_type: Optional[MeasurementTypes] = None,
        measurement_data: Optional[Dataset] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Measurement' to attribute background_references

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

        self.background_references.append(Measurement(**params))

        return self.background_references[-1]

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
