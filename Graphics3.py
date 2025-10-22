import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# === Configuración ===
INPUT_FILE = "resultados_pruebas.csv"
OUTPUT_DIR = "graficas_resultados"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "graficas_3D_heuristicas_Astar"), exist_ok=True)

# === Cargar datos ===
df = pd.read_csv(INPUT_FILE)

# Filtrar solo A* y casos válidos
df_astar = df[df["algoritmo"].str.startswith("A*") & (df["solved"] == True)].dropna(subset=["tiempo_seg", "nodos_expandidos"])

# Crear columna "heuristica" a partir del nombre del algoritmo
df_astar["heuristica"] = df_astar["algoritmo"].str.replace("A*_", "")

# Obtener lista de heurísticas y asignar colores distintos
heuristicas = df_astar["heuristica"].unique()
colors = px.colors.qualitative.Plotly
color_map = {heuristicas[i]: colors[i % len(colors)] for i in range(len(heuristicas))}

# Métricas a graficar
metricas_3d = ["tiempo_seg", "nodos_expandidos"]

def sanitize_filename(name: str):
    return name.replace("/", "_").replace("*", "star").replace(" ", "_")

# ============================
# 🔹 GRÁFICAS 3D INTERACTIVAS PARA HEURÍSTICAS DE A*
# ============================
for metrica in metricas_3d:
    fig = go.Figure()

    for heuristica in heuristicas:
        subset = df_astar[df_astar["heuristica"] == heuristica]

        fig.add_trace(
            go.Mesh3d(
                x=subset["num_tubes"],
                y=subset["num_colors"],
                z=subset[metrica],
                color=color_map[heuristica],
                opacity=0.7,
                name=heuristica,
                hovertemplate=(
                    "Heurística: " + heuristica + "<br>" +
                    "Tubes: %{x}<br>" +
                    "Colors: %{y}<br>" +
                    metrica + ": %{z}<extra></extra>"
                )
            )
        )

    # Configuración del layout
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

    # Guardar archivo HTML
    filename = os.path.join(
        OUTPUT_DIR,
        f"graficas_3D_heuristicas_Astar/3D_heuristicas_Astar_{sanitize_filename(metrica)}.html"
    )
    fig.write_html(filename)
    print(f"🧊 Guardado interactivo heurísticas A*: {filename}")
