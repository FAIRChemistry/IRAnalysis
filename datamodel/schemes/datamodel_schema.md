```mermaid
classDiagram
    IRAnalysis *-- Experiment
    Experiment *-- Measurement
    Experiment *-- CorrectedSpectrum
    Measurement *-- MeasurementTypes
    Measurement *-- Dataset
    CorrectedSpectrum *-- Measurement
    CorrectedSpectrum *-- Dataset
    Dataset *-- Series
    
    class IRAnalysis {
        +datetime datetime_created*
        +datetime datetime_modified
        +Experiment experiment
    }
    
    class Experiment {
        +string name*
        +Measurement[0..*] measurements
        +CorrectedSpectrum[0..*] corrected_spectra
    }
    
    class Measurement {
        +string name
        +MeasurementTypes measurement_type
        +Dataset measurement_data
    }
    
    class CorrectedSpectrum {
        +string name
        +Measurement[0..*] background_references
        +Measurement sample_reference
        +Dataset corrected_data
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
    
    class MeasurementTypes {
        << Enumeration >>
        +BACKGROUND
        +SAMPLE
    }
    
```