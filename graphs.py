import matplotlib.pyplot as plt

# Data
contexts = [3, 6, 11, 20, 25, 60]
features = [3, 7, 18, 27, 32, 60]
nodes = [6, 13, 29, 47, 57, 120]
mapping = [2, 4, 8, 14, 13, 35]
c_pairs = [1, 2, 6, 11, 10, 48]
mutants = [2, 3, 7, 15, 11, 88]
questions = [2, 3, 6, 11, 15, 88]
time = [0.685, 0.801, 1.217, 1.801, 1.885, 5.727]

# Create the graph
plt.figure(figsize=(10, 6))
#plt.plot(nodes, mapping, label='Mapping')
#plt.plot(nodes, c_pairs, label='Connected Pairs')
#plt.plot(nodes, mutants, label='Mutants')
#plt.plot(nodes, questions, label='Questions')
plt.plot(nodes, time, label='Time')

# Customize the graph
plt.xlabel('Number of Nodes (Contexts + Features)')
plt.ylabel('Time[ms]')
plt.title('Evolution of Time with respect to Number of Contexts and Features')
plt.legend()
plt.savefig('AnalysisTime')

# Show the graph
plt.show()

# Create the graph
plt.figure(figsize=(10, 6))
plt.plot(mapping, c_pairs, label='Connected Pairs')
plt.plot(mapping, mutants, label='Mutants')
plt.plot(mapping, questions, label='Questions')
plt.plot(mapping, time, label='Time')

# Customize the graph
plt.xlabel('Number of Mapping links')
plt.ylabel('Metrics')
plt.title('Evolution of Metrics with respect to Number Mapping links')
plt.legend()
plt.savefig('AnalysisMapping')

# Show the graph
plt.show()

# Create the graph
plt.figure(figsize=(10, 6))
#plt.plot(questions, c_pairs, label='Connected Pairs')
#plt.plot(questions, mutants, label='Mutants')
#plt.plot(questions, questions, label='Questions')
plt.plot(questions, time, label='Time')

# Customize the graph
plt.xlabel('Number of Questions')
plt.ylabel('Time[ms]')
plt.title('Evolution of Time with respect to Number Questions')
plt.legend()
plt.savefig('AnalysisMutant')

# Show the graph
plt.show()