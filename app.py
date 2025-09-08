import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Control de Peso", layout="centered")
st.title("📊 Control de Peso - Línea de Producción")

# --- Entrada de datos ---
st.header("📥 Ingreso de datos")
producto = st.text_input("Producto")
peso = st.number_input("Peso (g)", min_value=0.0, step=0.1)
lsl = st.number_input("LSL - Límite inferior", min_value=0.0, step=0.1)
usl = st.number_input("USL - Límite superior", min_value=0.0, step=0.1)

# --- Conexión con Google Sheets ---
conn = st.connection("gsheet", type=GSheetsConnection)
df = conn.read(worksheet="Hoja 1")  # Asegúrate de que tu hoja se llame "Hoja 1"

# --- Validación y guardado ---
if st.button("Guardar datos"):
    if not producto:
        st.error("⚠️ Debes ingresar el nombre del producto.")
    elif peso == 0 or lsl == 0 or usl == 0:
        st.error("⚠️ Peso, LSL y USL deben ser mayores que 0.")
    elif lsl >= usl:
        st.error("⚠️ LSL debe ser menor que USL.")
    else:
        nuevo = {"producto": producto, "peso": peso, "lsl": lsl, "usl": usl}
        df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
        conn.write(df)
        st.success("✅ Datos guardados exitosamente en Google Sheets.")

# --- Mostrar datos históricos ---
st.header("📊 Datos históricos")
if df.empty:
    st.info("No hay datos aún.")
else:
    st.dataframe(df)

    # Filtrar por producto
    productos = df["producto"].unique().tolist()
    prod_seleccionado = st.selectbox("Selecciona un producto para análisis:", productos)

    df_prod = df[df["producto"] == prod_seleccionado]

    if len(df_prod) >= 2:
        pesos = df_prod["peso"].astype(float).values
        lsl_val = df_prod["lsl"].astype(float).iloc[-1]
        usl_val = df_prod["usl"].astype(float).iloc[-1]

        media = np.mean(pesos)
        std_dev = np.std(pesos, ddof=1)
        Cp = (usl_val - lsl_val) / (6 * std_dev)
        Cpk = min((usl_val - media), (media - lsl_val)) / (3 * std_dev)

        st.subheader("📈 Estadísticas del proceso")
        st.write(f"Media: **{media:.2f} g**")
        st.write(f"Desviación estándar: **{std_dev:.3f}**")
        st.write(f"**Cp**: {Cp:.3f}")
        st.write(f"**Cpk**: {Cpk:.3f}")

        # --- Gráfica de control ---
        st.subheader("📉 Gráfica de control")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(pesos, marker='o', linestyle='-', color='blue', label='Peso')
        ax.axhline(media, color='green', linestyle='--', label='Media')
        ax.axhline(media + 3*std_dev, color='red', linestyle='--', label='Límite superior (UCL)')
        ax.axhline(media - 3*std_dev, color='red', linestyle='--', label='Límite inferior (LCL)')
        ax.set_title(f'Gráfico de Control - {prod_seleccionado}')
        ax.set_xlabel("Muestra")
        ax.set_ylabel("Peso (g)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    else:
        st.warning("⚠️ Se necesitan al menos 2 registros del producto seleccionado para calcular Cp y Cpk.")
