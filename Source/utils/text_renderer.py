def render_text(grid, islands, bridges, bridge_solution):
    rows, cols = len(grid), len(grid[0])
    canvas = [['.' for _ in range(cols)] for _ in range(rows)]

    # Đặt đảo
    for (id, (r, c, val)) in islands.items():
        canvas[r][c] = str(val)

    # Đặt cầu
    for bridge_id, count in bridge_solution.items():
        if count == 0:
            continue
        (a, b, direction) = bridges[bridge_id]
        r1, c1, _ = islands[a]
        r2, c2, _ = islands[b]

        if direction == 'E':
            for x in range(min(c1, c2) + 1, max(c1, c2)):
                canvas[r1][x] = '-' if count == 1 else '='
        elif direction == 'S':
            for y in range(min(r1, r2) + 1, max(r1, r2)):
                canvas[y][c1] = '|' if count == 1 else '‖'

    return "\n".join("".join(row) for row in canvas)
