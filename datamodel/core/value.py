import sdRDM

from typing import Optional
from pydantic import Field
from sdRDM.base.utils import forge_signature, IDGenerator

from astropy.units import UnitBase


@forge_signature
class Value(sdRDM.DataModel):

    """Abstract Container for a single value-unit pair."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("valueINDEX"),
        xml="@id",
    )

    value: Optional[float] = Field(
        default=None,
        description="Value of the data point",
    )

    unit: Optional[UnitBase] = Field(
        default=None,
        description="Unit of the data point contained in `value`.",
    )
