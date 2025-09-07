import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Control de peso - Línea de producción")

productos = ['Super', 'Barra', 'Brilla King', 'Lima fresca 250', 'Edén 300', 'Cepillo']
producto = st.selectbox("Producto:", productos)

cantidad = st.number_input("Cantidad de pesos:", min_value=1, max_value=100, value=5)

pesos = []
for i in range(cantidad):
    peso = st.number_input(f"Peso {i+1}:", min_value=0.0, format="%.3f")
    pesos.append(peso)

lsl = st.number_input("Límite inferior (LSL):", format="%.3f")
usl = st.number_input("Límite superior (USL):", format="%.3f")

if st.button("Calcular Cp y Cpk"):
    pesos_arr = np.array(pesos)
    
    if 0 in pesos_arr:
        st.error("Por favor ingresa todos los pesos (no pueden ser cero).")
    elif lsl >= usl:
        st.error("El Límite Inferior (LSL) debe ser menor que el Límite Superior (USL).")
    else:
        media = np.mean(pesos_arr)
        std_dev = np.std(pesos_arr, ddof=1)

        Cp = (usl - lsl) / (6 * std_dev) if std_dev != 0 else float('inf')
        Cpk = min((usl - media), (media - lsl)) / (3 * std_dev) if std_dev != 0 else float('inf')

        st.write(f"**Producto:** {producto}")
        st.write(f"**Cantidad de datos:** {len(pesos)}")
        st.write(f"**Media:** {media:.3f}")
        st.write(f"**Desviación estándar:** {std_dev:.3f}")
        st.write(f"**Cp:** {Cp:.3f}")
        st.write(f"**Cpk:** {Cpk:.3f}")

        fig, ax = plt.subplots()
        ax.plot(pesos_arr, marker='o', linestyle='-', color='blue')
        ax.axhline(media, color='green', linestyle='--', label='Media')
        ax.axhline(media + 3*std_dev, color='red', linestyle='--', label='Límite superior (UCL)')
        ax.axhline(media - 3*std_dev, color='red', linestyle='--', label='Límite inferior (LCL)')
        ax.set_title(f"Gráfica de Control - {producto}")
        ax.set_xlabel("Índice de muestra")
        ax.set_ylabel("Peso")
        ax.legend()
        st.pyplot(fig)

