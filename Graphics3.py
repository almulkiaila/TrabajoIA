import os
import pandas as pd
import plotly.graph_objects as go

# === Configuración ===
INPUT_FILE = "resultados_pruebas.csv"
OUTPUT_DIR = "graficas_resultados"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "graficas_3D_interactivas_Astar_avanzadas"), exist_ok=True)

# === Cargar datos ===
df = pd.read_csv(INPUT_FILE)

# Filtrar solo algoritmos A* y casos válidos
df_astar = df[df["algoritmo"].str.startswith("A*") & (df["solved"] == True)].dropna(subset=["tiempo_seg", "nodos_expandidos"])

# Crear columna "heuristica" a partir del nombre del algoritmo
df_astar["heuristica"] = df_astar["algoritmo"].str.replace("A*_", "")

# Métricas a graficar
metricas_3d = ["tiempo_seg", "nodos_expandidos"]

def sanitize_filename(name: str):
    return name.replace("/", "_").replace("*", "star").replace(" ", "_")

# ============================
# 🔹 GRÁFICAS 3D INTERACTIVAS AVANZADAS PARA A*
# ============================
for metrica in metricas_3d:
    fig = go.Figure()

    for heuristica in df_astar["heuristica"].unique():
        subset = df_astar[df_astar["heuristica"] == heuristica]

        # Intensidad de color según valor de la métrica
        fig.add_trace(
            go.Mesh3d(
                x=subset["num_tubes"],
                y=subset["num_colors"],
                z=subset[metrica],
                intensity=subset[metrica],
                colorscale="Viridis",
                opacity=0.7,
                name=heuristica,
                colorbar_title=metrica,
                hovertemplate=(
                    "Heurística: " + heuristica + "<br>" +
                    "Tubes: %{x}<br>" +
                    "Colors: %{y}<br>" +
                    f"{metrica}: " + "%{z}<extra></extra>"
                )
            )
        )

    fig.update_layout(
        title=f"A* - Comparativa heurísticas 3D interactiva ({metrica})",
        scene=dict(
            xaxis_title="Número de tubos",
            yaxis_title="Número de colores",
            zaxis_title=metrica,
            zaxis_type="log"
        ),
        legend_title_text="Heurística",
        width=1000,
        height=800
    )

    filename = os.path.join(OUTPUT_DIR, f"graficas_3D_interactivas_Astar_avanzadas/3D_Astar_log_heatmap_{sanitize_filename(metrica)}.html")
    fig.write_html(filename)
    print(f"🧊 Guardado interactivo avanzado: {filename}")
