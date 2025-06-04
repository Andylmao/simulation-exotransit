import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import time
import matplotlib as mpl
import pandas as pd
import matplotlib.colors as mcolors
st.set_page_config(layout="wide")
mpl.style.use('dark_background')

st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: white;
    }
    .stSlider > div > div > div[role="slider"] {
        background-color: #8A2BE2 !important;
    }
    .metric-box {
        background-color: #1a1f4c;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #8A2BE2;
    }
    .header-box {
        background-color: #1a1f4c;
        border-radius: 10px;
        padding: 10px 15px;
        margin-bottom: 20px;
        border-left: 5px solid #8A2BE2;
    }
    </style>
""", unsafe_allow_html=True)

def area_interseccion_circulos(x1, y1, r1, x2, y2, z1, r2):
    d = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if d >= r1 + r2:
        return 0
    elif d <= abs(r1 - r2) and z1 < 0:
        return np.pi * (r2**2)
    elif d <= abs(r1 - r2) and z1 >= 0:
        return 0
    else:
        a = (r1**2 - r2**2 + d**2) / (2 * d)
        h = np.sqrt(r1**2 - a**2)
        term1 = r1**2 * np.arccos((d**2 + r1**2 - r2**2) / (2 * d * r1))
        term2 = r2**2 * np.arccos((d**2 + r2**2 - r1**2) / (2 * d * r2))
        term3 = 0.5 * np.sqrt((-d + r1 + r2)*(d + r1 - r2)*(d - r1 + r2)*(d + r1 + r2))
        return term1 + term2 - term3

def main():
    # Estado para la simulación
    if "mostrar_info" not in st.session_state:
        st.session_state.mostrar_info = True

    # Cargar datos de exoplanetas
    @st.cache_data
    def load_exoplanet_data():
        try:
            # Reemplaza con la ruta real de tu archivo CSV
            url = 'https://raw.githubusercontent.com/Andylmao/simulation-exotransit/56c8235b14ccb796fee16eb83dfe8999254c5d75/planetas_consolidadosGauss.csv'
            df = pd.read_csv(url)
            
            # Limpieza básica de datos
            expected_columns = ['disc_year', 'discoverymethod', 'pl_bmasse', 'pl_orbper']
            if not all(col in df.columns for col in expected_columns):
                raise ValueError("Faltan columnas necesarias en el archivo CSV.")
            
           
            
            return df
        except Exception as e:
            st.error(f"Error cargando datos de exoplanetas: {str(e)}")
            return pd.DataFrame()

    # Iniciar simulación de tránsito
    st.title("🪐 Simulación de Tránsito de Exoplaneta en Tiempo Real")
    
    if st.session_state.mostrar_info:
        with st.expander("ℹ️ Sugerencia de visualización", expanded=True):
            st.markdown("💡 Puedes maximizar las gráficas usando el ícono 🔳 en la esquina superior de la gráfica")
    
    st.sidebar.header("⚙️ Parámetros de Simulación")
    st.sidebar.markdown("""
    Modifica los parámetros para observar cómo afectan la órbita y la curva de luz del exoplaneta.
    """)
    
    Radio_star = 10
    Rpf = st.sidebar.slider("Radio del planeta / Radio estrella", 0.01, 0.4, 0.1, 0.01)
    Radio_planet = Rpf * Radio_star

    R_orbf = st.sidebar.slider("Radio orbital", 2.0, 10.0, 5.0, 0.1)
    Orbita = R_orbf * Radio_star

    Angulo_inclinacion = st.sidebar.slider("Inclinación (grados)", -90, 90, 0, 1)
    Inclinacion = np.radians(90 + Angulo_inclinacion)


    
    Pasos = 100
    Caja = 1.5 * Orbita

    placeholder = st.empty()
    brillo = []

    # Ejecutar simulación de tránsito
    # Primer frame antes de la animación
    theta = 0
    x = np.cos(theta) * Orbita
    y = np.sin(theta) * Orbita * np.cos(Inclinacion)
    z = np.sin(theta) * Orbita

    inter = area_interseccion_circulos(0, 0, Radio_star, x, y, z, Radio_planet)
    brillo_val = 100 if z > 0 else 100 * (1 - inter / (np.pi * Radio_star**2))
    brillo = [brillo_val]

    fig, axs = plt.subplots(1, 2, figsize=(18, 10))
    axs = axs.flatten()

    # Subplot 1: órbita
    axs[0].set_xlim(-Caja, Caja)
    axs[0].set_ylim(-Caja, Caja)
    axs[0].set_aspect('equal')
    axs[0].set_title("Órbita del planeta", color='white')
    axs[0].set_facecolor("#0a0f2c")
    axs[0].tick_params(colors='white')
    estrella = Circle((0, 0), Radio_star, color='#FFD700')
    planeta = Circle((x, y), Radio_planet, color='#8A2BE2')
    axs[0].add_patch(estrella)
    axs[0].add_patch(planeta)

    # Subplot 2: curva de luz
    axs[1].set_xlim(0, Pasos)
    axs[1].set_ylim(brillo_val - 0.5, 101)
    axs[1].set_title("Curva de luz simulada", color='white')
    axs[1].set_xlabel("Tiempo (frames)", color='white')
    axs[1].set_ylabel("Brillo (%)", color='white')
    axs[1].set_facecolor("#0a0f2c")
    axs[1].tick_params(colors='white')
    axs[1].plot(brillo, color='#00BFFF')
    axs[1].scatter(0, brillo_val, color='#7CFC00', zorder=5)

    placeholder = st.empty()
    placeholder.pyplot(fig, use_container_width=True)
    plt.close(fig)

# Botón para iniciar simulación
    start_sim = st.sidebar.button("▶ Iniciar simulación")

    if start_sim:
        brillo = []
        for frame in range(Pasos):
            theta = 2 * np.pi * frame / Pasos
            x = np.cos(theta) * Orbita
            y = np.sin(theta) * Orbita * np.cos(Inclinacion)
            z = np.sin(theta) * Orbita

            if z > 0:
                brillo_val = 100
            else:
                inter = area_interseccion_circulos(0, 0, Radio_star, x, y, z, Radio_planet)
                brillo_val = 100 * (1 - inter / (np.pi * Radio_star**2))  
            brillo.append(brillo_val)

            fig, axs = plt.subplots(1, 2, figsize=(18, 10))
            axs = axs.flatten()

            axs[0].set_xlim(-Caja, Caja)
            axs[0].set_ylim(-Caja, Caja)
            axs[0].set_aspect('equal')
            axs[0].set_title("Órbita del planeta", color='white')
            axs[0].set_facecolor("#0a0f2c")
            axs[0].tick_params(colors='white')
            estrella = Circle((0, 0), Radio_star, color='#FFD700')
            planeta = Circle((x, y), Radio_planet, color='#8A2BE2')
            axs[0].add_patch(estrella)
            axs[0].add_patch(planeta)
            
            

            axs[1].set_xlim(0, Pasos)
            axs[1].set_ylim(min(brillo) - 0.5, 101)
            axs[1].set_title("Curva de luz simulada", color='white')
            axs[1].set_xlabel("Tiempo (frames)", color='white')
            axs[1].set_ylabel("Brillo (%)", color='white')
            axs[1].set_facecolor("#0a0f2c")
            axs[1].tick_params(colors='white')
            axs[1].plot(brillo, color='#00BFFF')
            axs[1].scatter(frame, brillo_val, color='#7CFC00', zorder=5)

            placeholder.pyplot(fig, use_container_width=True)
            plt.close(fig)
            time.sleep(0.02)
    
    # =============================================================================
    # NUEVA SECCIÓN: VISUALIZACIÓN DE EXOPLANETAS DESCUBIERTOS (MASA vs PERÍODO)
    # =============================================================================
    st.markdown("---")
    st.markdown('<div class="header-box"><h2>📊 Exoplanetas Descubiertos: Masa vs Período Orbital</h2></div>', unsafe_allow_html=True)
    
    # Cargar datos de exoplanetas
    df = load_exoplanet_data()
    
    if not df.empty:
        # Calcular el rango de años
        min_year = int(df['disc_year'].min())
        max_year = int(df['disc_year'].max())
        current_year = 2025  # Puedes cambiarlo al año actual si prefieres
        
        # Crear columnas para controles y métricas
        col_controls, col_metrics = st.columns([1, 3])
        
        with col_controls:
            # Slider para seleccionar el año
            selected_year = st.slider(
                "Año de descubrimiento",
                min_value=min_year,
                max_value=current_year,
                value=min_year,
                key="year_slider",
                format="%d"
            )
            
            # Selector para métodos de descubrimiento
            #methods = df['discoverymethod'].dropna().unique()
            #selected_methods = st.multiselect(
            #    "Métodos de descubrimiento",
            #    options=methods,
            #    default=methods,
            #    key="method_selector"
            #)
            
            # Mostrar información sobre métodos
            #st.markdown("""
            #<div class="metric-box">
            #    <p><strong>Métodos de descubrimiento:</strong></p>
            #    <p>● Transit: Tránsito</p>
            #    <p>● Radial Velocity: Velocidad Radial</p>
            #    <p>● Microlensing: Microlente</p>
            #    <p>● Imaging: Imagen directa</p>
            #    <p>● Timing: Púlsar/Timing</p>
            #    <p>● Other: Otros métodos</p>
            #</div>
            #""", unsafe_allow_html=True)
        
        with col_metrics:
            # Filtrar datos hasta el año seleccionado
            df_filtered = df[df['disc_year'] <= selected_year]

                             
            
            # Calcular estadísticas
            planets_count = len(df_filtered)
            years_covered = selected_year - min_year + 1
            avg_per_year = planets_count / years_covered if years_covered > 0 else 0
            
            # Mostrar métricas
            col1, col2, col3 = st.columns(3)
            with col2:
                st.markdown(f'<div class="metric-box"><h3>🌍 {planets_count}</h3><p>Exoplanetas descubiertos</p></div>', 
                           unsafe_allow_html=True)
            with col1:
                st.markdown(f'<div class="metric-box"><h3>📅 {selected_year}</h3><p>Año seleccionado</p></div>', 
                           unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-box"><h3>📈 {avg_per_year:.1f}</h3><p>Promedio por año</p></div>', 
                           unsafe_allow_html=True)
        
        # Crear figura principal
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('#0a0f2c')
        ax.set_facecolor('#0a0f2c')
        
        # Configurar escalas logarítmicas
        ax.set_xscale('log')
        ax.set_yscale('log')
        
        # Definir colores por método de descubrimiento
        method_colors = {
            'Transit': '#FFD700',      # Amarillo
            'Radial Velocity': '#8A2BE2',  # Morado
            'Microlensing': '#00BFFF',     # Azul claro
            'Imaging': '#7CFC00',       # Verde
            'Pulsar Timing': '#FF6347', # Rojo anaranjado
            'Timing': '#FF6347',        # Rojo anaranjado
            'Other': '#A9A9A9'          # Gris
        }
        
        # Crear dispersión
        for method, color in method_colors.items():
            subset = df_filtered[df_filtered['discoverymethod'] == method]
            ax.scatter(
                subset['pl_orbper'],
                subset['pl_bmasse'],
                s=20,
                color=color,
                label=method,
                alpha=0.6,
                edgecolors='none'
            )
        
        # Líneas de referencia para planetas
        ax.axhline(y=1, color='white', linestyle='--', alpha=0.3)
        ax.axhline(y=317.83, color='white', linestyle='--', alpha=0.3)  # 1 Júpiter
        ax.axvline(x=365, color='white', linestyle='--', alpha=0.3)     # 1 año
        ax.axvline(x=1, color='white', linestyle='--', alpha=0.3)       # 1 día
        
        # Etiquetas de referencia
        ax.text(0.5, 0.5, 'Tierra', color='white', alpha=0.7, fontsize=9, 
                transform=ax.get_yaxis_transform(), va='center')
        ax.text(0.5, 317.83*1.1, 'Júpiter', color='white', alpha=0.7, fontsize=9,
                transform=ax.get_yaxis_transform(), va='bottom')
        ax.text(1.2, 0.02, '1 día', color='white', alpha=0.7, fontsize=9, rotation=90)
        ax.text(400, 0.02, '1 año', color='white', alpha=0.7, fontsize=9, rotation=90)
        
        # Etiquetas de ejes
        ax.set_xlabel("Período Orbital (días, escala log)", fontsize=12, color='white')
        ax.set_ylabel("Masa del Planeta (Masas Terrestres, escala log)", fontsize=12, color='white')
        ax.set_title(f"Exoplanetas descubiertos hasta {selected_year}", fontsize=16, color='white')
        
        # Leyenda
        ax.legend(
            loc='upper right',
            facecolor='#1a1f4c',
            edgecolor='none',
            fontsize=10,
            framealpha=0.7
        )
        
        # Límites de ejes
        ax.set_xlim(0.1, 10000)
        ax.set_ylim(0.1, 1000000)
        
        # Cuadrícula
        ax.grid(True, which="both", ls="--", color='#2a2f5c', alpha=0.5)
        
        # Mostrar gráfico
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        
        # Pie de página
        st.caption("Nota: Los datos muestran exoplanetas confirmados. Lineas rectas debido a valores sin cálculo de masa")
    else:
        st.warning("No se encontraron datos de exoplanetas para mostrar.")

if __name__ == "__main__":
    main()