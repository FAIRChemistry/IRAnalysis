import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
from astropy.units import UnitBase


@forge_signature
class Result(sdRDM.DataModel):
    """Final result obtained from the analysis."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("resultINDEX"),
        xml="@id",
    )

    name: str = Field(
        ...,
        description="Name of the calculated value",
    )

    values: List[float] = Field(
        description="Value(s) for the specified result.",
        default_factory=ListPlus,
        multiple=True,
    )

    units: List[UnitBase] = Field(
        description=(
            "Units of the values contained in `values`. Ordered chronologically as in"
            " the values list."
        ),
        default_factory=ListPlus,
        multiple=True,
    )
