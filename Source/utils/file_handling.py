def read_file(path):
    grid = []
    with open(path, 'r') as file:
        for line in file:
            row = [int(s.strip()) for s in line.split(',')]
            grid.append(row)
    
    return grid