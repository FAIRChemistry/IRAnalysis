# IRAnalysis
Toolkit for the analysis IR spectroscopic data.

## 🛠️ What is IRAnalysis?
IRAnalysis presents, as of now, a toolkit to process, analyze, fit and plot data obtained from FT-IR measurements. All data and analysis steps are stored in a data model which can be later exported to ensure reproducability.

## 📦 Installation

The tool is built on python 3.10. The following packages are required:

- numpy
- pandas
- matplotlib
- scipy
- astropy
- jupyter
- pybaselines
- sdRDM
***
To install packages with pip or anaconda run either

```bash
python -m pip install numpy pandas matplotlib scipy astropy jupyter pybaselines
```
or  
```bash
conda install numpy pandas matplotlib scipy astropy jupyter pybaselines
```
***
The datamodel is built with [sdRDM](https://github.com/FAIRChemistry/software-driven-rdm). To install either run
```bash
python -m pip install sdRDM
```
or build from source
```bash
git clone https://github.com/JR-1991/software-driven-rdm.git
cd software-driven-rdm
python3 setup.py install
```
***
The tool itself is available from [GitHub](https://github.com/FAIRChemistry/IRAnalysis/) by running:
```bash
git clone https://github.com/FAIRChemistry/IRAnalysis/
```

## ⚡️ Quick Start

The current user guide is found in the [user_guide.ipynb](https://github.com/FAIRChemistry/IRAnalysis/blob/main/user_guide.ipynb) jupyter notebook.

## ⚖️ License

MIT License

Copyright (c) 2024 FAIR Chemistry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
