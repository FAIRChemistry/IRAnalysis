```mermaid
classDiagram
    IRAnalysis *-- Experiment
    Experiment *-- SamplePreparation
    Experiment *-- Measurement
    Experiment *-- Analysis
    Experiment *-- Result
    SamplePreparation *-- Value
    Measurement *-- MeasurementTypes
    Measurement *-- Dataset
    Measurement *-- Value
    Analysis *-- Band
    Analysis *-- Calculation
    Analysis *-- Result
    Analysis *-- Dataset
    Analysis *-- Series
    Band *-- Fit
    Band *-- Value
    Fit *-- Value
    Result *-- Value
    Dataset *-- Series
    
    class IRAnalysis {
        +datetime datetime_created*
        +datetime datetime_modified
        +string[0..*] contributors
        +Experiment[0..*] experiment
    }
    
    class Experiment {
        +string name*
        +SamplePreparation sample_preparation
        +Measurement[0..*] measurements
        +Analysis[0..*] analysis
        +Result results
    }
    
    class SamplePreparation {
        +Value mass
        +Value sample_area
        +string[0..*] literatureReference
        +string composition
        +string probeMolecule
        +string samplePreperation
    }
    
    class Measurement {
        +string name*
        +string geometry
        +Value temperature
        +Value pressure
        +MeasurementTypes measurement_type
        +Dataset measurement_data
    }
    
    class Analysis {
        +string background_reference
        +string sample_reference
        +Dataset corrected_data
        +Series baseline
        +Band[0..*] bands
        +Calculation[0..*] calculations
        +Result[0..*] measurement_results
    }
    
    class Band {
        +string assignment
        +Fit fit
        +Value location
        +Value start
        +Value end
        +Value extinction_coefficient
    }
    
    class Fit {
        +string model
        +string formula
        +Value[0..*] parameters
        +Value area
    }
    
    class Calculation {
        +string formula*
        +float[0..*] parameters
        +Unit[0..*] units
    }
    
    class Result {
        +string name*
        +Value value
    }
    
    class Dataset {
        +datetime timestamp
        +Series x_axis
        +Series y_axis
    }
    
    class Series {
        +float[0..*] data_array
        +Unit unit
    }
    
    class Value {
        +float value*
        +Unit unit*
        +float error
        +float error2
    }
    
    class MeasurementTypes {
        << Enumeration >>
        +BACKGROUND
        +SAMPLE
    }
    
```