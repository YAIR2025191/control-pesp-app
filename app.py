import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials

# Configura las credenciales y acceso
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credenciales.json", scopes=scope)
client = gspread.authorize(creds)

# Abrir hoja por URL y seleccionar worksheet
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1jzNLXGsxc6orLQ1-IajlFka9ViEdc9nbC9POPnejxzs/edit#gid=0")
worksheet = sheet.worksheet("Hoja 1")

# Leer datos actuales
data = worksheet.get_all_records()
df = pd.DataFrame(data)

st.title("Control de Peso")

producto = st.text_input("Producto")
peso = st.number_input("Peso (g)", min_value=0.0, step=0.1)
lsl = st.number_input("LSL", min_value=0.0, step=0.1)
usl = st.number_input("USL", min_value=0.0, step=0.1)

if st.button("Guardar"):
    if producto and peso > 0 and lsl > 0 and usl > 0 and lsl < usl:
        worksheet.append_row([producto, peso, lsl, usl])
        st.success("Datos guardados!")
        st.experimental_rerun()
    else:
        st.error("Revisa que todos los campos estén completos y sean correctos.")

st.header("Datos históricos")
if df.empty:
    st.info("No hay datos aún.")
else:
    st.dataframe(df)

    productos = df["producto"].unique().tolist()
    prod = st.selectbox("Producto para análisis", productos)
    df_prod = df[df["producto"] == prod]

    if len(df_prod) >= 2:
        pesos = df_prod["peso"].astype(float)
        media = pesos.mean()
        std = pesos.std(ddof=1)
        lsl_val = df_prod["lsl"].astype(float).iloc[-1]
        usl_val = df_prod["usl"].astype(float).iloc[-1]
        Cp = (usl_val - lsl_val) / (6 * std)
        Cpk = min(usl_val - media, media - lsl_val) / (3 * std)

        st.write(f"Media: {media:.2f}")
        st.write(f"Desviación estándar: {std:.3f}")
        st.write(f"Cp: {Cp:.3f}")
        st.write(f"Cpk: {Cpk:.3f}")

        fig, ax = plt.subplots()
        ax.plot(pesos.values, marker='o')
        ax.axhline(media, color='green', linestyle='--')
        ax.axhline(media + 3*std, color='red', linestyle='--')
        ax.axhline(media - 3*std, color='red', linestyle='--')
        st.pyplot(fig)
    else:
        st.warning("Se necesitan al menos 2 registros para análisis.")
