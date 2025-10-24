import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# === Configuración ===
INPUT_FILE = "resultados_pruebas.csv"
OUTPUT_DIR = "graficas_resultados"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "graficas_3D_Astar_h3_BFS_DFS"), exist_ok=True)

# === Cargar datos ===
df = pd.read_csv(INPUT_FILE)

# Filtrar solo los algoritmos de interés y casos válidos
algoritmos_interes = ["A*_h3", "BFS", "DFS"]
df_filtrado = df[
    df["algoritmo"].isin(algoritmos_interes) & 
    (df["solved"] == True)
].dropna(subset=["tiempo_seg", "nodos_expandidos", "nodos_en_memoria_max"])

# === Asignar colores ===
colors = px.colors.qualitative.D3  # paleta bien contrastada
color_map = {
    "A*_h3": colors[0],
    "BFS": colors[1],
    "DFS": colors[2]
}

# === Métricas a graficar ===
metricas_3d = ["tiempo_seg", "nodos_expandidos", "nodos_en_memoria_max"]

def sanitize_filename(name: str):
    return name.replace("/", "_").replace("*", "star").replace(" ", "_")

# ============================
# 🔹 GRÁFICAS 3D INTERACTIVAS CON LEYENDA
# ============================
for metrica in metricas_3d:
    fig = go.Figure()

    for algoritmo in algoritmos_interes:
        subset = df_filtrado[df_filtrado["algoritmo"] == algoritmo]
        color = color_map[algoritmo]

        # --- Superficie 3D principal ---
        fig.add_trace(
            go.Mesh3d(
                x=subset["num_tubes"],
                y=subset["num_colors"],
                z=subset[metrica],
                color=color,
                opacity=0.7,
                name=algoritmo,
                hovertemplate=(
                    "Algoritmo: " + algoritmo + "<br>" +
                    "Tubes: %{x}<br>" +
                    "Colors: %{y}<br>" +
                    metrica + ": %{z}<extra></extra>"
                ),
                showlegend=False
            )
        )

        # --- Punto fantasma para mostrar el color en la leyenda ---
        fig.add_trace(
            go.Scatter3d(
                x=[None], y=[None], z=[None],
                mode="markers",
                marker=dict(size=8, color=color),
                name=algoritmo,
                showlegend=True
            )
        )

    # --- Configuración del layout ---
    fig.update_layout(
        title=f"Comparativa 3D A*_h3 vs BFS vs DFS ({metrica})",
        scene=dict(
            xaxis_title="Número de tubos",
            yaxis_title="Número de colores",
            zaxis_title=metrica,
            zaxis_type="log"
        ),
        legend=dict(
            title="Algoritmo",
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
        f"graficas_3D_Astar_h3_BFS_DFS/3D_Astar_h3_BFS_DFS_{sanitize_filename(metrica)}.html"
    )
    fig.write_html(filename)
    print(f"🧊 Guardado: {filename}")

print("\n✅ Gráficas 3D comparativas A*_h3 vs BFS vs DFS generadas correctamente.")
