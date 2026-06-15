import yaml


def get_worker_id():

    with open(
        "configs/local_worker.yaml",
        "r"
    ) as f:

        config = yaml.safe_load(f)

    return config["worker_id"]