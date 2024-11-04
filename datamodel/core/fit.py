from typing import Dict, List, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.datatypes import Unit
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict

from .value import Value


class Fit(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Contains the fitting function and the found optimal parameters."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    model: str = element(
        description="Description of the fitting model used (e.g. Gauss-Lorentz)",
        tag="model",
        json_schema_extra=dict(),
    )

    formula: Optional[str] = element(
        description=(
            "Implemented formula of the fitting model. Corresponds with the sequence of"
            " fitting parameters."
        ),
        default=None,
        tag="formula",
        json_schema_extra=dict(),
    )

    parameters: List[Value] = element(
        description=(
            "Optained optimal fitting parameters. Sequence according to formula."
        ),
        default_factory=ListPlus,
        tag="parameters",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    area: Optional[Value] = element(
        description="Total area of the fitted model curve.",
        default=None,
        tag="area",
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

    def add_to_parameters(
        self,
        value: float,
        unit: Unit,
        error: Optional[float] = None,
        error2: Optional[float] = None,
        id: Optional[str] = None,
        **kwargs,
    ) -> Value:
        """
        This method adds an object of type 'Value' to attribute parameters

        Args:
            id (str): Unique identifier of the 'Value' object. Defaults to 'None'.
            value (): Value of the data point.
            unit (): Unit of the data point contained in `value`..
            error (): Error of the value.. Defaults to None
            error2 (): If the error is not symetric in both directions, this value specifies the error into the other direction.. Defaults to None
        """

        params = {
            "value": value,
            "unit": unit,
            "error": error,
            "error2": error2,
        }

        if id is not None:
            params["id"] = id

        obj = Value(**params)

        self.parameters.append(obj)

        return self.parameters[-1]
