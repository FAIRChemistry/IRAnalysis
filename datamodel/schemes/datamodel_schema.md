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
    Analysis *-- Measurement
    Analysis *-- Band
    Analysis *-- Calculation
    Analysis *-- Result
    Analysis *-- Dataset
    Analysis *-- Series
    Band *-- Fit
    Band *-- Value
    Fit *-- Value
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
        +Value mass*
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
        +Measurement background_reference
        +Measurement sample_reference
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
        +UnitClass[0..*] units
    }
    
    class Result {
        +string name*
        +float[0..*] values
        +UnitClass[0..*] units
    }
    
    class Dataset {
        +datetime timestamp
        +Series x_axis
        +Series y_axis
    }
    
    class Series {
        +float[0..*] data_array
        +UnitClass unit
    }
    
    class Value {
        +float value
        +UnitClass unit
    }
    
    class MeasurementTypes {
        << Enumeration >>
        +BACKGROUND
        +SAMPLE
    }
    
```