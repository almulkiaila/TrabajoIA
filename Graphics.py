import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
from mpl_toolkits.mplot3d import Axes3D

# ========= CONFIGURACIÓN =========
INPUT_FILE = "resultados_pruebas.csv"
OUTPUT_DIR = "graficas_resultados"

# Crear carpeta de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========= FUNCIÓN PARA LIMPIAR NOMBRES =========
def sanitize_filename(name: str) -> str:
    """Elimina caracteres no válidos para nombres de archivo en Windows."""
    return re.sub(r'[<>:"/\\|?*]', '_', str(name))

# ========= CARGA DE DATOS =========
df = pd.read_csv(INPUT_FILE)
print(f"✅ Datos cargados: {len(df)} filas")

# Filtramos por si hay errores o NaN
df = df[df["error"].isna() | (df["error"] == "")]
print(f"📊 Después de filtrar errores: {len(df)} filas")

# ========= LISTA DE MÉTRICAS =========
metricas = ["nodos_expandidos", "nodos_en_memoria_max", "tiempo_total", "profundidad_solucion"]

# ========= GRAFICAS HEATMAP POR ALGORITMO =========
for algoritmo in df["algoritmo"].unique():
    subset = df[df["algoritmo"] == algoritmo]
    for metrica in metricas:
        pivot = subset.pivot_table(values=metrica, index="num_colors", columns="num_tubes", aggfunc="mean")
        plt.figure(figsize=(8, 6))
        sns.heatmap(pivot, annot=True, fmt=".1f", cmap="viridis")
        plt.title(f"{algoritmo} - {metrica}")
        plt.xlabel("Número de tubos")
        plt.ylabel("Número de colores")

        filename = f"{OUTPUT_DIR}/heatmap_{sanitize_filename(algoritmo)}_{sanitize_filename(metrica)}.png"
        plt.savefig(filename, dpi=300)
        plt.close()
        print(f"📈 Guardado: {filename}")

# ========= GRAFICAS COMPARATIVAS POR MÉTRICA =========
for metrica in metricas:
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="algoritmo", y=metrica)
    plt.title(f"Comparativa de {metrica} por algoritmo")
    plt.xticks(rotation=45)
    plt.tight_layout()

    filename = f"{OUTPUT_DIR}/comparativa_{sanitize_filename(metrica)}.png"
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"📊 Guardado: {filename}")

# ========= GRAFICAS 3D =========
metricas_3d = ["tiempo_total", "nodos_expandidos"]

for algoritmo in df["algoritmo"].unique():
    subset = df[df["algoritmo"] == algoritmo]
    for metrica_3d in metricas_3d:
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        sc = ax.scatter(subset["num_tubes"], subset["num_colors"], subset[metrica_3d],
                        c=subset[metrica_3d], cmap="plasma")
        ax.set_xlabel("Número de tubos")
        ax.set_ylabel("Número de colores")
        ax.set_zlabel(metrica_3d)
        ax.set_title(f"{algoritmo} - {metrica_3d}")
        fig.colorbar(sc, ax=ax, shrink=0.5, aspect=10)

        filename = f"{OUTPUT_DIR}/3D_{sanitize_filename(algoritmo)}_{sanitize_filename(metrica_3d)}.png"
        plt.savefig(filename, dpi=300)
        plt.close()
        print(f"🧊 Guardado: {filename}")

print("\n✅ Todas las gráficas se han generado correctamente.")
print(f"📂 Guardadas en: {os.path.abspath(OUTPUT_DIR)}")
