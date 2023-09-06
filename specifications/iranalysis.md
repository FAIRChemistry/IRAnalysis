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
- measurement_data
  - Type: [MeasurementData](#measurementdata)
  - Description: Each single measurement is contained in one `measurement_data` object.
  - Multiple: True


### MeasurementData

Container for a single measurement.

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
  - Type: [Units](#units)
  - Description: Unit of the data points contained in `data_array`.


## Enumerations


### Units

Enumeration contain controlled vocabularies for fields in your data model, in this case units that are allowed for this data model.

```python
ARBITRARY = "arb. unit"
NM = "nm"
UM = "μm"
MM = "mm"
CM = "cm"
METER = "m"
RECI_CM = "cm^-1"
```
