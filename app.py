import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gspread

# --- Conectar con Google Sheet pública (requiere que tenga permiso de edición para "cualquiera con el enlace") ---
gc = gspread.Client(auth=None)
gc.session = gc.authenticated_session
sheet_url = "https://docs.google.com/spreadsheets/d/1jzNLXGsxc6orLQ1-IajlFka9ViEdc9nbC9POPnejxzs/edit#gid=0"
sh = gc.open_by_url(sheet_url)
worksheet = sh.get_worksheet(0)  # Primera hoja

# Cargar datos existentes
data = worksheet.get_all_records()
df = pd.DataFrame(data)

st.set_page_config(page_title="Control de Peso", layout="centered")
st.title("📊 Control de Peso - Línea de Producción")

# --- Entrada de datos ---
st.header("📥 Ingreso de datos")
producto = st.text_input("Producto")
peso = st.number_input("Peso (g)", min_value=0.0, step=0.1)
lsl = st.number_input("LSL - Límite inferior", min_value=0.0, step=0.1)
usl = st.number_input("USL - Límite superior", min_value=0.0, step=0.1)

# --- Guardar datos ---
if st.button("Guardar datos"):
    if not producto:
        st.error("⚠️ Debes ingresar el nombre del producto.")
    elif peso == 0 or lsl == 0 or usl == 0:
        st.error("⚠️ Peso, LSL y USL deben ser mayores que 0.")
    elif lsl >= usl:
        st.error("⚠️ LSL debe ser menor que USL.")
    else:
        nuevo = [producto, peso, lsl, usl]
        worksheet.append_row(nuevo)
        st.success("✅ Datos guardados exitosamente.")
        st.experimental_rerun()

# --- Mostrar datos históricos ---
st.header("📊 Datos históricos")
df = pd.DataFrame(worksheet.get_all_records())

if df.empty:
    st.info("No hay datos aún.")
else:
    st.dataframe(df)

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

        st.subheader("📉 Gráfica de control")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(pesos, marker='o', linestyle='-', color='blue', label='Peso')
        ax.axhline(media, color='green', linestyle='--', label='Media')
        ax.axhline(media + 3*std_dev, color='red', linestyle='--', label='UCL')
        ax.axhline(media - 3*std_dev, color='red', linestyle='--', label='LCL')
        ax.set_title(f'Gráfico de Control - {prod_seleccionado}')
        ax.set_xlabel("Muestra")
        ax.set_ylabel("Peso (g)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning("⚠️ Se necesitan al menos 2 registros para análisis.")
