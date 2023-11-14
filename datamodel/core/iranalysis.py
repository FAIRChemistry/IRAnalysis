import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator

from datetime import datetime as Datetime

from .samplepreparation import SamplePreparation
from .experiment import Experiment
from .correctedspectrum import CorrectedSpectrum
from .measurement import Measurement


@forge_signature
class IRAnalysis(sdRDM.DataModel):

    """Most meta object of your data model with some examples of sensible fields."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("iranalysisINDEX"),
        xml="@id",
    )

    datetime_created: Datetime = Field(
        ...,
        description="Date and time this dataset has been created.",
    )

    datetime_modified: Optional[Datetime] = Field(
        default=None,
        description="Date and time this dataset has last been modified.",
    )

    contributors: List[str] = Field(
        description="List of contributors.",
        default_factory=ListPlus,
        multiple=True,
    )

    experiment: List[Experiment] = Field(
        description="List of experiments associated with this dataset.",
        default_factory=ListPlus,
        multiple=True,
    )

    def add_to_experiment(
        self,
        name: str,
        sample_preparation: Optional[SamplePreparation] = None,
        measurements: List[Measurement] = ListPlus(),
        corrected_spectra: List[CorrectedSpectrum] = ListPlus(),
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Experiment' to attribute experiment

        Args:
            id (str): Unique identifier of the 'Experiment' object. Defaults to 'None'.
            name (): A descriptive name for the overarching experiment..
            sample_preparation (): Synthesis and preparation parameters. Defaults to None
            measurements (): Each single measurement is contained in one `measurement` object.. Defaults to ListPlus()
            corrected_spectra (): List of background-corrected spectra. Defaults to ListPlus()
        """

        params = {
            "name": name,
            "sample_preparation": sample_preparation,
            "measurements": measurements,
            "corrected_spectra": corrected_spectra,
        }

        if id is not None:
            params["id"] = id

        self.experiment.append(Experiment(**params))

        return self.experiment[-1]
