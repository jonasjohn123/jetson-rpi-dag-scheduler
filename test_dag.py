from scheduler.dag_loader import load_dag

G = load_dag(
    "dags/test_dag.yaml"
)

print("Nodes:")
print(G.nodes(data=True))

print()

print("Edges:")
print(list(G.edges()))

print()

print("Successors of n1:")
print(list(G.successors("n1")))

print()

print("Predecessors of n2:")
print(list(G.predecessors("n2")))

print()

print("Entry Nodes:")

print(
    [
        node
        for node in G.nodes
        if G.in_degree(node) == 0
    ]
)

print()

print("Exit Nodes:")

print(
    [
        node
        for node in G.nodes
        if G.out_degree(node) == 0
    ]
)