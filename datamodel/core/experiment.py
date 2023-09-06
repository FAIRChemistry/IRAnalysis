import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator

from datetime import datetime as Datetime

from .measurementdata import MeasurementData
from .series import Series


@forge_signature
class Experiment(sdRDM.DataModel):

    """This could be a very basic object that keeps track of the entire experiment."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("experimentINDEX"),
        xml="@id",
    )

    name: str = Field(
        ...,
        description="A descriptive name for the overarching experiment.",
    )

    measurement_data: List[MeasurementData] = Field(
        description=(
            "Each single measurement is contained in one `measurement_data` object."
        ),
        default_factory=ListPlus,
        multiple=True,
    )

    def add_to_measurement_data(
        self,
        timestamp: Optional[Datetime] = None,
        x_axis: Optional[Series] = None,
        y_axis: Optional[Series] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'MeasurementData' to attribute measurement_data

        Args:
            id (str): Unique identifier of the 'MeasurementData' object. Defaults to 'None'.
            timestamp (): Date and time the measurement was performed.. Defaults to None
            x_axis (): The object containing data points and unit of the x-axis.. Defaults to None
            y_axis (): The object containing data points and unit of the y-axis.. Defaults to None
        """

        params = {
            "timestamp": timestamp,
            "x_axis": x_axis,
            "y_axis": y_axis,
        }

        if id is not None:
            params["id"] = id

        self.measurement_data.append(MeasurementData(**params))

        return self.measurement_data[-1]
