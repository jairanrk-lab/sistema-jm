import streamlit as st

def aplicar_estilos_customizados():
    """
    Esta função injeta todo o CSS de design premium da JM DETAIL.
    """
    st.markdown("""
    <style>
        /* 1. FONTE POPPINS E ÍCONES */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
        
        * { font-family: 'Poppins', sans-serif !important; }
        
        /* --- FUNDO PRETO --- */
        [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { 
            background-color: #000000 !important; 
        }
        .block-container { padding-top: 1rem; padding-bottom: 6rem; }

        /* --- SUMIR COM A BARRA LATERAL --- */
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        [data-testid="stSidebar"] { display: none !important; }

        /* --- NAVEGAÇÃO SUPERIOR --- */
        div[role="radiogroup"] {
            display: flex;
            flex-direction: row;
            justify-content: center;
            background-color: #111;
            border-radius: 12px;
            padding: 5px;
            border: 1px solid #333;
            overflow-x: auto;
            gap: 8px;
        }
        
        div[role="radiogroup"] label {
            background-color: transparent !important;
            border: 1px solid transparent !important;
            padding: 10px 20px !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
            margin: 0 !important;
            color: #888 !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            white-space: nowrap !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* --- INJEÇÃO DOS ÍCONES BOOTSTRAP NO MENU --- */
        div[role="radiogroup"] label:nth-of-type(1)::before { font-family: "bootstrap-icons"; content: "\\F5A6"; margin-right: 8px; font-size: 16px; }
        div[role="radiogroup"] label:nth-of-type(2)::before { font-family: "bootstrap-icons"; content: "\\F20E"; margin-right: 8px; font-size: 16px; }
        div[role="radiogroup"] label:nth-of-type(3)::before { font-family: "bootstrap-icons"; content: "\\F23E"; margin-right: 8px; font-size: 16px; }
        div[role="radiogroup"] label:nth-of-type(4)::before { font-family: "bootstrap-icons"; content: "\\F4E9"; margin-right: 8px; font-size: 16px; }
        div[role="radiogroup"] label:nth-of-type(5)::before { font-family: "bootstrap-icons"; content: "\\F291"; margin-right: 8px; font-size: 16px; }

        /* Botão Selecionado e Hover */
        div[role="radiogroup"] label:hover { border-color: #D90429 !important; color: white !important; background-color: #1a1a1a !important; }
        div[role="radiogroup"] label[data-checked="true"] {
            background: linear-gradient(90deg, #D90429 0%, #8D021F 100%) !important;
            color: white !important;
            border-color: #D90429 !important;
            box-shadow: 0 0 12px rgba(217, 4, 41, 0.5) !important;
        }
        
        /* --- CARDS DASHBOARD --- */
        .dash-card { border-radius: 15px; padding: 20px; color: white; margin-bottom: 20px; border: 1px solid #333; position: relative; overflow: hidden; height: 140px !important; display: flex; flex-direction: column; justify-content: center; }
        .card-icon-bg { position: absolute !important; top: -10px !important; right: -10px !important; font-size: 100px !important; opacity: 0.15 !important; transform: rotate(15deg) !important; pointer-events: none !important; color: white !important; }
        
        /* CORES DOS CARDS */
        .bg-orange { background: linear-gradient(145deg, #FF9800, #F57C00); }
        .bg-blue { background: linear-gradient(145deg, #00B4DB, #0083B0); }
        .bg-red { background: linear-gradient(145deg, #D90429, #8D021F); }
        .bg-green { background: linear-gradient(145deg, #11998e, #38ef7d); }

        /* LISTAS (AGENDA/HISTÓRICO) */
        .agenda-card { background-color: #161616 !important; border-radius: 12px; padding: 15px; margin-bottom: 12px; border: 1px solid #333; border-left: 5px solid #00B4DB; }
        .history-card { background-color: #161616 !important; border-radius: 12px; padding: 15px; margin-bottom: 12px; border: 1px solid #333; }

        /* RODAPÉ */
        .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #000000; color: #666; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #222; z-index: 9999; }
        
        /* ESTILO DOS BOTÕES STREAMLIT */
        div.stButton > button { 
            background-color: #D90429 !important; 
            color: white !important; 
            border-radius: 8px !important; 
            font-weight: 700 !important; 
            border: none !important; 
            height: 45px !important; 
        }
    </style>
    """, unsafe_allow_html=True)
