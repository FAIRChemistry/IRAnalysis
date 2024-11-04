from typing import Dict, List, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict

from .analysis import Analysis
from .band import Band
from .dataset import Dataset
from .detection import Detection
from .measurement import Measurement
from .measurementtypes import MeasurementTypes
from .parameters import Parameters
from .result import Result
from .series import Series
from .value import Value


class Experiment(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """This could be a very basic object that keeps track of the entire experiment."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    name: str = element(
        description="A descriptive name for the overarching experiment.",
        tag="name",
        json_schema_extra=dict(),
    )

    varied_parameter: Optional[str] = element(
        description="Parameter that was varied between measurements.",
        default=None,
        tag="varied_parameter",
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

    measurements: List[Measurement] = element(
        description="Each single measurement is contained in one `measurement` object.",
        default_factory=ListPlus,
        tag="measurements",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    analysis: List[Analysis] = element(
        description="Analysis procedure and parameters.",
        default_factory=ListPlus,
        tag="analysis",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    results: Optional[Result] = element(
        description=(
            "List of final results calculated from measurements done for the"
            " experiment."
        ),
        default=None,
        tag="results",
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

    def add_to_measurements(
        self,
        name: str,
        detection: Detection,
        varied_parameter_value: Optional[Value] = None,
        measurement_type: Optional[MeasurementTypes] = None,
        measurement_data: Optional[Dataset] = None,
        static_parameters: Optional[Parameters] = None,
        id: Optional[str] = None,
        **kwargs,
    ) -> Measurement:
        """
        This method adds an object of type 'Measurement' to attribute measurements

        Args:
            id (str): Unique identifier of the 'Measurement' object. Defaults to 'None'.
            name (): Descriptive name for the single measurement..
            detection (): Method/Geometry of detection..
            varied_parameter_value (): Value of the varied parameter for the given measurement.. Defaults to None
            measurement_type (): Type of measurement.. Defaults to None
            measurement_data (): Series objects of the measured axes.. Defaults to None
            static_parameters (): Parameter object with attributes that do not change during the experiment or measurement series.. Defaults to None
        """

        params = {
            "name": name,
            "detection": detection,
            "varied_parameter_value": varied_parameter_value,
            "measurement_type": measurement_type,
            "measurement_data": measurement_data,
            "static_parameters": static_parameters,
        }

        if id is not None:
            params["id"] = id

        obj = Measurement(**params)

        self.measurements.append(obj)

        return self.measurements[-1]

    def add_to_analysis(
        self,
        sample_reference: str,
        background_reference: Optional[str] = None,
        corrected_data: Optional[Dataset] = None,
        baseline: Optional[Series] = None,
        bands: List[Band] = ListPlus(),
        measurement_results: List[Result] = ListPlus(),
        id: Optional[str] = None,
        **kwargs,
    ) -> Analysis:
        """
        This method adds an object of type 'Analysis' to attribute analysis

        Args:
            id (str): Unique identifier of the 'Analysis' object. Defaults to 'None'.
            sample_reference (): Reference to the ID of the sample measurement..
            background_reference (): Reference to the IDs of background measurements used.. Defaults to None
            corrected_data (): Dataset based on a measured sample and corrected with the background measurement and optionally baseline corrected.. Defaults to None
            baseline (): Dataset containing the baseline values. Calculation is based on the classification algorithm FastChrom (Johnsen, L., et al., Analyst. 2013, 138, 3502-3511.).. Defaults to None
            bands (): Bands assigned and quantified within the spectrum.. Defaults to ListPlus()
            measurement_results (): List of final results calculated from one measurement.. Defaults to ListPlus()
        """

        params = {
            "sample_reference": sample_reference,
            "background_reference": background_reference,
            "corrected_data": corrected_data,
            "baseline": baseline,
            "bands": bands,
            "measurement_results": measurement_results,
        }

        if id is not None:
            params["id"] = id

        obj = Analysis(**params)

        self.analysis.append(obj)

        return self.analysis[-1]
