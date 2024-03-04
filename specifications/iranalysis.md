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
- analysis
  - Type: [Analysis](#analysis)
  - Description: Analysis procedure and parameters.
  - Multiple: True
- results
  - Type: [Result](#result)
  - Description: List of final results calculated from measurements done for the experiment.


### SamplePreparation

This keeps track of important synthesis parameters relevant for later analysis.

- __mass__
  - Type: [Value](#value)
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
  - Type: [Value](#value)
  - Description: Temperature at which the measurement was performed.
- pressure
  - Type: [Value](#value)
  - Description: Pressure at which the measurement was performed.
- measurement_type
  - Type: [MeasurementTypes](#measurementtypes)
  - Description: Type of measurement.
- measurement_data
  - Type: [Dataset](#dataset)
  - Description: Series objects of the measured axes.

### Analysis

Contains all steps and parameters used to manipulate data and to calculate results from one sample measurement.

- background_reference
  - Type: @Measurement.id
  - Description: Reference to the IDs of background measurements used.
- sample_reference
  - Type: @Measurement.id
  - Description: Reference to the ID of the sample measurement.
- corrected_data
  - Type: [Dataset](#dataset)
  - Description: Dataset based on a measured sample and corrected with the background measurement and optionally baseline corrected.
- baseline
  - Type: [Series](#series)
  - Description: Dataset containing the baseline values. Calculation is based on the classification algorithm FastChrom (Johnsen, L., et al., Analyst. 2013, 138, 3502-3511.).
- bands
  - Type: [Band](#band)
  - Description: Bands assigned and quantified within the spectrum.
  - Multiple: True
- calculations
  - Type: [Calculation](#calculation)
  - Description: Calculations performed during the analysis.
  - Multiple: True
- measurement_results
  - Type: [Result](#result)
  - Description: List of final results calculated from one measurement.
  - Multiple: True


### Band

Contains parameters of a band analyzed during the analysis.

- assignment
  - Type: string
  - Description: Assignment of the band
- fit
  - Type: [Fit](#fit)
  - Description: Calculated fit for the band.
- location
  - Type: [Value](#value)
  - Description: Location of the band maximum.
- start
  - Type: [Value](#value)
  - Description: First data point attributed to the band.
- end
  - Type: [Value](#value)
  - Description: Last data point attributed to the band.


### Fit

Contains the fitting function and the found optimal parameters.

- model
  - Type: string
  - Description: Description of the fitting model used (e.g. Gauss-Lorentz)
- formula
  - Type: string
  - Description: Implemented formula of the fitting model. Corresponds with the sequence of fitting parameters.
- parameters
  - Type: [Value](#value)
  - Description: Optained optimal fitting parameters. Sequence according to formula.
  - Multiple: True
- area
  - Type: [Value](#value)
  - Description: Total area of the fitted model curve.


### Calculation

Contains the formula and it's parameters used for a calculation during the analysis.

- __formula__
  - Type: string
  - Description: Formula for the used calculation.
- parameters
  - Type: float
  - Description: Parameters used for the given formula. Ordered chronologically as described in the formula definition.
  - Multiple: True
- units
  - Type: UnitClass
  - Description: Units of the values contained in `parameters`. Ordered chronologically as in the parameters list.
  - Multiple: True

### Result

Final result obtained from the analysis.

- __name__
  - Type: string
  - Description: Name of the calculated value
- values
  - Type: float
  - Description: Value(s) for the specified result.
  - Multiple: True
- units
  - Type: UnitClass
  - Description: Units of the values contained in `values`. Ordered chronologically as in the values list.
  - Multiple: True


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


### Value

Abstract Container for a single value-unit pair.

- value
  - Type: float
  - Description: Value of the data point
- unit
  - Type: UnitClass
  - Description: Unit of the data point contained in `value`.


## Enumerations


### MeasurementTypes

Possible types of measurements to be used during analysis

```python
BACKGROUND = "Background"
SAMPLE = "Sample"
```
