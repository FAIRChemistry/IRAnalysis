import sdRDM

from typing import Dict, List, Optional
from pydantic import PrivateAttr, model_validator
from uuid import uuid4
from pydantic_xml import attr, element
from lxml.etree import _Element
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from sdRDM.base.datatypes import Unit
from sdRDM.tools.utils import elem2dict


@forge_signature
class Calculation(sdRDM.DataModel, search_mode="unordered"):
    """Contains the formula and it's parameters used for a calculation during the analysis."""

    id: Optional[str] = attr(
        name="id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
        xml="@id",
    )

    formula: str = element(
        description="Formula for the used calculation.",
        tag="formula",
        json_schema_extra=dict(),
    )

    parameters: List[float] = element(
        description=(
            "Parameters used for the given formula. Ordered chronologically as"
            " described in the formula definition."
        ),
        default_factory=ListPlus,
        tag="parameters",
        json_schema_extra=dict(multiple=True),
    )

    units: List[Unit] = element(
        description=(
            "Units of the values contained in `parameters`. Ordered chronologically as"
            " in the parameters list."
        ),
        default_factory=ListPlus,
        tag="units",
        json_schema_extra=dict(multiple=True),
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

    def add_to_units(self, unit_string: str):
        """
        This method adds an object of type 'Unit' to attribute units

        Args:
            unit_string (str): The string to be parsed into a Unit object
        """
        self.units.append(Unit.from_string(unit_string))
        return self.units[-1]
