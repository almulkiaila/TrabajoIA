import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# === Configuración ===
INPUT_FILE = "resultados_pruebas.csv"
OUTPUT_DIR = "graficas_resultados"

sns.set(style="whitegrid", context="talk")

# Crear carpetas
os.makedirs(OUTPUT_DIR, exist_ok=True)
for sub in ["lineas", "barras", "facets"]:
    os.makedirs(os.path.join(OUTPUT_DIR, f"graficas_{sub}"), exist_ok=True)

# === Cargar datos ===
print(f"📂 Cargando datos desde {INPUT_FILE}...")
df = pd.read_csv(INPUT_FILE)

# Filtrar casos válidos
df = df[df["solved"] == True].dropna(subset=["tiempo_seg", "nodos_expandidos"])

# === Agrupar por configuración (promedio de 10 semillas) ===
print("📊 Calculando promedios por configuración...")
df_avg = (
    df.groupby(["algoritmo", "num_tubes", "num_colors"])
    .agg({
        "nodos_expandidos": "mean",
        "nodos_en_memoria_max": "mean",
        "tiempo_seg": "mean",
        "profundidad_solucion": "mean"
    })
    .reset_index()
)

# Métricas a analizar
metricas = ["nodos_expandidos", "nodos_en_memoria_max", "tiempo_seg", "profundidad_solucion"]

def sanitize_filename(name: str):
    """Evita errores al guardar nombres con caracteres especiales."""
    return name.replace("/", "_").replace("*", "star").replace(" ", "_")

# ============================
# 🔹 1. GRÁFICAS DE LÍNEAS
# ============================
print("\n📈 Generando gráficas de líneas promedio...")
for metrica in metricas:
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df_avg, x="num_tubes", y=metrica, hue="algoritmo", marker="o")
    plt.title(f"Evolución promedio de {metrica} según número de tubos")
    plt.xlabel("Número de tubos")
    plt.ylabel(metrica)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/graficas_lineas/lineplot_{sanitize_filename(metrica)}_tubos.png", dpi=300)
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df_avg, x="num_colors", y=metrica, hue="algoritmo", marker="o")
    plt.title(f"Evolución promedio de {metrica} según número de colores")
    plt.xlabel("Número de colores")
    plt.ylabel(metrica)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/graficas_lineas/lineplot_{sanitize_filename(metrica)}_colores.png", dpi=300)
    plt.close()

# ============================
# 🔹 2. GRÁFICAS DE BARRAS
# ============================
print("📊 Generando gráficas de barras promedio...")
for metrica in metricas:
    plt.figure(figsize=(10, 6))
    mean_vals = df_avg.groupby("algoritmo")[metrica].mean().reset_index()
    sns.barplot(data=mean_vals, x="algoritmo", y=metrica)
    plt.title(f"Media global de {metrica} por algoritmo")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/graficas_barras/barplot_{sanitize_filename(metrica)}.png", dpi=300)
    plt.close()

# ============================
# 🔹 3. HEATMAPS
# ============================
print("🔥 Generando heatmaps promedio...")
for metrica in metricas:
    for algoritmo in df_avg["algoritmo"].unique():
        subset = df_avg[df_avg["algoritmo"] == algoritmo]
        pivot = subset.pivot_table(index="num_colors", columns="num_tubes", values=metrica, aggfunc="mean")

        plt.figure(figsize=(8, 6))
        sns.heatmap(pivot, cmap="viridis", annot=False)
        plt.title(f"{algoritmo} - {metrica} (promedio)")
        plt.xlabel("Número de tubos")
        plt.ylabel("Número de colores")
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/graficas_facets/heatmap_{sanitize_filename(algoritmo)}_{sanitize_filename(metrica)}.png", dpi=300)
        plt.close()

print("\n✅ Todas las gráficas promediadas se han guardado en:")
print(f"   📁 {os.path.abspath(OUTPUT_DIR)}")



# ===============================================
# 🔹 4. TABLA RESUMEN DE MEJORES ALGORITMOS
# ===============================================
print("\n🏆 Generando tabla resumen de mejores algoritmos...")

resumen = []
for metrica in metricas:
    mean_vals = df_avg.groupby("algoritmo")[metrica].mean().reset_index()
    # Para tiempo y nodos, el mejor es el mínimo; para profundidad, el máximo
    mejor_algoritmo = (
        mean_vals.loc[mean_vals[metrica].idxmin()]
        if metrica != "profundidad_solucion"
        else mean_vals.loc[mean_vals[metrica].idxmax()]
    )
    resumen.append({
        "métrica": metrica,
        "mejor_algoritmo": mejor_algoritmo["algoritmo"],
        "valor_promedio": mejor_algoritmo[metrica]
    })

df_resumen = pd.DataFrame(resumen)

# Guardar en CSV
csv_path = os.path.join(OUTPUT_DIR, "resumen_mejores_algoritmos.csv")
df_resumen.to_csv(csv_path, index=False)
print(f"✅ Resumen guardado en {csv_path}")

# Mostrar tabla visual
plt.figure(figsize=(6, 2 + len(df_resumen) * 0.5))
plt.axis("off")
tabla = plt.table(
    cellText=df_resumen.values,
    colLabels=df_resumen.columns,
    cellLoc='center',
    loc='center'
)
tabla.auto_set_font_size(False)
tabla.set_fontsize(10)
tabla.scale(1.2, 1.5)
plt.title("🏁 Mejores algoritmos promedio por métrica", fontsize=12, pad=10)

# Guardar imagen
plt.savefig(f"{OUTPUT_DIR}/tabla_resumen_mejores.png", dpi=300, bbox_inches="tight")
plt.close()

print("\n📋 Tabla resumen generada correctamente:")
print(df_resumen)
