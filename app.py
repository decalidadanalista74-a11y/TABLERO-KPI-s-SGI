import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np
import io

# Configuración de página
st.set_page_config(page_title="Tablero SGI con Análisis Predictivo", layout="wide", page_icon="🎯")

st.title("🎯 Tablero de Control SGI con Análisis Predictivo")
st.markdown("---")

# Base de datos inicial
datos_defecto = [
    {"Proceso": "Calidad", "Indicador": "Quejas de Clientes", "Meta": 1, "Tipo": "menor_mejor", "Ene": 5, "Feb": 4, "Mar": 3, "Abr": 2, "May": 2, "Jun": 1, "Jul": 1, "Ago": None},
    {"Proceso": "Calidad", "Indicador": "Satisfacción del Cliente %", "Meta": 90, "Tipo": "mayor_mejor", "Ene": 82, "Feb": 85, "Mar": 88, "Abr": 87, "May": 91, "Jun": 93, "Jul": 94, "Ago": None},
    {"Proceso": "SST", "Indicador": "Accidentes de Trabajo", "Meta": 0, "Tipo": "menor_mejor", "Ene": 2, "Feb": 1, "Mar": 1, "Abr": 0, "May": 1, "Jun": 0, "Jul": 0, "Ago": None},
    {"Proceso": "SST", "Indicador": "Cumplimiento Capacitación %", "Meta": 85, "Tipo": "mayor_mejor", "Ene": 70, "Feb": 75, "Mar": 78, "Abr": 82, "May": 88, "Jun": 90, "Jul": 92, "Ago": None},
    {"Proceso": "Gestión Ambiental", "Indicador": "Consumo de Energía (kWh)", "Meta": 1200, "Tipo": "menor_mejor", "Ene": 1450, "Feb": 1380, "Mar": 1300, "Abr": 1250, "May": 1220, "Jun": 1180, "Jul": 1150, "Ago": None},
    {"Proceso": "Gestión Ambiental", "Indicador": "Residuos Reciclados (Kg)", "Meta": 500, "Tipo": "mayor_mejor", "Ene": 350, "Feb": 380, "Mar": 420, "Abr": 460, "May": 490, "Jun": 510, "Jul": 530, "Ago": None}
]

# Inicializar memoria de sesión
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(datos_defecto)

# Barra lateral
st.sidebar.header("⚙️ Gestión y Filtros")

# Carga de Excel
st.sidebar.subheader("Subir base de indicadores (Excel)")
uploaded_file = st.sidebar.file_uploader("Upload", type=["xlsx", "xls"], label_visibility="collapsed")

if uploaded_file is not None:
    try:
        st.session_state.df = pd.read_excel(uploaded_file)
        st.sidebar.success("¡Base de datos cargada!")
    except Exception as e:
        st.sidebar.error(f"Error al leer archivo: {e}")

# Botón para descargar Excel
output = io.BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    st.session_state.df.to_excel(writer, index=False, sheet_name='Indicadores_SGI')
processed_data = output.getvalue()

st.sidebar.download_button(
    label="💾 Descargar Base Actualizada",
    data=processed_data,
    file_name='Indicadores_SGI_Actualizado.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

st.sidebar.markdown("---")

# Filtros
procesos = ["Todos"] + list(st.session_state.df["Proceso"].dropna().unique())
proceso_sel = st.sidebar.selectbox("1️⃣ Selecciona el Proceso:", procesos)

if proceso_sel != "Todos":
    df_filtrado = st.session_state.df[st.session_state.df["Proceso"] == proceso_sel]
else:
    df_filtrado = st.session_state.df.copy()

indicadores = list(df_filtrado["Indicador"].dropna().unique())
indicador_sel = st.sidebar.selectbox("2️⃣ Selecciona el Indicador:", indicadores) if indicadores else None

# Pestañas principales
tab1, tab2 = st.tabs(["📊 Dashboard & Diagnóstico Inteligente", "✏️ Ingresar / Editar Resultados y Metas"])

# --- PESTAÑA 2: EDITOR INTERACTIVO ---
with tab2:
    st.subheader("✏️ Editor Interactivo de Indicadores")
    st.info("Puedes agregar más filas para tus indicadores, ajustar las metas o escribir los avances mes a mes directamente en la tabla. Todos los cambios repercutirán de inmediato en el tablero.")
    
    edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
    st.session_state.df = edited_df

# --- PESTAÑA 1: DASHBOARD ---
with tab1:
    meses_cols = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    meses_presentes = [m for m in meses_cols if m in st.session_state.df.columns]
    
    st.subheader("📋 Resumen General de Indicadores")
    
    # Calcular semáforos
    resumen = []
    for _, row in df_filtrado.iterrows():
        valores_validos = [row[m] for m in meses_presentes if pd.notnull(row[m])]
        ult_valor = valores_validos[-1] if valores_validos else "Sin datos"
        meta = row.get("Meta", 0)
        tipo = row.get("Tipo", "mayor_mejor")
        
        if isinstance(ult_valor, (int, float)):
            cumple = (ult_valor <= meta) if tipo == "menor_mejor" else (ult_valor >= meta)
            semaforo = "🟢 Cumplido" if cumple else "🔴 No Cumplido"
        else:
            semaforo = "⚪ Sin Datos"
            
        resumen.append({
            "Proceso": row.get("Proceso", ""),
            "Indicador": row.get("Indicador", ""),
            "Meta": meta,
            "Último Valor": ult_valor,
            "Estado": semaforo
        })
    
    st.dataframe(pd.DataFrame(resumen), use_container_width=True)
    
    st.markdown("---")
    
    # Análisis Detallado e Inteligencia Predictiva
    if indicador_sel:
        row_ind = df_filtrado[df_filtrado["Indicador"] == indicador_sel].iloc[0]
        st.subheader(f"📈 Análisis Detallado: {indicador_sel}")
        
        # Extraer serie temporal
        x_vals = []
        y_vals = []
        meses_labels = []
        
        for idx, m in enumerate(meses_presentes):
            val = row_ind.get(m, None)
            if pd.notnull(val):
                try:
                    y_vals.append(float(val))
                    x_vals.append(idx)
                    meses_labels.append(m)
                except ValueError:
                    pass
        
        if len(y_vals) >= 2:
            # Modelo Predictivo
            X = np.array(x_vals).reshape(-1, 1)
            y = np.array(y_vals)
            model = LinearRegression().fit(X, y)
            
            siguiente_mes_idx = max(x_vals) + 1
            prediccion = model.predict([[siguiente_mes_idx]])[0]
            
            # Gráfica con Plotly
            df_plot = pd.DataFrame({"Mes": meses_labels, "Resultado": y_vals})
            fig = px.line(df_plot, x="Mes", y="Resultado", markers=True, title=f"Evolución Mensual - {indicador_sel}")
            fig.add_hline(y=row_ind.get("Meta", 0), line_dash="dash", line_color="red", annotation_text="Meta")
            st.plotly_chart(fig, use_container_width=True)
            
            # Métricas y Diagnóstico
            col1, col2, col3 = st.columns(3)
            col1.metric("Último Registro", f"{y_vals[-1]}")
            col2.metric("Meta Establecida", f"{row_ind.get('Meta', 0)}")
            col3.metric("Proyección Siguiente Mes", f"{prediccion:.2f}")
            
            # Generador de Diagnóstico IA
            meta_val = float(row_ind.get("Meta", 0))
            tipo_val = row_ind.get("Tipo", "mayor_mejor")
            cumple_pred = (prediccion <= meta_val) if tipo_val == "menor_mejor" else (prediccion >= meta_val)
            
            st.markdown("### 💡 Diagnóstico Automático")
            if cumple_pred:
                st.success(f"**Tendencia Favorable:** Según la proyección lineal ({prediccion:.2f}), el indicador mantendrá el cumplimiento de la meta ({meta_val}) en el próximo periodo. Se sugiere mantener los controles operacionales actuales.")
            else:
                st.warning(f"**Alerta Preventiva:** La tendencia proyectada ({prediccion:.2f}) indica riesgo de incumplir la meta ({meta_val}). Se recomienda revisar las causas raíz e implementar acciones correctivas/preventivas en el marco del SGI.")
        else:
            st.info("Ingresa al menos 2 meses de datos para habilitar el gráfico de tendencia y el análisis predictivo.")
