import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# === Configuración ===
INPUT_FILE = "resultados_pruebas.csv"
OUTPUT_DIR = "graficas_resultados"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "graficas_3D_comparativa_final_colores"), exist_ok=True)

# === Cargar datos ===
df = pd.read_csv(INPUT_FILE)
df = df[df["solved"] == True].dropna(subset=["tiempo_seg", "nodos_expandidos"])

# Crear máscara para identificar A*
mask_astar = df["algoritmo"].str.startswith("A*")

# Seleccionar la mejor heurística A*_h3
df_best_h3 = df[df["algoritmo"] == "A*_h3"]

# Obtener lista de algoritmos (A*_h3 + demás)
algoritmos = ["A*_h3"] + list(df[~mask_astar]["algoritmo"].unique())

# Asignar colores distintos usando Plotly Express
colors = px.colors.qualitative.Plotly
color_map = {algoritmos[i]: colors[i % len(colors)] for i in range(len(algoritmos))}

# Métricas a graficar
metricas_3d = ["tiempo_seg", "nodos_expandidos"]

def sanitize_filename(name: str):
    return name.replace("/", "_").replace("*", "star").replace(" ", "_")

# ============================
# 🔹 GRÁFICAS 3D INTERACTIVAS CON COLORES DISTINTOS
# ============================
for metrica in metricas_3d:
    fig = go.Figure()

    # ===== Añadir A*_h3 =====
    fig.add_trace(
        go.Mesh3d(
            x=df_best_h3["num_tubes"],
            y=df_best_h3["num_colors"],
            z=df_best_h3[metrica],
            color=color_map["A*_h3"],
            opacity=0.7,
            name="A*_h3",
            hovertemplate=(
                "Algoritmo: A*_h3<br>" +
                "Tubes: %{x}<br>" +
                "Colors: %{y}<br>" +
                metrica + ": %{z}<extra></extra>"
            )
        )
    )

    # ===== Añadir los demás algoritmos =====
    for algoritmo in df[~mask_astar]["algoritmo"].unique():
        subset = df[df["algoritmo"] == algoritmo]
        fig.add_trace(
            go.Mesh3d(
                x=subset["num_tubes"],
                y=subset["num_colors"],
                z=subset[metrica],
                color=color_map[algoritmo],
                opacity=0.6,
                name=algoritmo,
                hovertemplate=(
                    "Algoritmo: " + algoritmo + "<br>" +
                    "Tubes: %{x}<br>" +
                    "Colors: %{y}<br>" +
                    metrica + ": %{z}<extra></extra>"
                )
            )
        )

    # ===== Configuración de layout =====
    fig.update_layout(
        title=f"Comparativa 3D: A*_h3 vs demás algoritmos ({metrica})",
        scene=dict(
            xaxis_title="Número de tubos",
            yaxis_title="Número de colores",
            zaxis_title=metrica,
            zaxis_type="log"
        ),
        legend_title_text="Algoritmo",
        width=1000,
        height=800
    )

    # ===== Guardar archivo HTML =====
    filename = os.path.join(
        OUTPUT_DIR,
        f"graficas_3D_comparativa_final_colores/3D_comparativa_Astar_h3_{sanitize_filename(metrica)}.html"
    )
    fig.write_html(filename)
    print(f"🧊 Guardado interactivo comparativa final: {filename}")
