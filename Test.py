import time
import pandas as pd
from tqdm import tqdm
from water_sort_solver import WaterSortGame, SearchAlgorithm
import os

# ===== CONFIGURACIÓN =====
num_tubes_range = range(5, 13)   # tubos de 5 a 12
seeds = range(10)                # 10 semillas
algoritmos = ["BFS", "DFS", "A*_h1", "A*_h2", "A*_h3"]
OUTPUT_FILE = "resultados_pruebas.csv"

def ejecutar_algoritmo(game, solver, initial_state, algoritmo):
    start = time.time()
    try:
        if algoritmo == "BFS":
            path, stats = solver.bfs(initial_state)
        elif algoritmo == "DFS":
            path, stats = solver.dfs(initial_state)
        elif algoritmo == "A*_h1":
            path, stats = solver.a_star(initial_state, solver.h1)
        elif algoritmo == "A*_h2":
            path, stats = solver.a_star(initial_state, solver.h2)
        elif algoritmo == "A*_h3":
            path, stats = solver.a_star(initial_state, solver.h3)
        else:
            raise ValueError(f"Algoritmo no reconocido: {algoritmo}")

        elapsed = time.time() - start
        stats["tiempo_total"] = elapsed
        stats["solved"] = stats["profundidad_solucion"] is not None
        stats["error"] = ""
        return stats

    except Exception as e:
        elapsed = time.time() - start
        return {
            "nodos_expandidos": None,
            "nodos_en_memoria_max": None,
            "tiempo_seg": None,
            "tiempo_total": elapsed,
            "profundidad_solucion": None,
            "solved": False,
            "error": str(e)
        }

# ===== CARGA DE CSV EXISTENTE (para reanudar) =====
if os.path.exists(OUTPUT_FILE):
    df_existente = pd.read_csv(OUTPUT_FILE)
    print(f"📂 Reanudando desde '{OUTPUT_FILE}' con {len(df_existente)} resultados previos.")
    resultados_guardados = set(
        tuple(row) for row in df_existente[["num_tubes", "num_colors", "seed", "algoritmo"]].values
    )
else:
    df_existente = pd.DataFrame()
    resultados_guardados = set()

# ===== BUCLE PRINCIPAL =====
total_experimentos = sum(
    (num_tubes - 3) * len(seeds) * len(algoritmos) for num_tubes in num_tubes_range
)
print(f"\n🚀 Iniciando {total_experimentos} pruebas...\n")

# Progreso global
for num_tubes in tqdm(num_tubes_range, desc="🔹 Progreso general", position=0):
    for num_colors in range(3, num_tubes - 1):  # regla: colores <= tubos - 2
        for seed in seeds:
            game = WaterSortGame(num_tubes, num_colors, seed)
            solver = SearchAlgorithm(game)
            init_state = game.initial_state

            print(f"\n🧪 {num_tubes} tubos, {num_colors} colores, semilla {seed}:")

            # Progreso interno por algoritmo
            for algoritmo in tqdm(algoritmos, desc=f"  Algoritmos", position=1, leave=False):
                clave = (num_tubes, num_colors, seed, algoritmo)

                if clave in resultados_guardados:
                    # Ya estaba en el CSV
                    continue

                stats = ejecutar_algoritmo(game, solver, init_state, algoritmo)

                # Guardamos una fila en el CSV inmediatamente
                nueva_fila = {
                    "num_tubes": num_tubes,
                    "num_colors": num_colors,
                    "seed": seed,
                    "algoritmo": algoritmo,
                    "nodos_expandidos": stats.get("nodos_expandidos"),
                    "nodos_en_memoria_max": stats.get("nodos_en_memoria_max"),
                    "tiempo_seg": stats.get("tiempo_seg"),
                    "tiempo_total": stats.get("tiempo_total"),
                    "profundidad_solucion": stats.get("profundidad_solucion"),
                    "solved": stats.get("solved"),
                    "error": stats.get("error", "")
                }

                pd.DataFrame([nueva_fila]).to_csv(
                    OUTPUT_FILE, mode='a', header=not os.path.exists(OUTPUT_FILE), index=False
                )

                resultados_guardados.add(clave)

            print(f"✅ Completadas todas las pruebas para semilla {seed}.\n")

print(f"\n✅ Resultados guardados y actualizados en '{OUTPUT_FILE}'")
