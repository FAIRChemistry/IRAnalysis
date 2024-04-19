import sdRDM

from typing import Dict, Optional
from pydantic import PrivateAttr, model_validator
from uuid import uuid4
from pydantic_xml import attr, element
from lxml.etree import _Element
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from sdRDM.tools.utils import elem2dict
from .value import Value
from .fit import Fit


@forge_signature
class Band(sdRDM.DataModel, search_mode="unordered"):
    """Contains parameters of a band analyzed during the analysis."""

    id: Optional[str] = attr(
        name="id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
        xml="@id",
    )

    assignment: Optional[str] = element(
        description="Assignment of the band",
        default=None,
        tag="assignment",
        json_schema_extra=dict(),
    )

    fit: Optional[Fit] = element(
        description="Calculated fit for the band.",
        default_factory=Fit,
        tag="fit",
        json_schema_extra=dict(),
    )

    location: Optional[Value] = element(
        description="Location of the band maximum.",
        default=None,
        tag="location",
        json_schema_extra=dict(),
    )

    start: Optional[Value] = element(
        description="First data point attributed to the band.",
        default=None,
        tag="start",
        json_schema_extra=dict(),
    )

    end: Optional[Value] = element(
        description="Last data point attributed to the band.",
        default=None,
        tag="end",
        json_schema_extra=dict(),
    )

    extinction_coefficient: Optional[Value] = element(
        description="Molar extinction coefficient of the band.",
        default=None,
        tag="extinction_coefficient",
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