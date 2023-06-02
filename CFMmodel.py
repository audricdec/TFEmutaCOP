# Author: Audric Deckers
import sys
from time import sleep
from CFMnode import *

class CFMmodel:
    def __init__(self, contextsFile=None, featuresFile=None, mappingFile=None):
        path = 'models/examples/runningexample/'
        if featuresFile is None:
            featuresFile = path+'features.txt'
        if contextsFile is None:
            contextsFile = path+'contexts.txt'
        if mappingFile is None:
            mappingFile = path+'mapping.txt'

        # Set to keep track of each nodes (contexts + features)
        self.nodes = set()

        # List containing CFMnodes information (cfr. CFMnode.py)
        self.cfmnodes = []
        # List of CFMnodes that are exclusively features.
        self.cfmfeatures = []
        # List of CFMnodes that are exclusively contexts.
        self.cfmcontexts = []

        # Initialise set of contexts
        self.contexts = set()
        self.processCFFiles(contextsFile, "contexts")

        # Initialise set of features
        self.features = set()
        self.processCFFiles(featuresFile, "features")

        # Initialise mapping dictionnaries
        self.dictContext = {}
        self.dictFeature = {}
        self.processMappingFile(mappingFile)

        # Initialise connected pairs in the CFM
        self.connectedPairs = []
        self.generateConnectedPairs()

        # Initialise questions List
        self.questions = []

        # Initialise mutations
        self.mutants = []
        self.generateMutants()


    # ---------------------------
    # --------- HELPERS ---------
    # -------- FUNCTIONS --------
    # ---------------------------

    def addToSet(self, toBeAdded, modelType):
        """
        Adds toBeAdded to the modelType set and in the nodes set.
        """
        if modelType == "contexts":
            self.contexts.add(toBeAdded)
        if modelType == "features":
            self.features.add(toBeAdded)
        self.nodes.add(toBeAdded)

    def addNode(self, toBeAdded, modelType):
        """
        Adds toBeAdded to the cfmmodelType list and in the cfmnodes list.
        """
        if modelType == "contexts":
            self.cfmcontexts.append(toBeAdded)
        if modelType == "features":
            self.cfmfeatures.append(toBeAdded)
        self.cfmnodes.append(toBeAdded)

    def checkMappingDefinitions(self, dictionnary, type):
        """
        Checks whether all elements in dictionnary are in the ${type}s.txt file.
        """
        for elems in dictionnary:
            for elem in elems.split('-'):
                if elem not in self.nodes:
                    print("FORMAT ERROR: The "+type+" '"+elem +
                          "' in mapping.txt does not seem to be defined in "+type+"s.txt")
                    sys.exit()

    def flattenDict(self, d):
        """
        Flattens a nested dictionary by splitting keys containing hyphens and merging values.
        """
        result = {}
        for key, values in d.items():
            for value in values:
                for sub_key in key.split("-"):
                    if sub_key not in result:
                        result[sub_key] = []
                    result[sub_key].append(value)
        return result

    def modifyConstraint(self, consContext, consFeature, connectedPair):
        """
        Creates a mutant from a subModel by modifying constraintContext to consContext 
        and constraintFeature to consFeature.
        """
        mutant = connectedPair.copy()
        mutant['constraintContext'] = consContext
        mutant['constraintFeature'] = consFeature
        return mutant

    def evalSet(self, dictionnary):
        return list(map(lambda dict: eval(dict), dictionnary))

    def set_node_depth(self, node, depth, cfmnodes):
        node.depth = depth
        for child_name in node.children:
            child_node = next(
                (n for n in cfmnodes if n.name == child_name), None)
            if child_node:
                self.set_node_depth(child_node, depth + 1, cfmnodes)

    # ---------------------------
    # --------- STEP 1 ----------
    # ----- DATA EXTRACTION -----
    # ---------------------------

    def processCFFiles(self, filename, type):
        """
        Reads the content of the file of type = {contexts / features} and returns a list of, 
        dictionaries where each dictionary contains the values of the three columns in the
        file splitted into 'parent{type}', 'constraint{type}', 'childrens{type}', and 
        'mutable{type}' keys.
        """
        modelType = "contexts" if type == "contexts" else "features"

        if filename is None:
            print("Please, provide a valid " + modelType + ".txt file.\n")
            sys.exit()

        else:
            with open(filename) as f:
                for line in f:
                    # row[0] = parent, row[1] = constraint, row[2] = children
                    row = line.strip().split('/')
                    if row:
                        # Handle wrong format case
                        if row[1].lower() not in ["mandatory", "optional", "or", "alternative"]:
                            print("FORMAT ERROR: In your "+modelType+".txt file, line: " + line + "does not seem to define a valid relationship.")
                            sys.exit()
                        else:
                            # Add parent to the set
                            self.addToSet(row[0], modelType)
                            type = "Context" if modelType == "contexts" else "Feature"
                            self.addNode(CFMNode(name=row[0], parent=type, type=type.lower(), constraint=row[1], children=row[2].split('-')), modelType)
                            # Split and add each child to the set
                            for child in row[2].split('-'):
                                self.addToSet(child, modelType)
                                self.addNode(CFMNode(name=child, parent=row[0], type=type.lower(), constraint=row[1], children=[]), modelType)
            # Set up depth
            for node in self.cfmnodes:
                if node.name == "Context" or node.name == "Feature":
                    self.set_node_depth(node, 0, self.cfmnodes)
                if node.parent == "Context" or node.parent == "Feature":
                    self.set_node_depth(node, 1, self.cfmnodes)

    def processMappingFile(self, filename):
        """ 
        Reads the content of the mapping file and sets a tuple containing two dictionaries. 

        The first dictionary maps contexts to sets of features that they activate. 
        The second dictionary maps features to sets of contexts that activate them. 
        """
        if filename is None:
            print("Please, provide a valid mapping.txt file.\n")
            sys.exit()

        else:
            with open(filename) as f:
                for line in f:
                    # Extract Contexts-ACTIVATES-Features
                    mapContexts, mapFeatures = map(str.split, line.strip().split('-ACTIVATES-'))

                    self.checkMappingDefinitions(mapContexts, "context")
                    self.checkMappingDefinitions(mapFeatures, "feature")

                    self.dictContext.update({context: mapFeatures for context in mapContexts})
                    self.dictFeature.update({feature: mapContexts for feature in mapFeatures})

    # ---------------------------
    # --------- STEP 2 ----------
    # ----- CONNECTED PAIRS -----
    # ---------------------------

    def generateConnectedPairs(self):
        """
        Generates connected pairs between CFM nodes. This method iterates through the CFM nodes and establishes connected pairs 
        between them based on certain conditions. The connected pairs are stored in the 'connectedPairs' attribute of each CFM node
        and in the self.connectedPairs list.
        """
        setConnectedPairs = set()
        dictContexts = self.flattenDict(self.dictContext)
        dictFeatures = self.flattenDict(self.dictFeature)

        for context in self.cfmcontexts:
            for feature in self.cfmfeatures:
                for childContext in context.children:
                    for childFeature in feature.children:
                        if childContext not in dictContexts or childFeature not in dictFeatures:
                            continue
                        if childFeature in dictContexts[childContext] or childContext in dictFeatures[childFeature]:

                            if context.name not in dictContexts and feature.name not in dictFeatures:
                                if context.name != "Context" and feature.name != "Feature":
                                    setConnectedPairs.add(str({'parentContext': context.name,
                                            'constraintContext': context.constraint,
                                            'childrenContext': context.children,
                                            'parentFeature': feature.name,
                                            'constraintFeature': feature.constraint,
                                            'childrenFeature': feature.children}))
                                    #if feature.name not in context.connectedPairs:
                                    #    context.connectedPairs.append(
                                    #        feature.name)

                            if context.name not in dictContexts and feature.name in dictFeatures:
                                for fea in self.cfmfeatures:
                                    if childFeature == fea.name:
                                        setConnectedPairs.add(str({'parentContext': context.name,
                                             'constraintContext': context.constraint,
                                             'childrenContext': context.children,
                                             'parentFeature': childFeature,
                                             'constraintFeature': fea.constraint,
                                             'childrenFeature': fea.children}))
                                #if childFeature not in context.connectedPairs:
                                #    context.connectedPairs.append(childFeature)

                            if context.parent == "Context" and context.constraint not in ["Alternative", "Or"]:
                                if feature.parent == "Feature":
                                    #for con in self.cfmcontexts:
                                    #    if childContext == con.name and childFeature not in con.connectedPairs:
                                    #        con.connectedPairs.append(
                                    #            childFeature)
                                    for fea in self.cfmfeatures:
                                        for con in self.cfmcontexts:
                                            if childFeature == fea.name and childContext == con.name:
                                                setConnectedPairs.add(str({'parentContext': childContext,
                                                'constraintContext': con.constraint,
                                                'childrenContext': con.children,
                                                'parentFeature': childFeature,
                                                'constraintFeature': fea.constraint,
                                                'childrenFeature': fea.children}))
                                else:
                                    #for con in self.cfmcontexts:
                                    #    if childContext == con.name and feature.name not in con.connectedPairs:
                                    #        con.connectedPairs.append(
                                    #            feature.name)
                                    for con in self.cfmcontexts:
                                        if childContext == con.name:
                                            setConnectedPairs.add(str({'parentContext': childContext,
                                                'constraintContext': con.constraint,
                                                'childrenContext': con.children,
                                                'parentFeature': feature.name,
                                                'constraintFeature': feature.constraint,
                                                'childrenFeature': feature.children}))

                            elif feature.name == "Feature" and feature.constraint not in ["Alternative", "Or"]:
                                for fea in self.cfmfeatures:
                                    if childFeature == fea.name:
                                        setConnectedPairs.add(str({'parentContext': context.name,
                                             'constraintContext': context.constraint,
                                             'childrenContext': context.children,
                                             'parentFeature': childFeature,
                                             'constraintFeature': fea.constraint,
                                             'childrenFeature': fea.children}))
                                #if childFeature not in context.connectedPairs:
                                #    context.connectedPairs.append(childFeature)

        self.connectedPairs = self.evalSet(setConnectedPairs)

    # ---------------------------
    # --------- STEP 3 ----------
    # ---- MUTANT GENERATION ----
    # ---------------------------

    def generateMutants(self):
        """
        Generates mutants based on connected pairs. This method generates mutants by iterating through the connected pairs 
        and applying specific mutations based on the constraints of the parent context and parent feature. The mutants are 
        stored in self.mutants, and corresponding questions, mutations to be performed and expected answers for evaluation 
        are stored self.questions.
        """
        path = "models/mutants/"
        modelFile = open(path+"mutations.txt", "w")
        count = 0

        for connectedPair in self.connectedPairs:
            parentContext = connectedPair['parentContext']
            parentFeature = connectedPair['parentFeature']
            childrenContext = ','.join(connectedPair['childrenContext'])
            childrenFeature = ','.join(connectedPair['childrenFeature'])
            modelFile.write("Connected Pair processed: <"+parentContext+","+parentFeature+"> \n")
            contextConstraint = connectedPair['constraintContext']
            constraintFeature = connectedPair['constraintFeature']

            # If constraintContext is Alternative and constraintFeature is Alternative:
            if contextConstraint == 'Alternative' and constraintFeature == 'Alternative':
                # Apply AltToOr.
                mutant = self.modifyConstraint('Or', 'Or', connectedPair)
                mutation = "Modify the constraints of " + parentContext+" context and "+parentFeature+" feature from Alternatives to Or constraints"
                modelFile.write("Applying AltToOr to "+parentContext+" and "+parentFeature+". \n")
                self.mutants.append(mutant)
                self.questions.append({'question':"Is it possible for "+childrenContext+" contexts and for "+childrenFeature+" features to be activated simultaneously?",'mutation': mutation, 'answer':['yes','y']})

            # If constraintContext is Alternative and constraintFeature is Or:
            if contextConstraint == 'Alternative' and constraintFeature == 'Or':

                # Apply AltToOr.
                mutant = self.modifyConstraint('Or', 'Or', connectedPair)
                mutation = "Modify the constraint of " + parentContext+" context from Alternative to Or constraint"
                modelFile.write("Applying AltToOr to "+parentContext+". \n")
                self.mutants.append(mutant)
                self.questions.append({'question':"Is it possible for "+childrenContext+" contexts to be activated simultaneously?",'mutation': mutation, 'answer':['yes','y']})


                # Apply OrToAlt.
                mutant = self.modifyConstraint('Alternative', 'Alternative', connectedPair)
                mutation2 = "Modify the constraint of " + parentFeature+" feature from Or to Alternative constraint"
                modelFile.write("Applying OrToAlt to "+parentFeature+". \n")
                self.mutants.append(mutant)
                self.questions.append({'question':"Is it possible for "+childrenFeature+" features to be activated simultaneously?",'mutation': mutation2, 'answer':['no','n']})
                count += 1

            # If constraintContext is Or and constraintFeature is Alternative:
            if contextConstraint == 'Or' and constraintFeature == 'Alternative':

                # Apply OrToAlt.
                mutant = self.modifyConstraint('Alternative', 'Alternative', connectedPair)
                mutation = "Modify the constraint of " + parentContext+" context from Or to Alternative constraint"
                modelFile.write("Applying OrToAlt to "+parentContext+". \n")
                self.questions.append({'question':"Is it possible for "+childrenContext+" contexts to be activated simultaneously?",'mutation': mutation, 'answer':['no','n']})
                self.mutants.append(mutant)

                # Apply AltToOr.
                mutant = self.modifyConstraint('Or', 'Or', connectedPair)
                mutation2 = "Modify the constraint of " + parentFeature+" feature from Alternative to Or constraint"
                modelFile.write("Applying AltToOr to "+parentFeature+". \n")
                self.questions.append({'question':"Is it possible for "+childrenFeature+" features to be activated simultaneously?",'mutation': mutation2, 'answer':['yes','y']})
                self.mutants.append(mutant)
                count += 1

            # If both constraints are Or:
            if contextConstraint == 'Or' and constraintFeature == 'Or':

                # Apply OrToAlt.
                mutant = self.modifyConstraint('Alternative', 'Alternative', connectedPair)
                mutation = "Modify the constraints of " + parentContext+" context and "+parentFeature+" feature from Or to Alternative constraints"
                modelFile.write("Applying OrToAlt to " + parentContext+" and "+parentFeature+"\n")
                self.questions.append({'question':"Is it possible for "+childrenContext+" contexts and for "+childrenFeature+" features to be activated simultaneously?",'mutation': mutation, 'answer':['no','n']})
                self.mutants.append(mutant)

                # Apply OrToOpt
                mutant = self.modifyConstraint('Optional', 'Optional', connectedPair)
                mutation2 = "Modify the constraints of " + parentContext+" context and "+parentFeature+" feature from Or to Optional constraints"
                modelFile.write("Applying OrToOpt to " +parentContext+" and "+parentFeature+"\n")
                self.questions.append({'question':"Is it possible for "+childrenContext+" contexts and for "+childrenFeature+" features to be deactivated simultaneously?",'mutation': mutation2, 'answer':['yes','y']})
                self.mutants.append(mutant)
                count += 1

            # If constraintContext is Alternative and constraintFeature is Optional or Mandatory:
            if contextConstraint == 'Alternative' and (constraintFeature == 'Optional' or constraintFeature == 'Mandatory'):
                # Apply AltToOr.
                mutant = self.modifyConstraint('Or', constraintFeature, connectedPair)
                mutation = "Modify the constraint of " + parentContext+" context from Alternative to Or constraint"
                modelFile.write("Applying AltToOr to " + parentContext+". \n")
                self.questions.append({'question':"Is it possible for "+childrenContext+" contexts to be activated simultaneously?",'mutation': mutation, 'answer':['yes','y']})
                self.mutants.append(mutant)

            # If constraintContext is Or and constraintFeature is Optional or Mandatory:
            if contextConstraint == 'Or' and (constraintFeature == 'Optional' or constraintFeature == 'Mandatory'):
                # Apply OrToAlt.
                mutant = self.modifyConstraint('Alternative', constraintFeature, connectedPair)
                mutation = "Modify the constraint of " + parentContext+" context from Or to Alternative constraint"
                modelFile.write("Applying OrToAlt to " + parentContext+". \n")
                self.questions.append({'question':"Is it possible for "+childrenContext+" contexts to be activated simultaneously?",'mutation': mutation, 'answer':['no','n']})
                self.mutants.append(mutant)

                # Apply OrToOpt.
                mutant = self.modifyConstraint('Optional', constraintFeature, connectedPair)
                mutation2 = "Modify the constraint of " + parentContext+" context from Or to Optional constraint"
                modelFile.write("Applying OrToOpt to " + parentContext+". \n")
                self.questions.append({'question':"Is it possible for "+childrenContext+" contexts to be deactivated simultaneously?",'mutation': mutation2, 'answer':['yes','y']})
                self.mutants.append(mutant)
                count += 1

            # If constraintContext is Mandatory and constraintFeature is Optional:
            if contextConstraint == 'Mandatory' and constraintFeature == 'Optional':

                # Apply ManToOpt.
                mutant = self.modifyConstraint('Optional', 'Optional', connectedPair)
                mutation = "Modify the constraint of " + parentContext+" context from Mandatory to Optional constraint"
                modelFile.write("Applying ManToOpt to " + parentContext+". \n")
                self.questions.append({'question':"Do "+parentContext+" context(s) have to be activated in any configuration?",'mutation': mutation, 'answer':['no','n']})
                self.mutants.append(mutant)

            count += 1
            modelFile.write("\n")


        modelFile.write("Total mutant generated: "+str(count)+"\n")
        modelFile.close()

    # ---------------------------
    # --------- STEP 4 ----------
    # ------- MUTANT Q&A --------
    # ---------------------------

    def launchRecommendationSystem(self):
        print()
        print("╔══════════════════════════════════════════════╗")
        print("║   The recommendation system will start,      ║")
        print("║   answer each question carefully. Accepted   ║")
        print("║   answers are among (yes, y, no, n).         ║")
        print("╚══════════════════════════════════════════════╝")
        sleep(0.5)
        count = 1
        nbr_mutations = 0
        mutations = set()
        for question in self.questions:
            print("")
            print("Question "+str(count)+ ":")
            print("══════════")
            while True:
                response = input(question['question'] + " (yes/no): \n").lower()
                if response == "yes" or response == "y":
                    if response in question['answer']:
                        nbr_mutations += 1 
                        print("Suggestion: " + question['mutation'])
                        mutations.add(question['mutation'])
                        sleep(0.5)
                    break
                elif response == "no" or response == "n":
                    if response in question['answer']:
                        nbr_mutations += 1 
                        print("Suggestion: " + question['mutation'])
                        mutations.add(question['mutation'])
                        sleep(0.5)
                    break
                else:
                    print("Invalid response. Please enter 'yes', 'y', 'no' or 'n'.")
            count+=1
        print("╔══════════════════════════════════════════════╗")
        print("║            The process is now over.          ║")
        print("║            Mutation score: " + str(len(self.questions) - nbr_mutations) + "/" + str(len(self.questions)) + ".              ║")
        print("╚══════════════════════════════════════════════╝")
        print("Summary of the recommendations:")
        for mut in mutations:
            print("- " + mut)



