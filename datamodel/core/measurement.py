from typing import Dict, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict

from .dataset import Dataset
from .detection import Detection
from .measurementtypes import MeasurementTypes
from .parameters import Parameters
from .value import Value


class Measurement(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Contains one measurement done for the experiment. E.g. sample, unloaded sample and background."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    name: str = element(
        description="Descriptive name for the single measurement.",
        tag="name",
        json_schema_extra=dict(),
    )

    varied_parameter_value: Optional[Value] = element(
        description="Value of the varied parameter for the given measurement.",
        default=None,
        tag="varied_parameter_value",
        json_schema_extra=dict(),
    )

    measurement_type: Optional[MeasurementTypes] = element(
        description="Type of measurement.",
        default=None,
        tag="measurement_type",
        json_schema_extra=dict(),
    )

    detection: Detection = element(
        description="Method/Geometry of detection.",
        tag="detection",
        json_schema_extra=dict(),
    )

    measurement_data: Optional[Dataset] = element(
        description="Series objects of the measured axes.",
        default_factory=Dataset,
        tag="measurement_data",
        json_schema_extra=dict(),
    )

    static_parameters: Optional[Parameters] = element(
        description=(
            "Parameter object with attributes that do not change during the experiment"
            " or measurement series."
        ),
        default_factory=Parameters,
        tag="static_parameters",
        json_schema_extra=dict(),
    )

    _raw_xml_data: Dict = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def _parse_raw_xml_data(self):
        for attr, value in self:
            if isinstance(value, (ListPlus, list)) and all(
                isinstance(i, _Element) for i in value
            ):
                self._raw_xml_data[attr] = [elem2dict(i) for i in value]
            elif isinstance(value, _Element):
                self._raw_xml_data[attr] = elem2dict(value)

        return self
