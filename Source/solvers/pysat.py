from pysat.solvers import Glucose3

def solve(cnf):
    solver = Glucose3()
    solver.append_formula(cnf.clauses)
    
    if solver.solve():
        model = solver.get_model()  
        solver.delete()
        return model
    else:
        solver.delete()
        return None