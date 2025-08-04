from utils.cnf_management import HashiCNFManager

def find_islands(grid):
    islands = {}
    island_index = 0

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] != 0:
                islands[island_index] = (i, j, grid[i][j])  # (row, col, val)
                island_index += 1
    
    return islands

def find_bridges(grid, islands):
    bridges = {}
    bridge_index = 0
    
    # Create a mapping from coordinates to island IDs for quick lookup
    coord_to_island = {}
    for island_id, (x, y, val) in islands.items():
        coord_to_island[(x, y)] = island_id
    
    # Check all pairs of islands
    for id_a in islands:
        i_a, j_a, _ = islands[id_a]
        
        for id_b in islands:
            if id_a >= id_b:  # Only process each pair once, avoid duplicates
                continue
                
            i_b, j_b, _ = islands[id_b]
            
            # Check if islands are in the same row (horizontal connection)
            if i_a == i_b and j_a != j_b:
                # Ensure no islands between them
                min_j, max_j = min(j_a, j_b), max(j_a, j_b)
                path_clear = True
                
                for j in range(min_j + 1, max_j):
                    if grid[i_a][j] != 0:  # There's an island blocking the path
                        path_clear = False
                        break
                
                if path_clear:
                    # Determine direction from a to b
                    direction = 'E' if j_b > j_a else 'W'
                    bridges[bridge_index] = (id_a, id_b, direction)
                    bridge_index += 1
            
            # Check if islands are in the same column (vertical connection)
            elif j_a == j_b and i_a != i_b:
                # Ensure no islands between them
                min_i, max_i = min(i_a, i_b), max(i_a, i_b)
                path_clear = True
                
                for i in range(min_i + 1, max_i):
                    if grid[i][j_a] != 0:  # There's an island blocking the path
                        path_clear = False
                        break
                
                if path_clear:
                    # Determine direction from a to b
                    direction = 'S' if i_b > i_a else 'N'
                    bridges[bridge_index] = (id_a, id_b, direction)
                    bridge_index += 1
    
    return bridges

def find_crossing_bridges(bridges, islands):
    crossing_pairs = []
    bridge_ids = list(bridges.keys())
    
    for i in range(len(bridge_ids)):
        for j in range(i + 1, len(bridge_ids)):
            bridge_id1 = bridge_ids[i]
            bridge_id2 = bridge_ids[j]
            
            # Get bridge information
            island_a1, island_b1, dir1 = bridges[bridge_id1]
            island_a2, island_b2, dir2 = bridges[bridge_id2]
            
            # Get island coordinates
            row_a1, col_a1, _ = islands[island_a1]
            row_b1, col_b1, _ = islands[island_b1]
            row_a2, col_a2, _ = islands[island_a2]
            row_b2, col_b2, _ = islands[island_b2]
            
            # Check if bridges are perpendicular (one horizontal, one vertical)
            bridge1_horizontal = dir1 in ['E', 'W']
            bridge2_horizontal = dir2 in ['E', 'W']
            
            if bridge1_horizontal == bridge2_horizontal:
                continue  # Both horizontal or both vertical, can't cross
            
            # Determine which bridge is horizontal and which is vertical
            if bridge1_horizontal:
                # Bridge 1 is horizontal, Bridge 2 is vertical
                h_row = row_a1  # Same row for horizontal bridge
                h_col_min, h_col_max = min(col_a1, col_b1), max(col_a1, col_b1)
                
                v_col = col_a2  # Same column for vertical bridge
                v_row_min, v_row_max = min(row_a2, row_b2), max(row_a2, row_b2)
            else:
                # Bridge 2 is horizontal, Bridge 1 is vertical
                h_row = row_a2  # Same row for horizontal bridge
                h_col_min, h_col_max = min(col_a2, col_b2), max(col_a2, col_b2)
                
                v_col = col_a1  # Same column for vertical bridge
                v_row_min, v_row_max = min(row_a1, row_b1), max(row_a1, row_b1)
            
            # Check if bridges cross
            # They cross if the intersection point is within both ranges
            if (h_col_min < v_col < h_col_max and 
                v_row_min < h_row < v_row_max):
                crossing_pairs.append((bridge_id1, bridge_id2))
    
    return crossing_pairs

def generate(grid):
    islands = find_islands(grid)
    bridges = find_bridges(grid, islands)
    crossing_bridges = find_crossing_bridges(bridges, islands)
    
    hashi = HashiCNFManager(grid, islands, bridges, crossing_bridges)
    
    return hashi.extract_cnf(), hashi.get_statistics(), hashi
