import time
import matplotlib.pyplot as plt
import pandas as pd
import itertools
from water_sort_solver import WaterSortGame
from water_sort_solver import SearchAlgorithm


def run_experiments():
    results = []

    n_configs = [
        (6, 3),  
        (8, 4), 
        (10, 5)  
    ]
    seeds = [0, 42, 78]

    algorithms = ['BFS', 'DFS', 'A*_h1', 'A*_h2', 'A*_h3']

    for (num_tubes,num_colors), seed in itertools.product(n_configs,seeds):
        print(f"\n Configuración: tubos={num_tubes}, colores={num_colors}, seed={seed} ")

        game = WaterSortGame(num_tubes, num_colors, seed)
        solver = SearchAlgorithm(game)
        initial_state = game.generate_initial_state()

        for algo in algorithms:
            try:
                if algo == 'BFS':
                    path, stats = solver.bfs(initial_state)
                elif algo == 'DFS':
                    path, stats = solver.dfs(initial_state)
                elif algo == 'A*_h1':
                    path, stats = solver.a_star(initial_state, solver.h1)
                elif algo == 'A*_h2':
                    path, stats = solver.a_star(initial_state, solver.h2)
                else: 
                    path, stats = solver.a_star(initial_state, solver.h3)

                results.append({
                    'Algoritmo': algo,
                    'Tubos': num_tubes,
                    'Colores': num_colors,
                    'Seed': seed,
                    'Tiempo (s)': stats['tiempo_seg'],
                    'Nodos expandidos': stats['nodos_expandidos'],
                    'Memoria máxima': stats['nodos_en_memoria_max'],
                    'Profundidad': stats['profundidad_solucion']
                })

                print(f"{algo}: OK ({stats['tiempo_seg']:.3f}s, {stats['nodos_expandidos']} nodos)")

            except Exception as e:
                print(f"{algo} falló: {e}")
                results.append({
                    'Algoritmo': algo,
                    'Tubos': num_tubes,
                    'Colores': num_colors,
                    'Seed': seed,
                    'Tiempo (s)': None,
                    'Nodos expandidos': None,
                    'Memoria máxima': None,
                    'Profundidad': None
                })

    df = pd.DataFrame(results)
    df.to_csv('resultados_experimentos.csv', index=False)
    print("\n Resultados guardados en 'resultados_experimentos.csv'")
    return df


def plot_results(df):
    metrics = ['Tiempo (s)', 'Nodos expandidos', 'Memoria máxima', 'Profundidad']

    for metric in metrics:
        plt.figure(figsize=(10,6))
        avg = df.groupby(['Tubos', 'Algoritmo'])[metric].mean().reset_index()

        for algo in df['Algoritmo'].unique():
            subset = avg[avg['Algoritmo'] == algo]
            plt.plot(subset['Tubos'], subset[metric], marker='o', label=algo)

        plt.title(f"Comparación de algoritmos - {metric}")
        plt.xlabel("Número de tubos")
        plt.ylabel(metric)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(f"grafico_{metric.replace(' ', '_')}.png")
        plt.show()


if __name__ == "__main__":
    df = run_experiments()
    plot_results(df)
