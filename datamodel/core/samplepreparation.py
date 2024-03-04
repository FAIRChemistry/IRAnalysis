import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator


from .value import Value


@forge_signature
class SamplePreparation(sdRDM.DataModel):

    """This keeps track of important synthesis parameters relevant for later analysis."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("samplepreparationINDEX"),
        xml="@id",
    )

    mass: Value = Field(
        description="Mass of the IR sample",
        default=Value(),
    )

    literatureReference: List[str] = Field(
        description="Points to literature references used for the sample preparation",
        default_factory=ListPlus,
        multiple=True,
    )

    composition: Optional[str] = Field(
        default=None,
        description="Relative amount of components used in preparation",
    )

    probeMolecule: Optional[str] = Field(
        default=None,
        description="Probe molecule used",
    )

    samplePreperation: Optional[str] = Field(
        default=None,
        description="Addidional description of preperation parameters.",
    )
