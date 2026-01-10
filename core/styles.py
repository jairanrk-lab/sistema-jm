import streamlit as st

def aplicar_estilos_customizados():
    st.markdown("""
        <style>
        /* Importando fonte Google Fonts (Montserrat) */
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
        
        /* Aplicando fonte em todo o site */
        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif;
        }
        
        /* Cor de fundo do app */
        .stApp {
            background-color: #0e1117;
        }
        
        /* Estilizando Botões */
        div.stButton > button {
            background-color: #00ADB5;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            background-color: #00FFF5;
            color: #000000;
            transform: scale(1.02);
        }

        /* Estilizando Métricas (Caixas de números) */
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            color: #00ADB5 !important;
        }
        
        /* Centralizando títulos */
        h1, h2, h3 {
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
