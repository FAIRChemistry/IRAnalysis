import sdRDM

from typing import Optional
from pydantic import Field
from sdRDM.base.utils import forge_signature, IDGenerator

from datetime import datetime as Datetime

from .series import Series


@forge_signature
class Dataset(sdRDM.DataModel):

    """Container for a single set of data."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("datasetINDEX"),
        xml="@id",
    )

    timestamp: Optional[Datetime] = Field(
        default=None,
        description="Date and time the data was recorded",
    )

    x_axis: Optional[Series] = Field(
        default=Series(),
        description="The object containing data points and unit of the x-axis.",
    )

    y_axis: Optional[Series] = Field(
        default=Series(),
        description="The object containing data points and unit of the y-axis.",
    )
