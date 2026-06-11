from scheduler.cost_model import (
    get_edge_data_size_mb,
    get_avg_comm_cost
)

print(
    get_edge_data_size_mb(
        "capture",
        "preprocess"
    )
)

print(
    get_avg_comm_cost(
        "capture",
        "preprocess"
    )
)