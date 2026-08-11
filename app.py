%%writefile app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tablero SGI - 50 Indicadores", layout="wide")

st.title("📊 Tablero de Control SGI")
st.markdown("---")

# 1. BASE DE DATOS DE INDICADORES (Plantilla para tus ~50 indicadores)
@st.cache_data
def cargar_datos():
    # Aquí puedes conectar un archivo Excel subido usando pd.read_excel('tus_indicadores.xlsx')
    # Estructura ejemplo con múltiples procesos del SGI:
    data = [
        {"Proceso": "Calidad", "Indicador": "Quejas de Clientes", "Meta": 1, "Tipo": "menor_mejor", "Ene": 5, "Feb": 3, "Mar": 2, "Abr": 4, "May": 1, "Jun": 1, "Jul": 0},
        {"Proceso": "Calidad", "Indicador": "Satisfacción del Cliente %", "Meta": 90, "Tipo": "mayor_mejor", "Ene": 85, "Feb": 88, "Mar": 92, "Abr": 90, "May": 94, "Jun": 95, "Jul": 97},
        {"Proceso": "SST", "Indicador": "Accidentes de Trabajo", "Meta": 0, "Tipo": "menor_mejor", "Ene": 2, "Feb": 1, "Mar": 0, "Abr": 1, "May": 0, "Jun": 0, "Jul": 0},
        {"Proceso": "SST", "Indicador": "Cumplimiento Capacitación %", "Meta": 85, "Tipo": "mayor_mejor", "Ene": 70, "Feb": 75, "Mar": 80, "Abr": 85, "May": 90, "Jun": 92, "Jul": 95},
        {"Proceso": "Ambiental", "Indicador": "Consumo Energía (kWh)", "Meta": 1200, "Tipo": "menor_mejor", "Ene": 1400, "Feb": 1350, "Mar": 1280, "Abr": 1210, "May": 1190, "Jun": 1150, "Jul": 1100},
    ]
    return pd.DataFrame(data)

df = cargar_datos()
meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul']

# Función para calcular semáforo
def evaluar_semaforo(valor, meta, tipo):
    if tipo == "mayor_mejor":
        if valor >= meta: return "🟢 Cumplido"
        elif valor >= meta * 0.85: return "🟡 En Riesgo"
        else: return "🔴 Crítico"
    else:
        if valor <= meta: return "🟢 Cumplido"
        elif valor <= meta * 1.15: return "🟡 En Riesgo"
        else: return "🔴 Crítico"

# 2. FILTROS EN LA BARRA LATERAL
st.sidebar.header("🔍 Filtros del Tablero")
proceso_sel = st.sidebar.selectbox("Selecciona el Proceso:", ["Todos"] + list(df["Proceso"].unique()))

if proceso_sel != "Todos":
    df_filtrado = df[df["Proceso"] == proceso_sel]
else:
    df_filtrado = df

# 3. TABLA CON SEMÁFOROS Y ESTADO ACTUAL
st.subheader("📋 Resumen General de Indicadores")

# Calcular estado para el último mes registrado (Julio)
df_resumen = df_filtrado.copy()
df_resumen['Valor Actual'] = df_resumen['Jul']
df_resumen['Semaforo'] = df_resumen.apply(lambda r: evaluar_semaforo(r['Valor Actual'], r['Meta'], r['Tipo']), axis=1)

# Mostrar tabla resuelta
st.dataframe(
    df_resumen[['Proceso', 'Indicador', 'Meta', 'Valor Actual', 'Semaforo']],
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# 4. ANÁLISIS DE TENDENCIA POR INDICADOR
st.subheader("📈 Análisis Detallado y Tendencia")

indicador_sel = st.selectbox("Selecciona un indicador para ver su gráfico de tendencia:", df_filtrado["Indicador"].unique())

row_ind = df[df["Indicador"] == indicador_sel].iloc[0]
df_tendencia = pd.DataFrame({
    'Mes': meses,
    'Valor': [row_ind[m] for m in meses]
})

col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown(f"### {row_ind['Indicador']}")
    st.write(f"**Proceso:** {row_ind['Proceso']}")
    st.write(f"**Meta:** {row_ind['Meta']}")
    st.write(f"**Resultado Último Mes:** {row_ind['Jul']}")
    st.markdown(f"**Estado Semáforo:** {evaluar_semaforo(row_ind['Jul'], row_ind['Meta'], row_ind['Tipo'])}")

with col_right:
    fig = px.line(
        df_tendencia,
        x='Mes',
        y='Valor',
        title=f"Evolución Mensual - {indicador_sel}",
        markers=True,
        text='Valor'
    )
    fig.add_hline(y=row_ind['Meta'], line_dash="dash", line_color="red", annotation_text="Meta")
    st.plotly_chart(fig, use_container_width=True)
