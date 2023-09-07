import sdRDM

from typing import Optional
from pydantic import Field
from sdRDM.base.utils import forge_signature, IDGenerator


from .dataset import Dataset
from .measurementtypes import MeasurementTypes


@forge_signature
class Measurement(sdRDM.DataModel):

    """Wow. Such docstring."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("measurementINDEX"),
        xml="@id",
    )

    name: Optional[str] = Field(
        default=None,
        description="Descriptive name for the single measurement.",
    )

    measurement_type: Optional[MeasurementTypes] = Field(
        default=None,
        description="Type of measurement.",
    )

    measurement_data: Optional[Dataset] = Field(
        default=Dataset(),
        description="Series objects of the measured axes.",
    )
