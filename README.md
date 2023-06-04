# TFEmutaCOP
** Testing the design of context-oriented software through mutation testing
* Author: Audric Deckers - May 2023

## Architecture of the project
``` text
src/ 
├── README.md           << Documentation of the TFE
├── analysis.py         << Python script to generate validation results
├── graphs.py           << Python script to generate graphs 
├── CFMmodel.py         << Python file representing the CFMmodel
├── CFMnode.py          << Python file representing a node in the CFMmodel
└── models/
    ├── examples/       << Folder containing all models examples   
    └── mutants/        << Folder containing all generated mutants
```

## How to run
To use our recommendation system, you can use the following [python script](/launcher.py).
Replace the "None" values within the variables contextsFile, featuresFile, and mappingFile with the respective paths to your own files.
```python
contextsFile=None
featuresFile=None
mappingFile=None

# Instantiates the CFMmodel class
cfmmodel = CFMmodel(contextsFile, featuresFile, mappingFile)

# Launches the recommendation system
cfmmodel.launchRecommendationSystem
```

You can launch it using the following command in your terminal, at the root of the project:
```bash
python3 launcher.py
```