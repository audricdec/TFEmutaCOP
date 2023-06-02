class CFMNode:
    def __init__(self, name=None, type=None, parent=None, constraint=None, children=[], depth=0):
        self.name = name
        self.parent = parent
        self.type = type              # either contexts or features.
        self.constraint = constraint  # either "Alternative", "Or", "Optional" or "Mandatory".
        self.children = children      # List of children, if any.
        self.depth = depth            # 0 = root either "context" or "feature" in the CFM model.
        self.connectedPairs = []      # List to keep track of the nodes associated (cfr. connectedPairs).

        # Initialise the root connections
        if self.name == "Context":
            self.connectedPairs.append("Feature")
        elif self.name == "Feature":
            self.connectedPairs.append("Context")
            
    def printList(self, L):
        for elem in L:
            print("  " + elem)

    def printNode(self):
        print("---------------")
        print("Node: " + self.name)
        print("Parent: " + self.parent)
        print("Constraint: " + self.constraint)
        print("Children: ")
        self.printList(self.children)
        print("Depth: " + str(self.depth))
        print("Connected Pairs: ")
        self.printList(self.connectedPairs)
    