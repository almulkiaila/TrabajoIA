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

# ========= GRAFICAS COMPARATIVAS POR MÉTRICA (LOGARÍTMICA) =========
for metrica in metricas:
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="algoritmo", y=metrica)
    plt.yscale("log")  # Escala logarítmica
    plt.title(f"Comparativa de {metrica} por algoritmo (escala log)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    filename = f"{OUTPUT_DIR}/comparativa_log_{sanitize_filename(metrica)}.png"
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"📊 Guardado: {filename}")

# ========= GRAFICAS 3D COMPARANDO ALGORITMOS =========
metricas_3d = ["tiempo_total", "nodos_expandidos"]

for metrica_3d in metricas_3d:
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    for algoritmo in df["algoritmo"].unique():
        subset = df[df["algoritmo"] == algoritmo]
        # plot_trisurf permite coordenadas irregulares
        ax.plot_trisurf(subset["num_tubes"], subset["num_colors"], subset[metrica_3d],
                        alpha=0.7, label=algoritmo)

    ax.set_xlabel("Número de tubos")
    ax.set_ylabel("Número de colores")
    ax.set_zlabel(metrica_3d)
    ax.set_title(f"Comparativa 3D por algoritmo - {metrica_3d}")
    ax.view_init(elev=30, azim=135)  # Ajuste de ángulo
    plt.legend(df["algoritmo"].unique())

    filename = f"{OUTPUT_DIR}/3D_comparativa_{sanitize_filename(metrica_3d)}.png"
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"🧊 Guardado: {filename}")

print("\n✅ Todas las gráficas se han generado correctamente.")
print(f"📂 Guardadas en: {os.path.abspath(OUTPUT_DIR)}")
