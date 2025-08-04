import os
import argparse
from utils import (
    cnf_generation,
    file_handling,
)
from utils.cnf_management import HashiCNFManager
from utils.text_renderer import render_text
from solvers import (
    pysat
)
from solvers.a_star import solve_astar
from solvers.misc_solvers import solve_brute_force, solve_backtracking
from utils.performance_measure import run_with_metrics, show_result

INPATH = "./Source/Inputs"
OUTPATH = "./Source/Outputs"

def main():
    parser = argparse.ArgumentParser(description="Hashiwokakero Solver")
    parser.add_argument("input_file", type=str, help="Input file name (e.g. 'input-01.txt')")
    parser.add_argument(
        "--algorithm",
        "-a",
        type=str,
        choices=["pysat", "astar", "brute", "backtracking"],
        default="pysat",
        help="Algorithm to use: sat (default), astar, brute, backtracking",
    )
    args = parser.parse_args()

    in_file = os.path.join(INPATH, args.input_file)
    out_file = os.path.join(OUTPATH, f"output_{args.algorithm}_{args.input_file.lstrip('input')}")

    # Read file
    grid = file_handling.read_file(in_file)

    # Generate CNF & Statistics
    cnf, stats, hashi = cnf_generation.generate(grid)
    print("CNF Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Call solver
    if args.algorithm == "pysat":
        model = pysat.solve(cnf)
        if model is None:
            print("No solution found.")
            return
        bridge_solution = hashi._extract_solution(model)
        text_output = render_text(grid, hashi.islands, hashi.bridges, bridge_solution)
        output_txt_path = os.path.join(OUTPATH, f"text_output_{args.input_file}")
        with open(output_txt_path, "w") as f:
            f.write(text_output)
        print("\nSolution found!")
            
    elif args.algorithm == "astar":
        astar_model = run_with_metrics(solve_astar, cnf, hashi)
        if astar_model is None:
            print("No solution found.")
            return
        bridge_var_map = {}
        for key, var in hashi.bridge_vars.items():
            bridge_var_map[var] = key
        show_result("A*", astar_model, grid, hashi, bridge_var_map)
        print("\nSolution found!")
        
        
    elif args.algorithm == "brute":
        brute_force_model = run_with_metrics(solve_brute_force, cnf, hashi)
        if brute_force_model is None:
            print("No solution found.")
            return
        bridge_var_map = {}
        for key, var in hashi.bridge_vars.items():
            bridge_var_map[var] = key
        show_result("Brute Force", brute_force_model, grid, hashi, bridge_var_map)
        print("\nSolution found!")
            
    elif args.algorithm == "backtracking":
        backtracking_model = run_with_metrics(solve_backtracking, cnf, hashi)
        if backtracking_model is None:
            print("No solution found.")
            return
        bridge_var_map = {}
        for key, var in hashi.bridge_vars.items():
            bridge_var_map[var] = key
        show_result("Backtracking", backtracking_model, grid, hashi, bridge_var_map)
        print("\nSolution found!")
        
    else:
        raise ValueError(f"Unsupported algorithm: {args.algorithm}")

if __name__ == "__main__":
    main()