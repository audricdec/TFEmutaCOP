from CFMmodel import *
# Author: Audric Deckers - Testing the design of context-oriented software through mutation testing.
# Version: May 2023
# Replace the "None" in the following variables with the path to your txt files.
contextsFile=None
featuresFile=None
mappingFile=None

# Instantiates the CFMmodel class
cfmmodel = CFMmodel(contextsFile, featuresFile, mappingFile)

# Launches the recommendation system
cfmmodel.launchRecommendationSystem





