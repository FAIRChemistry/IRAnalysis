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
- contributors
  - Type: string
  - Description: List of contributors.
  - Multiple: True
- experiment
  - Type: [Experiment](#experiment)
  - Description: List of experiments associated with this dataset.
  - Multiple: True

### Experiment

This could be a very basic object that keeps track of the entire experiment.

- __name__
  - Type: string
  - Description: A descriptive name for the overarching experiment.
- sample_preparation
  - Type: [SamplePreparation](#samplepreparation)
  - Description: Synthesis and preparation parameters
- measurements
  - Type: [Measurement](#measurement)
  - Description: Each single measurement is contained in one `measurement` object.
  - Multiple: True
- corrected_spectra
  - Type: [CorrectedSpectrum](#correctedspectrum)
  - Description: List of background-corrected spectra
  - Multiple: True



### SamplePreparation

This keeps track of important synthesis parameters relevant for later analysis.

- __mass__
  - Type: float
  - Description: Mass of the IR sample
- literatureReference
  - Type: string
  - Description: Points to literature references used for the sample preparation
  - Multiple: True
- composition
  - Type: string
  - Description: Relative amount of components used in preparation
- probeMolecule
  - Type: string
  - Description: Probe molecule used
- samplePreperation
  - Type: string
  - Description: Addidional description of preperation parameters.

### Measurement

Contains all measurements done for the experiment. E.g. sample, unloaded sample and background.

- __name__
  - Type: string
  - Description: Descriptive name for the single measurement.
- geometry
  - Type: string
  - Description: Spectrometer geometry used for the measurement
- temperature
  - Type: float
  - Description: Temperature at which the measurement was performed.
- pressure
  - Type: float
  - Description: Pressure at which the measurement was performed.
- measurement_type
  - Type: [MeasurementTypes](#measurementtypes)
  - Description: Type of measurement.
- measurement_data
  - Type: [Dataset](#dataset)
  - Description: Series objects of the measured axes.


### CorrectedSpectrum

Resulting spectrum after removing the background and unloaded sample intensities.

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


### Results

Resulting values calculated from the corrected spectrum

- fitting_parameters
  - Type: [Series](#series)
  - Description: Object containing fitting parameters for all curves
- n_active_sites
  - Type: [Series](#series)
  - Description: Object containing number of Lewis, Bronstedt and mixed active sites


### Dataset

Container for a single set of data.

- timestamp
  - Type: datetime
  - Description: Date and time the data was recorded
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

Possible types of measurements to be used during analysis

```python
BACKGROUND = "Background"
SAMPLE = "Sample"
```
