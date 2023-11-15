import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
from astropy.units import UnitBase


@forge_signature
class Series(sdRDM.DataModel):
    """Abstract Container for a measured Series (i.e. one axis)."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("seriesINDEX"),
        xml="@id",
    )

    data_array: List[float] = Field(
        description="List of data points of one measured Series.",
        default_factory=ListPlus,
        multiple=True,
    )

    unit: Optional[UnitBase] = Field(
        default=None,
        description="Unit of the data points contained in `data_array`.",
    )
