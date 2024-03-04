import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator

from astropy.units import UnitBase

from .value import Value


@forge_signature
class Fit(sdRDM.DataModel):

    """Contains the fitting function and the found optimal parameters."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("fitINDEX"),
        xml="@id",
    )

    model: Optional[str] = Field(
        default=None,
        description="Description of the fitting model used (e.g. Gauss-Lorentz)",
    )

    formula: Optional[str] = Field(
        default=None,
        description=(
            "Implemented formula of the fitting model. Corresponds with the sequence of"
            " fitting parameters."
        ),
    )

    parameters: List[Value] = Field(
        description=(
            "Optained optimal fitting parameters. Sequence according to formula."
        ),
        default_factory=ListPlus,
        multiple=True,
    )

    area: Optional[Value] = Field(
        default=Value(),
        description="Total area of the fitted model curve.",
    )

    def add_to_parameters(
        self,
        value: Optional[float] = None,
        unit: Optional[UnitBase] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Value' to attribute parameters

        Args:
            id (str): Unique identifier of the 'Value' object. Defaults to 'None'.
            value (): Value of the data point. Defaults to None
            unit (): Unit of the data point contained in `value`.. Defaults to None
        """

        params = {
            "value": value,
            "unit": unit,
        }

        if id is not None:
            params["id"] = id

        self.parameters.append(Value(**params))

        return self.parameters[-1]
