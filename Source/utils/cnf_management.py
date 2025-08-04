from pysat.solvers import Glucose3
from pysat.card import CardEnc, EncType
from pysat.pb import PBEnc
from pysat.formula import CNF, IDPool  
class HashiCNFManager:
    """
    Manages CNF clauses and variables for Hashiwokakero puzzle using IDPool
    """
    
    def __init__(self, grid, islands, bridges, crossing_bridges):
        """
        Initialize the CNF manager with puzzle data
        
        Args:
            grid: 2D grid of the puzzle
            islands: Dictionary of island_id -> (row, col, val)
            bridges: Dictionary of bridge_id -> (island_a, island_b, direction)
            crossing_bridges: List of (bridge_id1, bridge_id2) that cross
        """
        self.grid = grid
        self.islands = islands
        self.bridges = bridges
        self.crossing_bridges = crossing_bridges
        
        # Initialize CNF and variable pool
        self.cnf = CNF()
        self.vpool = IDPool()  #  Khởi tạo riêng IDPool
        
        # Variable mappings
        self.bridge_vars = {}  # (bridge_id, bridge_type) -> variable_id
        self.flow_vars = {}    # (island_from, island_to) -> variable_id
        
        # Initialize variables
        self._create_variables()
        
        # Add constraints
        self._add_bridge_capacity_constraints()
        self._add_island_value_constraints()
        self._add_no_crossing_constraints()
        self._add_connectivity_constraints()
    
    def _create_variables(self):
        """Create all necessary variables for the puzzle"""

        # Bridge variables: for each possible bridge, create variables for single and double bridges
        for bridge_id in self.bridges:
            self.bridge_vars[(bridge_id, 1)] = self.vpool.id(f'bridge_{bridge_id}_single')
            self.bridge_vars[(bridge_id, 2)] = self.vpool.id(f'bridge_{bridge_id}_double')
        
        # Flow variables: for connectivity constraint
        # Only create flow variables between islands that have possible bridges
        island_pairs = set()
        for bridge_id, (island_a, island_b, _) in self.bridges.items():
            island_pairs.add((island_a, island_b))
            island_pairs.add((island_b, island_a))  # Both directions
        
        for island_from, island_to in island_pairs:
            self.flow_vars[(island_from, island_to)] = self.vpool.id(f'flow_{island_from}_{island_to}')
    
    def _add_bridge_capacity_constraints(self):
        """Add constraints: at most one type of bridge (single OR double) per bridge location"""
        for bridge_id in self.bridges:
            single_var = self.bridge_vars[(bridge_id, 1)]
            double_var = self.bridge_vars[(bridge_id, 2)]
            
            # At most one of single or double bridge can be true
            self.cnf.append([-single_var, -double_var])
    
    def _add_island_value_constraints(self, use_cardinality=True):
        """
        Add constraints: number of bridges connecting to each island equals its value
        
        Args:
            use_cardinality (bool): If True, use CardEnc.equals; if False, use manual clauses
        """
        if use_cardinality:
            self._add_island_value_constraints_v1()
        else:
            self._add_island_value_constraints_v2()
    
    def _add_island_value_constraints_v1(self):
        """Version 1: Use Pseudo-Boolean constraints (PBEnc.equals)"""
        for island_id, (row, col, island_value) in self.islands.items():
            # Find all bridges connected to this island
            bridge_literals = []
            bridge_weights = []
            
            for bridge_id, (island_a, island_b, direction) in self.bridges.items():
                if island_a == island_id or island_b == island_id:
                    # This bridge connects to our island
                    single_var = self.bridge_vars[(bridge_id, 1)]
                    double_var = self.bridge_vars[(bridge_id, 2)]
                    
                    # Single bridge has weight 1
                    bridge_literals.append(single_var)
                    bridge_weights.append(1)
                    
                    # Double bridge has weight 2
                    bridge_literals.append(double_var)
                    bridge_weights.append(2)
            
            # Use pseudo-boolean constraint: sum of weights equals island_value
            if bridge_literals:
                pb_clauses = PBEnc.equals(
                    lits=bridge_literals,
                    weights=bridge_weights,
                    bound=island_value,
                    vpool=self.vpool,
                    encoding=EncType.seqcounter
                )
                self.cnf.extend(pb_clauses.clauses)
    
    def _add_island_value_constraints_v2(self):
        """Version 2: Manually implement with clauses"""
        # TODO: Implement flow-based connectivity
        pass
    
    def _add_no_crossing_constraints(self):
        """Add constraints: no two bridges can cross each other"""
        for bridge_id1, bridge_id2 in self.crossing_bridges:
            # If bridge1 exists (single or double), then bridge2 cannot exist
            single_var1 = self.bridge_vars[(bridge_id1, 1)]
            double_var1 = self.bridge_vars[(bridge_id1, 2)]
            single_var2 = self.bridge_vars[(bridge_id2, 1)]
            double_var2 = self.bridge_vars[(bridge_id2, 2)]
            
            # Not (bridge1_single OR bridge1_double) OR Not (bridge2_single OR bridge2_double)
            # Which is equivalent to: NOT both bridges can exist simultaneously
            self.cnf.append([-single_var1, -single_var2])
            self.cnf.append([-single_var1, -double_var2])
            self.cnf.append([-double_var1, -single_var2])
            self.cnf.append([-double_var1, -double_var2])
    
    def _add_connectivity_constraints(self):
        """Add flow-based connectivity constraints"""
        if len(self.islands) <= 1:
            return  # No connectivity needed for 0 or 1 islands
        
        root_island = 0  # Select first island as root
        total_islands = len(self.islands)
        
        # 1. Flow only allowed on active bridges
        self._add_flow_bridge_constraints()
        
        # 2. Flow direction restriction (only one direction per bridge)
        self._add_flow_direction_constraints()
        
        # 3. Flow balance constraints
        self._add_flow_balance_constraints(root_island, total_islands)
    
    def _add_flow_bridge_constraints(self):
        """Flow is only allowed on active bridges (single or double)"""
        for bridge_id, (island_a, island_b, direction) in self.bridges.items():
            single_var = self.bridge_vars[(bridge_id, 1)]
            double_var = self.bridge_vars[(bridge_id, 2)]
            
            # Flow variables for both directions
            flow_a_to_b = self.flow_vars[(island_a, island_b)]
            flow_b_to_a = self.flow_vars[(island_b, island_a)]
            
            # If no bridge exists, then no flow is allowed in either direction
            # (single_var OR double_var) OR NOT(flow_a_to_b OR flow_b_to_a)
            # Equivalent to: NOT(flow_a_to_b) AND NOT(flow_b_to_a) OR (single_var OR double_var)
            
            # flow_a_to_b -> (single_var OR double_var)
            self.cnf.append([-flow_a_to_b, single_var, double_var])
            
            # flow_b_to_a -> (single_var OR double_var)  
            self.cnf.append([-flow_b_to_a, single_var, double_var])
    
    def _add_flow_direction_constraints(self):
        """Ensure flow goes in only one direction per bridge"""
        for bridge_id, (island_a, island_b, direction) in self.bridges.items():
            flow_a_to_b = self.flow_vars[(island_a, island_b)]
            flow_b_to_a = self.flow_vars[(island_b, island_a)]
            
            # At most one direction: NOT(flow_a_to_b AND flow_b_to_a)
            self.cnf.append([-flow_a_to_b, -flow_b_to_a])
    
    def _add_flow_balance_constraints(self, root_island, total_islands):
        """Add flow balance constraints for connectivity"""
        all_non_root_inflow_vars = []
        
        # For each island, add appropriate constraints
        for island_id in self.islands:
            if island_id == root_island:
                continue  # Skip root island for individual constraints
            
            # Find inflow variables for this non-root island
            inflow_vars = []
            for (island_from, island_to), flow_var in self.flow_vars.items():
                if island_to == island_id:
                    inflow_vars.append(flow_var)
                    all_non_root_inflow_vars.append(flow_var)
            
            # Individual constraint: each non-root island receives exactly 1 unit of inflow
            if inflow_vars:
                card_clauses = CardEnc.equals(
                    lits=inflow_vars,
                    bound=1,
                    vpool=self.vpool,
                    encoding=EncType.seqcounter
                )
                self.cnf.extend(card_clauses.clauses)
        
        # Global constraint: sum of all inflow to non-root islands = total_islands - 1
        if all_non_root_inflow_vars:
            card_clauses = CardEnc.equals(
                    lits=all_non_root_inflow_vars,
                    bound=total_islands - 1,
                    vpool=self.vpool,
                    encoding=EncType.seqcounter
            )
            self.cnf.extend(card_clauses.clauses)

    def extract_cnf(self):
        """Extract formulated CNF from Hashi rules"""
        return self.cnf
    
    def solve(self):
        """
        Solve the CNF and return the solution
        
        Returns:
            dict or None: Dictionary of bridge solutions or None if unsatisfiable
        """
        solver = Glucose3()
        solver.append_formula(self.cnf)
        
        if solver.solve():
            model = solver.get_model()
            return self._extract_solution(model)
        else:
            return None
    
    def _extract_solution(self, model):
        """Extract bridge solution from SAT model"""
        solution = {}
        
        for bridge_id in self.bridges:
            single_var = self.bridge_vars[(bridge_id, 1)]
            double_var = self.bridge_vars[(bridge_id, 2)]
            
            if single_var in model:
                solution[bridge_id] = 1
            elif double_var in model:
                solution[bridge_id] = 2
            else:
                solution[bridge_id] = 0  # No bridge
        
        return solution
    
    def get_statistics(self):
        """Return statistics about the CNF"""
        return {
            'variables': self.vpool.top,
            'clauses': len(self.cnf.clauses),
            'islands': len(self.islands),
            'possible_bridges': len(self.bridges),
            'crossing_pairs': len(self.crossing_bridges),
            'islands_raw': self.islands,
            'bridges_raw': self.bridges,
            'crossings_raw': self.crossing_bridges
          

        }