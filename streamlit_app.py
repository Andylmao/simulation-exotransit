import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.animation as animation
import matplotlib as mpl
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
mpl.style.use('dark_background')

# Configuración de estilo
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
            url = 'https://raw.githubusercontent.com/Andylmao/simulation-exotransit/56c8235b14ccb796fee16eb83dfe8999254c5d75/planetas_consolidadosGauss.csv'
            df = pd.read_csv(url)
            
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
    - Modifica los parámetros para observar cómo afectan la órbita y la curva de luz del exoplaneta 
                        \n - Después inicia la simulación 🚀🌕
                        \n - Debajo puedes observar una gráfica que muestra un histórico de descubrimiento de exoplanetas 📡🪐
    """)
    
    Radio_star = 10
    Rpf = st.sidebar.slider("Radio del planeta / Radio estrella", 0.01, 0.4, 0.1, 0.01)
    Radio_planet = Rpf * Radio_star

    R_orbf = st.sidebar.slider("Radio orbital", 2.0, 10.0, 5.0, 0.1)
    Orbita = R_orbf * Radio_star

    Angulo_inclinacion = st.sidebar.slider("Inclinación (grados)", -90, 90, 0, 1)
    Inclinacion = np.radians(90 + Angulo_inclinacion)

    Pasos = 70
    Caja = 1.5 * Orbita

    # Configuración de la figura para la animación
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 5))
    
    # Configurar subplot 1 (órbita)
    ax1.set_xlim(-Caja, Caja)
    ax1.set_ylim(-Caja, Caja)
    ax1.set_aspect('equal')
    ax1.set_title("Órbita del planeta", color='white')
    ax1.set_facecolor("#0a0f2c")
    ax1.tick_params(colors='white')
    
    # Configurar subplot 2 (curva de luz)
    ax2.set_xlim(0, Pasos)
    ax2.set_ylim(83, 101)  # Rango ajustado para mejor visualización
    ax2.set_title("Curva de luz simulada", color='white')
    ax2.set_xlabel("Tiempo (frames)", color='white')
    ax2.set_ylabel("Brillo (%)", color='white')
    ax2.set_facecolor("#0a0f2c")
    ax2.tick_params(colors='white')
    
    # Dibujar estrella fija
    estrella = Circle((0, 0), Radio_star, color='#FFD700')
    ax1.add_patch(estrella)
    
    # Inicializar elementos de la animación
    planeta = Circle((0, 0), Radio_planet, color='#8A2BE2')
    ax1.add_patch(planeta)
    line, = ax2.plot([], [], color='#00BFFF')
    point = ax2.scatter([], [], color='#7CFC00', zorder=5)
    
    # Función de inicialización
    def init():
        planeta.center = (0, 0)
        line.set_data([], [])
        point.set_offsets(np.empty((0, 2)))
        return planeta, line, point
    
    # Función de animación
    def animate(frame):
        theta = 2 * np.pi * frame / Pasos
        x = np.cos(theta) * Orbita
        y = np.sin(theta) * Orbita * np.cos(Inclinacion)
        z = np.sin(theta) * Orbita

        if z > 0:
            brillo_val = 100
        else:
            inter = area_interseccion_circulos(0, 0, Radio_star, x, y, z, Radio_planet)
            brillo_val = 100 * (1 - inter / (np.pi * Radio_star**2))
        
        # Actualizar posición del planeta
        planeta.center = (x, y)
        
        # Actualizar curva de luz
        x_data = np.arange(frame + 1)
        y_data = [100] * (frame + 1)  # Valor inicial
        for i in range(frame + 1):
            theta_i = 2 * np.pi * i / Pasos
            z_i = np.sin(theta_i) * Orbita
            if z_i <= 0:
                x_i = np.cos(theta_i) * Orbita
                y_i = np.sin(theta_i) * Orbita * np.cos(Inclinacion)
                inter_i = area_interseccion_circulos(0, 0, Radio_star, x_i, y_i, z_i, Radio_planet)
                y_data[i] = 100 * (1 - inter_i / (np.pi * Radio_star**2))
        
        line.set_data(x_data, y_data)
        point.set_offsets([[frame, brillo_val]])
        
        return planeta, line, point
    
    # Botón para iniciar simulación
    if st.sidebar.button("▶ Iniciar simulación"):
        # Crear la animación
        with st.spinner('⏳ Generando animación de tránsito...'):
            ani = animation.FuncAnimation(
                fig, animate, frames=Pasos,
                init_func=init, blit=True, interval=50, repeat=False
            )
            html_anim = ani.to_jshtml()
            
        # Mostrar la animación
        components.html(ani.to_jshtml(), height=600)
    
    # =============================================================================
    # SECCIÓN DE EXOPLANETAS DESCUBIERTOS
    # =============================================================================
    st.markdown("---")
    st.markdown('<div class="header-box"><h2>📊 Exoplanetas Descubiertos: Masa vs Período Orbital</h2></div>', unsafe_allow_html=True)
    
    df = load_exoplanet_data()
    
    if not df.empty:
        min_year = int(df['disc_year'].min())
        max_year = int(df['disc_year'].max())
        current_year = 2025
        
        col_controls, col_metrics = st.columns([1, 3])
        
        with col_controls:
            selected_year = st.slider(
                "Año de descubrimiento",
                min_value=min_year,
                max_value=current_year,
                value=min_year,
                key="year_slider",
                format="%d"
            )
        
        with col_metrics:
            df_filtered = df[df['disc_year'] <= selected_year]
            planets_count = len(df_filtered)
            years_covered = selected_year - min_year + 1
            avg_per_year = planets_count / years_covered if years_covered > 0 else 0
            
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
        
        fig2, ax = plt.subplots(figsize=(10, 6))
        fig2.patch.set_facecolor('#0a0f2c')
        ax.set_facecolor('#0a0f2c')
        ax.set_xscale('log')
        ax.set_yscale('log')
        
        method_colors = {
            'Transit': '#FFD700',
            'Radial Velocity': '#8A2BE2',
            'Microlensing': '#00BFFF',
            'Imaging': '#7CFC00',
            'Pulsar Timing': '#FF6347',
            'Timing': '#FF6347',
            'Other': '#A9A9A9'
        }
        
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
        
        ax.axhline(y=1, color='white', linestyle='--', alpha=0.3)
        ax.axhline(y=317.83, color='white', linestyle='--', alpha=0.3)
        ax.axvline(x=365, color='white', linestyle='--', alpha=0.3)
        ax.axvline(x=1, color='white', linestyle='--', alpha=0.3)
        
        ax.text(0.5, 0.5, 'Tierra', color='white', alpha=0.7, fontsize=9, 
                transform=ax.get_yaxis_transform(), va='center')
        ax.text(0.5, 317.83*1.1, 'Júpiter', color='white', alpha=0.7, fontsize=9,
                transform=ax.get_yaxis_transform(), va='bottom')
        ax.text(1.2, 0.02, '1 día', color='white', alpha=0.7, fontsize=9, rotation=90)
        ax.text(400, 0.02, '1 año', color='white', alpha=0.7, fontsize=9, rotation=90)
        
        ax.set_xlabel("Período Orbital (días, escala log)", fontsize=12, color='white')
        ax.set_ylabel("Masa del Planeta (Masas Terrestres, escala log)", fontsize=12, color='white')
        ax.set_title(f"Exoplanetas descubiertos hasta {selected_year}", fontsize=16, color='white')
        
        ax.legend(
            loc='upper right',
            facecolor='#1a1f4c',
            edgecolor='none',
            fontsize=10,
            framealpha=0.7
        )
        
        ax.set_xlim(0.1, 10000)
        ax.set_ylim(0.1, 1000000)
        ax.grid(True, which="both", ls="--", color='#2a2f5c', alpha=0.5)
        
        st.pyplot(fig2, use_container_width=True)
        plt.close(fig2)
        
        st.caption("Nota: Los datos muestran exoplanetas confirmados. Lineas rectas debido a valores sin cálculo de masa")
    else:
        st.warning("No se encontraron datos de exoplanetas para mostrar.")

if __name__ == "__main__":
    main()