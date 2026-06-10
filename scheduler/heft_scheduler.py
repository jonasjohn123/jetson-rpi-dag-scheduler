"""Simple HEFT scheduler utilities.

This module provides helpers to load cost/profile tables, build a DAG
from YAML, compute upward ranks (HEFT) and produce a mapping using
the earliest-finish-time processor selection.
"""

import json
from typing import Dict, Tuple, List

import yaml
import networkx as nx


def load_costs(profile_file: str):
	"""Load workers, execution cost and communication cost tables.

	Expected YAML structure:
	  workers: [w1, w2, ...]
	  exec_cost:
		task1: {w1: 10.0, w2: 12.0}
	  comm_cost:
		w1: {w2: 1.0}
	"""
	with open(profile_file) as f:
		data = yaml.safe_load(f)
	return data["workers"], data["exec_cost"], data.get("comm_cost", {})


def load_dag(dag_file: str) -> nx.DiGraph:
	"""Build a NetworkX DiGraph from a YAML task/edge description."""
	with open(dag_file) as f:
		data = yaml.safe_load(f)
	G = nx.DiGraph()
	G.add_nodes_from(data.get("tasks", []))
	for edge in data.get("edges", []):
		if len(edge) != 2:
			raise ValueError("Edges must be pairs: (src, dst)")
		src, dst = edge
		G.add_edge(src, dst)
	if not nx.is_directed_acyclic_graph(G):
		raise ValueError("Provided graph is not a DAG")
	return G


def compute_ranks(G: nx.DiGraph, exec_cost: Dict, comm_cost: Dict, workers: List) -> Dict:
	"""Compute upward ranks for all tasks (HEFT)."""
	n_workers = len(workers)
	# average execution cost per task across workers
	avg_exec = {t: sum(exec_cost[t][w] for w in workers) / n_workers for t in G.nodes}

	# average communication cost for each edge (assume comm_cost[w1][w2])
	avg_comm = {}
	for u, v in G.edges:
		costs = [
			comm_cost.get(w1, {}).get(w2, 0.0)
			for w1 in workers
			for w2 in workers
			if w1 != w2
		]
		avg_comm[(u, v)] = sum(costs) / max(1, len(costs))

	rank = {}

	def upward_rank(task):
		if task in rank:
			return rank[task]
		succs = list(G.successors(task))
		if not succs:
			rank[task] = avg_exec[task]
		else:
			rank[task] = avg_exec[task] + max(
				avg_comm.get((task, s), 0.0) + upward_rank(s) for s in succs
			)
		return rank[task]

	for t in G.nodes:
		upward_rank(t)
	return rank


def schedule_heft(G: nx.DiGraph, workers: List, exec_cost: Dict, comm_cost: Dict, rank: Dict) -> Tuple[Dict, float]:
	"""Schedule tasks using HEFT priority and EFT processor selection.

	Returns a schedule dict and the makespan (ms).
	"""
	priority_order = sorted(rank.keys(), key=rank.get, reverse=True)
	worker_avail = {w: 0.0 for w in workers}
	task_result: Dict[str, Tuple[str, float, float]] = {}

	for task in priority_order:
		best = None
		for w in workers:
			# data ready time: max over parents of (parent_finish + comm if different worker)
			ready = 0.0
			for parent in G.predecessors(task):
				if parent not in task_result:
					raise RuntimeError(f"Parent task '{parent}' not scheduled before '{task}'")
				pw, _, pf = task_result[parent]
				c = 0.0 if pw == w else comm_cost.get(pw, {}).get(w, 0.0)
				ready = max(ready, pf + c)

			start = max(ready, worker_avail[w])
			finish = start + exec_cost[task][w]
			if best is None or finish < best["finish"]:
				best = {"worker": w, "start": start, "finish": finish}

		bw, bs, bf = best["worker"], best["start"], best["finish"]
		worker_avail[bw] = bf
		task_result[task] = (bw, bs, bf)

	schedule = {
		t: {"worker": r[0], "start_ms": round(r[1], 2), "finish_ms": round(r[2], 2)}
		for t, r in task_result.items()
	}
	makespan = max(v["finish_ms"] for v in schedule.values()) if schedule else 0.0
	return schedule, round(makespan, 2)


if __name__ == "__main__":
	import sys

	dag_file = sys.argv[1] if len(sys.argv) > 1 else "dags/vision_pipeline.yaml"
	profile_file = sys.argv[2] if len(sys.argv) > 2 else "configs/profiles.yaml"

	workers, exec_cost, comm_cost = load_costs(profile_file)
	G = load_dag(dag_file)
	rank = compute_ranks(G, exec_cost, comm_cost, workers)
	schedule, makespan = schedule_heft(G, workers, exec_cost, comm_cost, rank)
	print(f"Makespan: {makespan} ms")
	with open("results/mapping.json", "w") as f:
		json.dump({"makespan_ms": makespan, "schedule": schedule}, f, indent=2)