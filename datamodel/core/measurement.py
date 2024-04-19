import sdRDM

from typing import Dict, Optional
from pydantic import PrivateAttr, model_validator
from uuid import uuid4
from pydantic_xml import attr, element
from lxml.etree import _Element
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from sdRDM.tools.utils import elem2dict
from .dataset import Dataset
from .value import Value
from .measurementtypes import MeasurementTypes


@forge_signature
class Measurement(sdRDM.DataModel, search_mode="unordered"):
    """Contains all measurements done for the experiment. E.g. sample, unloaded sample and background."""

    id: Optional[str] = attr(
        name="id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
        xml="@id",
    )

    name: str = element(
        description="Descriptive name for the single measurement.",
        tag="name",
        json_schema_extra=dict(),
    )

    geometry: Optional[str] = element(
        description="Spectrometer geometry used for the measurement",
        default=None,
        tag="geometry",
        json_schema_extra=dict(),
    )

    temperature: Optional[Value] = element(
        description="Temperature at which the measurement was performed.",
        default=None,
        tag="temperature",
        json_schema_extra=dict(),
    )

    pressure: Optional[Value] = element(
        description="Pressure at which the measurement was performed.",
        default=None,
        tag="pressure",
        json_schema_extra=dict(),
    )

    measurement_type: Optional[MeasurementTypes] = element(
        description="Type of measurement.",
        default=None,
        tag="measurement_type",
        json_schema_extra=dict(),
    )

    measurement_data: Optional[Dataset] = element(
        description="Series objects of the measured axes.",
        default_factory=Dataset,
        tag="measurement_data",
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
