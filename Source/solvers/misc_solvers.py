from itertools import product
from pysat.solvers import Glucose3

def solve_brute_force(cnf, hashi):
    bridge_vars = list(hashi.bridge_vars.values())
    for assignment in product([1, -1], repeat=len(bridge_vars)):
        solver = Glucose3()
        solver.append_formula(cnf.clauses)
        assumptions = [var if val > 0 else -var for var, val in zip(bridge_vars, assignment)]
        if solver.solve(assumptions=assumptions):
            return solver.get_model()
    return None

def solve_backtracking(cnf, hashi):
    bridge_vars = list(hashi.bridge_vars.values())

    def backtrack(index, assignment):
        if index == len(bridge_vars):
            assumptions = [lit for lit in assignment if lit != 0]
            with Glucose3(bootstrap_with=cnf.clauses) as solver:
                if solver.solve(assumptions=assumptions):
                    return assumptions
            return None

        var = bridge_vars[index]
        # try assigning true
        result = backtrack(index + 1, assignment + [var])
        if result:
            return result
        # Try assigning false
        result = backtrack(index + 1, assignment + [-var])
        if result:
            return result
        return None

    return backtrack(0, [])