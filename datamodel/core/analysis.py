from typing import Dict, List, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict

from .band import Band
from .dataset import Dataset
from .fit import Fit
from .result import Result
from .series import Series
from .value import Value


class Analysis(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Contains all steps and parameters used to manipulate data and to calculate results from one sample measurement."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    background_reference: Optional[str] = element(
        description="Reference to the IDs of background measurements used.",
        default=None,
        tag="background_reference",
        json_schema_extra=dict(),
    )

    sample_reference: str = element(
        description="Reference to the ID of the sample measurement.",
        tag="sample_reference",
        json_schema_extra=dict(),
    )

    corrected_data: Optional[Dataset] = element(
        description=(
            "Dataset based on a measured sample and corrected with the background"
            " measurement and optionally baseline corrected."
        ),
        default_factory=Dataset,
        tag="corrected_data",
        json_schema_extra=dict(),
    )

    baseline: Optional[Series] = element(
        description=(
            "Dataset containing the baseline values. Calculation is based on the"
            " classification algorithm FastChrom (Johnsen, L., et al., Analyst. 2013,"
            " 138, 3502-3511.)."
        ),
        default_factory=Series,
        tag="baseline",
        json_schema_extra=dict(),
    )

    bands: List[Band] = element(
        description="Bands assigned and quantified within the spectrum.",
        default_factory=ListPlus,
        tag="bands",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    measurement_results: List[Result] = element(
        description="List of final results calculated from one measurement.",
        default_factory=ListPlus,
        tag="measurement_results",
        json_schema_extra=dict(
            multiple=True,
        ),
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

    def add_to_bands(
        self,
        assignment: Optional[str] = None,
        fit: Optional[Fit] = None,
        location: Optional[Value] = None,
        start: Optional[Value] = None,
        end: Optional[Value] = None,
        extinction_coefficient: Optional[Value] = None,
        id: Optional[str] = None,
        **kwargs,
    ) -> Band:
        """
        This method adds an object of type 'Band' to attribute bands

        Args:
            id (str): Unique identifier of the 'Band' object. Defaults to 'None'.
            assignment (): Assignment of the band. Defaults to None
            fit (): Calculated fit for the band.. Defaults to None
            location (): Location of the band maximum.. Defaults to None
            start (): First data point attributed to the band.. Defaults to None
            end (): Last data point attributed to the band.. Defaults to None
            extinction_coefficient (): Molar extinction coefficient of the band.. Defaults to None
        """

        params = {
            "assignment": assignment,
            "fit": fit,
            "location": location,
            "start": start,
            "end": end,
            "extinction_coefficient": extinction_coefficient,
        }

        if id is not None:
            params["id"] = id

        obj = Band(**params)

        self.bands.append(obj)

        return self.bands[-1]

    def add_to_measurement_results(
        self,
        name: str,
        value: Optional[Value] = None,
        id: Optional[str] = None,
        **kwargs,
    ) -> Result:
        """
        This method adds an object of type 'Result' to attribute measurement_results

        Args:
            id (str): Unique identifier of the 'Result' object. Defaults to 'None'.
            name (): Name of the calculated value.
            value (): Value(s) for the specified result.. Defaults to None
        """

        params = {
            "name": name,
            "value": value,
        }

        if id is not None:
            params["id"] = id

        obj = Result(**params)

        self.measurement_results.append(obj)

        return self.measurement_results[-1]
