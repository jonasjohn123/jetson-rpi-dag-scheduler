import yaml
import networkx as nx


def load_dag(dag_file):
    """
    Load a DAG from YAML and return a NetworkX DiGraph.

    Args:
        dag_file (str)

    Returns:
        nx.DiGraph
    """

    with open(dag_file, "r") as f:
        dag_data = yaml.safe_load(f)

    graph = nx.DiGraph()

    for node_id, node_info in dag_data["nodes"].items():

        graph.add_node(
            node_id,
            task_type=node_info["task_type"]
        )

    for src, dst in dag_data["edges"]:

        graph.add_edge(
            src,
            dst
        )

    if not nx.is_directed_acyclic_graph(graph):

        raise ValueError(
            "Input graph is not a DAG."
        )

    return graph