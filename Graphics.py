# ==========================
# 📊 Análisis de Resultados Water Sort (con guardado automático)
# ==========================
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

# --------------------------
# CONFIGURACIÓN
# --------------------------
INPUT_FILE = "resultados_pruebas.csv"
OUTPUT_DIR = "graficas_resultados"

# Crear carpeta de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cargar datos
df = pd.read_csv(INPUT_FILE)
df = df.fillna(0)

# Orden de algoritmos
orden_algoritmos = ["BFS", "DFS", "A*_h1", "A*_h2", "A*_h3"]
df["algoritmo"] = pd.Categorical(df["algoritmo"], categories=orden_algoritmos, ordered=True)

# Métricas a graficar
metricas = ["nodos_expandidos", "nodos_en_memoria_max", "tiempo_total", "profundidad_solucion"]

# --------------------------
# 1️⃣ GRÁFICAS 2D COMPARATIVAS
# --------------------------
print("\n📈 Generando y guardando gráficas 2D...")

for metrica in metricas:
    plt.figure(figsize=(8,5))
    df_grouped = df.groupby(["num_tubes", "algoritmo"])[metrica].mean().reset_index()
    sns.lineplot(data=df_grouped, x="num_tubes", y=metrica, hue="algoritmo", marker="o")
    plt.title(f"Comparativa de {metrica} por número de tubos")
    plt.xlabel("Número de tubos")
    plt.ylabel(metrica)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(title="Algoritmo")
    plt.tight_layout()

    filename = f"{OUTPUT_DIR}/comparativa_{metrica}.png"
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"✅ Guardado: {filename}")

# --------------------------
# 2️⃣ HEATMAPS (mapas de calor)
# --------------------------
print("\n🔥 Generando heatmaps por algoritmo y métrica...")

for algoritmo in orden_algoritmos:
    df_alg = df[df["algoritmo"] == algoritmo]
    for metrica in metricas:
        pivot = df_alg.pivot_table(index="num_tubes", columns="num_colors", values=metrica, aggfunc="mean")
        plt.figure(figsize=(7,5))
        sns.heatmap(pivot, cmap="YlGnBu", annot=False)
        plt.title(f"Heatmap de {metrica} - {algoritmo}")
        plt.xlabel("Número de colores")
        plt.ylabel("Número de tubos")
        plt.tight_layout()

        filename = f"{OUTPUT_DIR}/heatmap_{algoritmo}_{metrica}.png"
        plt.savefig(filename, dpi=300)
        plt.close()
        print(f"✅ Guardado: {filename}")

# --------------------------
# 3️⃣ GRÁFICAS 3D (opcional)
# --------------------------
metrica_3d = "tiempo_total"
print(f"\n🧊 Generando gráficas 3D para '{metrica_3d}'...")

for algoritmo in orden_algoritmos:
    df_alg = df[df["algoritmo"] == algoritmo]

    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(df_alg["num_tubes"], df_alg["num_colors"], df_alg[metrica_3d], c='b', marker='o')

    ax.set_xlabel("Nº tubos")
    ax.set_ylabel("Nº colores")
    ax.set_zlabel(metrica_3d)
    ax.set_title(f"{algoritmo} - {metrica_3d}")
    plt.tight_layout()

    filename = f"{OUTPUT_DIR}/3D_{algoritmo}_{metrica_3d}.png"
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"✅ Guardado: {filename}")

print(f"\n🎉 Todas las gráficas se han guardado correctamente en: {OUTPUT_DIR}/")

