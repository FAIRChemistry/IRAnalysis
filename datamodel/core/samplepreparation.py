import sdRDM

from typing import Dict, List, Optional
from pydantic import PrivateAttr, model_validator
from uuid import uuid4
from pydantic_xml import attr, element
from lxml.etree import _Element
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from sdRDM.tools.utils import elem2dict
from .value import Value


@forge_signature
class SamplePreparation(sdRDM.DataModel, search_mode="unordered"):
    """This keeps track of important synthesis parameters relevant for later analysis."""

    id: Optional[str] = attr(
        name="id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
        xml="@id",
    )

    mass: Optional[Value] = element(
        description="Mass of the IR sample",
        default=None,
        tag="mass",
        json_schema_extra=dict(),
    )

    sample_area: Optional[Value] = element(
        description="Area of the IR sample",
        default=None,
        tag="sample_area",
        json_schema_extra=dict(),
    )

    literatureReference: List[str] = element(
        description="Points to literature references used for the sample preparation",
        default_factory=ListPlus,
        tag="literatureReference",
        json_schema_extra=dict(multiple=True),
    )

    composition: Optional[str] = element(
        description="Relative amount of components used in preparation",
        default=None,
        tag="composition",
        json_schema_extra=dict(),
    )

    probeMolecule: Optional[str] = element(
        description="Probe molecule used",
        default=None,
        tag="probeMolecule",
        json_schema_extra=dict(),
    )

    samplePreperation: Optional[str] = element(
        description="Addidional description of preperation parameters.",
        default=None,
        tag="samplePreperation",
        json_schema_extra=dict(),
    )
    _raw_xml_data: Dict = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def _parse_raw_xml_data(self):
        for attr, value in self:
            if isinstance(value, (ListPlus, list)) and all(
                (isinstance(i, _Element) for i in value)
            ):
                self._raw_xml_data[attr] = [elem2dict(i) for i in value]
            elif isinstance(value, _Element):
                self._raw_xml_data[attr] = elem2dict(value)
        return self
