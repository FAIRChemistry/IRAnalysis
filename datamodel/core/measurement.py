import sdRDM

from typing import Optional
from pydantic import Field
from sdRDM.base.utils import forge_signature, IDGenerator


from .measurementtypes import MeasurementTypes
from .dataset import Dataset


@forge_signature
class Measurement(sdRDM.DataModel):

    """Contains all measurements done for the experiment. E.g. sample, unloaded sample and background.
    """

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("measurementINDEX"),
        xml="@id",
    )

    name: str = Field(
        ...,
        description="Descriptive name for the single measurement.",
    )

    geometry: Optional[str] = Field(
        default=None,
        description="Spectrometer geometry used for the measurement",
    )

    temperature: Optional[float] = Field(
        default=None,
        description="Temperature at which the measurement was performed.",
    )

    pressure: Optional[float] = Field(
        default=None,
        description="Pressure at which the measurement was performed.",
    )

    measurement_type: Optional[MeasurementTypes] = Field(
        default=None,
        description="Type of measurement.",
    )

    measurement_data: Optional[Dataset] = Field(
        default=Dataset(),
        description="Series objects of the measured axes.",
    )
