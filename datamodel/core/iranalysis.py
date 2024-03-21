import sdRDM

from typing import Dict, List, Optional
from pydantic import PrivateAttr, model_validator
from uuid import uuid4
from pydantic_xml import attr, element
from lxml.etree import _Element
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from sdRDM.tools.utils import elem2dict
from datetime import datetime as Datetime
from .samplepreparation import SamplePreparation
from .experiment import Experiment
from .analysis import Analysis
from .result import Result
from .measurement import Measurement


@forge_signature
class IRAnalysis(sdRDM.DataModel, search_mode="unordered"):
    """Most meta object of your data model with some examples of sensible fields."""

    id: Optional[str] = attr(
        name="id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
        xml="@id",
    )

    datetime_created: Datetime = element(
        description="Date and time this dataset has been created.",
        tag="datetime_created",
        json_schema_extra=dict(),
    )

    datetime_modified: Optional[Datetime] = element(
        description="Date and time this dataset has last been modified.",
        default=None,
        tag="datetime_modified",
        json_schema_extra=dict(),
    )

    contributors: List[str] = element(
        description="List of contributors.",
        default_factory=ListPlus,
        tag="contributors",
        json_schema_extra=dict(multiple=True),
    )

    experiment: List[Experiment] = element(
        description="List of experiments associated with this dataset.",
        default_factory=ListPlus,
        tag="experiment",
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

    def add_to_experiment(
        self,
        name: str,
        sample_preparation: Optional[SamplePreparation] = None,
        measurements: List[Measurement] = ListPlus(),
        analysis: List[Analysis] = ListPlus(),
        results: Optional[Result] = None,
        id: Optional[str] = None,
    ) -> Experiment:
        """
        This method adds an object of type 'Experiment' to attribute experiment

        Args:
            id (str): Unique identifier of the 'Experiment' object. Defaults to 'None'.
            name (): A descriptive name for the overarching experiment..
            sample_preparation (): Synthesis and preparation parameters. Defaults to None
            measurements (): Each single measurement is contained in one `measurement` object.. Defaults to ListPlus()
            analysis (): Analysis procedure and parameters.. Defaults to ListPlus()
            results (): List of final results calculated from measurements done for the experiment.. Defaults to None
        """
        params = {
            "name": name,
            "sample_preparation": sample_preparation,
            "measurements": measurements,
            "analysis": analysis,
            "results": results,
        }
        if id is not None:
            params["id"] = id
        self.experiment.append(Experiment(**params))
        return self.experiment[-1]
