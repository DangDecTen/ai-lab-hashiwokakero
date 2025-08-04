import time
import tracemalloc
from utils.text_renderer import render_text

def decode_model(model, bridge_var_map):
    if model is None:
        return {}

    # attempting to flatten more
    def flatten(x):
        if isinstance(x, list):
            for item in x:
                yield from flatten(item)
        else:
            yield x

    solution = {}
    for lit in flatten(model):
        if isinstance(lit, int) and lit > 0 and lit in bridge_var_map:
            bridge_id, count = bridge_var_map[lit]
            solution[bridge_id] = count
    return solution

def run_with_metrics(solver_fn, cnf, hashi = None):
    start = time.time()
    tracemalloc.start()

    solution = solver_fn(cnf, hashi)

    mem_now, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    end = time.time()

    return {
        "solution": solution,
        "time": end - start,
        "memory_kb": mem_peak // 1024
    }

def show_result(name, result, grid, hashi, bridge_var_map=None):
    if result["solution"] is None:
        print(f"{name}: No solution found")
    else:
        print(f"{name}: Found solution in {result['time']:.3f}s, {result['memory_kb']}KB used")

        model = result["solution"]
        # flatten if needed
        if isinstance(model, list) and len(model) == 1 and isinstance(model[0], list):
            model = model[0]

        bridge_solution = decode_model(model, bridge_var_map)
        print(render_text(grid, hashi.islands, hashi.bridges, bridge_solution))
        print()