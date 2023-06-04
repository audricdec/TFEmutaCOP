from CFMmodel import *
from time import *
# Author: Audric Deckers - Testing the design of context-oriented software through mutation testing.
# Version: May 2023
# Replace the "None" in the following variables with the path to your txt files.
contextsFile=None
featuresFile=None
mappingFile=None
totaltime = []

for i in range(50):
    starttime = time()
    cfmmodel = CFMmodel(contextsFile, featuresFile, mappingFile)
    endtime = time()
    totaltime.append((endtime - starttime)*1000)

averagetime = sum(totaltime) / len(totaltime)
print("Average time in ms: "+ str(averagetime))