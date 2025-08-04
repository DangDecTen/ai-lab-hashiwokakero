import heapq
from itertools import count
from pysat.formula import CNF
from pysat.solvers import Glucose3

def solve_astar(cnf: CNF, hashi):
    all_vars = sorted(set(abs(lit) for clause in cnf.clauses for lit in clause))
    var_count = len(all_vars)
    counter = count()

    def heuristic(assign):
        return var_count - len(assign)

    def encode_state(assign_dict):
        return [[v if val else -v] for v, val in assign_dict.items()]

    frontier = []
    init_state = {}
    g = 0
    h = heuristic(init_state)
    f = g + h
    heapq.heappush(frontier, (f, next(counter), init_state))

    while frontier:
        _, _, current = heapq.heappop(frontier)

        solver = Glucose3()
        solver.append_formula(cnf.clauses)
        solver.append_formula(encode_state(current))

        if solver.solve():
            model = solver.get_model()
            return model

        assigned = set(current.keys())
        for v in all_vars:
            if v in assigned:
                continue

            for val in [True, False]:
                new_state = current.copy()
                new_state[v] = val
                g = len(new_state)
                h = heuristic(new_state)
                heapq.heappush(frontier, (g + h, next(counter), new_state))

    return None