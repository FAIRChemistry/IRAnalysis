# IRAnalysis data model

Python object model specifications based on the [software-driven-rdm](https://github.com/JR-1991/software-driven-rdm) Python library.


## Core objects


### IRAnalysis

Most meta object of your data model with some examples of sensible fields.

- __datetime_created__
  - Type: datetime
  - Description: Date and time this dataset has been created.
- datetime_modified
  - Type: datetime
  - Description: Date and time this dataset has last been modified.
- experiment
  - Type: [Experiment](#experiment)
  - Description: List of experiments associated with this dataset.


### Experiment

This could be a very basic object that keeps track of the entire experiment.

- __name__
  - Type: string
  - Description: A descriptive name for the overarching experiment.
- measurements
  - Type: [Measurement](#measurement)
  - Description: Each single measurement is contained in one `measurement` object.
  - Multiple: True
- corrected_spectra
  - Type:
  - Description:


### Measurement

Wow. Such docstring.

- name
  - Type: string
  - Description: Descriptive name for the single measurement.
- measurement_type
  - Type: [MeasurementTypes](#measurementtypes)
- measurement_data
  - Type: [Dataset](#dataset)
  - Description: Series objects of the measured axes.


### CorrectedSpectrum

Lorem ipsum.

- name
  - Type: string
  - Description: Descriptive name for the corrected spectrum.
- background_references
  - Type: @Measurement.id
  - Description: References to the IDs of background measurements used.
  - Multiple: True
- sample_reference
  - Type: @Measurement.id
  - Description: Reference to the ID of the sample measurement.
- corrected_data
  - Type: [Dataset](#dataset)
  - Description: Dataset based on a measured sample and corrected with one or more backgrounds.


### Dataset

Container for a single set of data.

- timestamp
  - Type: datetime
  - Description: Date and time the measurement was performed.
- x_axis
  - Type: [Series](#series)
  - Description: The object containing data points and unit of the x-axis.
- y_axis
  - Type: [Series](#series)
  - Description: The object containing data points and unit of the y-axis.


## Utility objects


### Series

Abstract Container for a measured Series (i.e. one axis).

- data_array
  - Type: float
  - Description: List of data points of one measured Series.
  - Multiple: True
- unit
  - Type: UnitClass
  - Description: Unit of the data points contained in `data_array`.


## Enumerations


### MeasurementTypes

lorem ipsum.

```python
BACKGROUND = auto()
SAMPLE = auto()
```
