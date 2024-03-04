import sdRDM

from typing import Optional
from pydantic import Field
from sdRDM.base.utils import forge_signature, IDGenerator


from .fit import Fit
from .value import Value


@forge_signature
class Band(sdRDM.DataModel):

    """Contains parameters of a band analyzed during the analysis."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("bandINDEX"),
        xml="@id",
    )

    assignment: Optional[str] = Field(
        default=None,
        description="Assignment of the band",
    )

    fit: Optional[Fit] = Field(
        default=Fit(),
        description="Calculated fit for the band.",
    )

    location: Optional[Value] = Field(
        default=Value(),
        description="Location of the band maximum.",
    )

    start: Optional[Value] = Field(
        default=Value(),
        description="First data point attributed to the band.",
    )

    end: Optional[Value] = Field(
        default=Value(),
        description="Last data point attributed to the band.",
    )
