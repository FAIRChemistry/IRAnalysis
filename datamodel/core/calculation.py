import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator

from astropy.units import UnitBase


@forge_signature
class Calculation(sdRDM.DataModel):

    """Contains the formula and it's parameters used for a calculation during the analysis."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("calculationINDEX"),
        xml="@id",
    )

    formula: str = Field(
        ...,
        description="Formula for the used calculation.",
    )

    parameters: List[float] = Field(
        description=(
            "Parameters used for the given formula. Ordered chronologically as"
            " described in the formula definition."
        ),
        default_factory=ListPlus,
        multiple=True,
    )

    units: List[UnitBase] = Field(
        description=(
            "Units of the values contained in `parameters`. Ordered chronologically as"
            " in the parameters list."
        ),
        default_factory=ListPlus,
        multiple=True,
    )
