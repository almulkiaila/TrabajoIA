from water_sort_solver import WaterSortGame, SearchAlgorithm
import numpy as np

def main():
    print("\n=== Water Sort Puzzle Solver ===\n")

    while True:
        num_tubes = int(input("Número de tubos (5–12): "))
        if 5 <= num_tubes <= 12:
            break
        print(" Debe estar entre 5 y 12.")

    while True:
        num_colors = int(input(f"Número de colores: "))
        if 3 <= num_colors <= num_tubes - 2:
            break
        print(f" Debe estar entre 3 y {num_tubes - 2}.")

    seed = int(input("Semilla para reproducibilidad: "))

    print("\nAlgoritmos disponibles:")
    print("  1. BFS")
    print("  2. DFS")
    print("  3. A*")
    print("  4. DLS (profundidad limitada)")
    print("  5. IDA* (Iterative Deepening A*)")
    opt_alg = input("Selecciona algoritmo (1–5): ")

    algorithm = None
    heuristic = None
    depth_limit = None

    if opt_alg == "1":
        algorithm = "bfs"
    elif opt_alg == "2":
        algorithm = "dfs"
    elif opt_alg == "3":
        algorithm = "a*"
        print("\nHeurísticas disponibles:")
        print("  1. h1 (dispersión de colores)")
        print("  2. h2 (colores bien colocados)")
        print("  3. h3 (mezcla y bloqueo)")
        opt_h = input("Selecciona heurística (1–3): ")
        heuristic = opt_h
    elif opt_alg == "4":
        algorithm = "dls"
        depth_limit = int(input("Introduce el límite de profundidad: "))
    elif opt_alg == "5":
        algorithm = "ida*"
        print("\nHeurísticas disponibles:")
        print("  1. h1 (dispersión de colores)")
        print("  2. h2 (colores bien colocados)")
        print("  3. h3 (mezcla y bloqueo)")
        opt_h = input("Selecciona heurística (1–3): ")
        heuristic = opt_h
    else:
        print("Opción no válida. Usando BFS por defecto.")
        algorithm = "bfs"

    print("\nModo de ejecución:")
    print("  1. Automático")
    print("  2. Paso a paso")
    opt_mode = input("Selecciona modo (1–2): ")
    step_mode = (opt_mode == "2")

    # --- Inicialización del juego ---
    game = WaterSortGame(num_tubes, num_colors, seed)
    solver = SearchAlgorithm(game)

    print("\n=== Estado inicial ===")
    for i, row in enumerate(game.initial_state):
        print(f"Tubo {i}: {row.tolist()}")

    # --- Ejecución del algoritmo ---
    if algorithm == "bfs":
        path, stats = solver.bfs(game.initial_state)
    elif algorithm == "dfs":
        path, stats = solver.dfs(game.initial_state)
    elif algorithm == "a*":
        if heuristic == "1":
            path, stats = solver.a_star(game.initial_state, solver.h1)
        elif heuristic == "2":
            path, stats = solver.a_star(game.initial_state, solver.h2)
        elif heuristic == "3":
            path, stats = solver.a_star(game.initial_state, solver.h3)
        else:
            print("Heurística no válida. Usando h1 por defecto.")
            path, stats = solver.a_star(game.initial_state, solver.h1)
    elif algorithm == "dls":
        path, stats = solver.dls(game.initial_state, depth_limit)
    elif algorithm == "ida*":
        if heuristic == "1":
            path, stats = solver.ida_star(game.initial_state, solver.h1)
        elif heuristic == "2":
            path, stats = solver.ida_star(game.initial_state, solver.h2)
        elif heuristic == "3":
            path, stats = solver.ida_star(game.initial_state, solver.h3)
        else:
            print("Heurística no válida. Usando h1 por defecto.")
            path, stats = solver.ida_star(game.initial_state, solver.h1)

    # --- Resultados ---
    print("\n=== RESULTADOS ===")
    if path is None:
        print("No se encontró solución (o se alcanzó el límite de profundidad).")
        return
    else:
        print(f"Se encontró solución en {len(path)} movimientos.")
        moves_str = ", ".join([f"({i}->{j})" for i, j in path])
        print(f"Movimientos: {moves_str}")

    # --- Modo paso a paso o automático ---
    cur_state = np.copy(game.initial_state)
    for idx, (i, j) in enumerate(path, 1):
        cur_state = game.apply_move(cur_state, (i, j))
        if step_mode:
            print(f"\nMovimiento {idx}: {i} → {j}")
            for t, row in enumerate(cur_state):
                print(f"Tubo {t}: {row.tolist()}")
            input("Presiona Enter para continuar...")

    if not step_mode:
        print("\n=== Estado final ===")
        for i, row in enumerate(cur_state):
            print(f"Tubo {i}: {row.tolist()}")

    # --- Estadísticas ---
    print("\n=== Estadísticas ===")
    for k, v in stats.items():
        print(f"{k}: {v}")

# Solo se ejecuta el main si corres este archivo directamente
if __name__ == "__main__":
    main()
