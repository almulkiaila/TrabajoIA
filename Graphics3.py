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
df_astar = df[
    df["algoritmo"].str.startswith("A*") & 
    (df["solved"] == True)
].dropna(subset=["tiempo_seg", "nodos_expandidos", "nodos_en_memoria_max"])

# Crear columna "heuristica" a partir del nombre del algoritmo
df_astar["heuristica"] = df_astar["algoritmo"].str.replace("A*_", "", regex=False)

# Obtener lista de heurísticas y asignar colores distintos
heuristicas = df_astar["heuristica"].unique()
colors = px.colors.qualitative.Plotly
color_map = {heuristicas[i]: colors[i % len(colors)] for i in range(len(heuristicas))}

# Métricas a graficar (ahora incluye los nodos en memoria)
metricas_3d = ["tiempo_seg", "nodos_expandidos", "nodos_en_memoria_max"]

def sanitize_filename(name: str):
    return name.replace("/", "_").replace("*", "star").replace(" ", "_")

# ============================
# 🔹 GRÁFICAS 3D INTERACTIVAS CON LEYENDA
# ============================
for metrica in metricas_3d:
    fig = go.Figure()

    for heuristica in heuristicas:
        subset = df_astar[df_astar["heuristica"] == heuristica]
        color = color_map[heuristica]

        # --- Mesh 3D principal ---
        fig.add_trace(
            go.Mesh3d(
                x=subset["num_tubes"],
                y=subset["num_colors"],
                z=subset[metrica],
                color=color,
                opacity=0.7,
                name=heuristica,
                hovertemplate=(
                    "Heurística: " + heuristica + "<br>" +
                    "Tubes: %{x}<br>" +
                    "Colors: %{y}<br>" +
                    metrica + ": %{z}<extra></extra>"
                ),
                showlegend=False
            )
        )

        # --- Punto fantasma solo para mostrar color en la leyenda ---
        fig.add_trace(
            go.Scatter3d(
                x=[None], y=[None], z=[None],
                mode="markers",
                marker=dict(size=8, color=color),
                name=heuristica,
                showlegend=True
            )
        )

    # --- Layout y configuración general ---
    fig.update_layout(
        title=f"A* - Comparativa heurísticas 3D interactiva ({metrica})",
        scene=dict(
            xaxis_title="Número de tubos",
            yaxis_title="Número de colores",
            zaxis_title=metrica,
            zaxis_type="log"
        ),
        legend=dict(
            title="Heurística",
            itemsizing="constant",
            x=0.02,
            y=0.98,
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="black",
            borderwidth=1
        ),
        width=1000,
        height=800
    )

    # --- Guardar archivo HTML ---
    filename = os.path.join(
        OUTPUT_DIR,
        f"graficas_3D_heuristicas_Astar/3D_heuristicas_Astar_{sanitize_filename(metrica)}.html"
    )
    fig.write_html(filename)
    print(f"🧊 Guardado interactivo con leyenda: {filename}")

print("\n✅ Gráficas 3D de heurísticas de A* generadas correctamente.")
