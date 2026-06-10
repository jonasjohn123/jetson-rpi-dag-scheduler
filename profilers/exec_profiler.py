import subprocess, time, psutil, json

def profile_task(cmd, runs=5, workdir="."):
	"""Run cmd N times and return mean/min/max execution time in ms."""
	samples = []
	for _ in range(runs):
		start = time.perf_counter()
		subprocess.run(cmd, shell=True, cwd=workdir,
					   check=True, capture_output=True)
		elapsed_ms = (time.perf_counter() - start) * 1000.0
		proc = psutil.Process()
		samples.append({
			"exec_ms": round(elapsed_ms, 2),
			"cpu_pct": psutil.cpu_percent(interval=0.1),
			"mem_mb": proc.memory_info().rss / 1e6,
		})
	exec_times = [s["exec_ms"] for s in samples]
	return {
		"mean_ms": round(sum(exec_times) / runs, 2),
		"min_ms": round(min(exec_times), 2),
		"max_ms": round(max(exec_times), 2),
		"samples": samples,
	}