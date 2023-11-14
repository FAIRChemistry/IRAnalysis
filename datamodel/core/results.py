import sdRDM

from typing import Optional
from pydantic import Field
from sdRDM.base.utils import forge_signature, IDGenerator


from .series import Series


@forge_signature
class Results(sdRDM.DataModel):

    """Resulting values calculated from the corrected spectrum"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("resultsINDEX"),
        xml="@id",
    )

    fitting_parameters: Optional[Series] = Field(
        default=Series(),
        description="Object containing fitting parameters for all curves",
    )

    n_active_sites: Optional[Series] = Field(
        default=Series(),
        description=(
            "Object containing number of Lewis, Bronstedt and mixed active sites"
        ),
    )
