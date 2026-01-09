st.markdown("""
<style>
    /* 1. IMPORTAÇÕES PADRÃO */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    * { font-family: 'Montserrat', sans-serif !important; }
    
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { background-color: #000000 !important; }
    .block-container { padding-bottom: 6rem; }

    /* ================================================================= */
    /* 2. O EXTERMINADOR DE ÍCONES (V10.17) */
    /* ================================================================= */

    /* PASSO 1: Ocultar TUDO que estiver na área dos botões de controle */
    [data-testid="stSidebarCollapsedControl"] *, 
    [data-testid="stSidebarHeader"] * {
        display: none !important; /* Some com texto, svg, span, div... tudo! */
    }

    /* PASSO 2: Manter apenas a área clicável (o container) invisível mas ativa */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarHeader"] {
        display: block !important;
        width: 50px !important;
        height: 50px !important;
        z-index: 99999 !important; /* Força ficar no topo pra receber o clique */
    }

    /* PASSO 3: Desenhar um NOVO Ícone "fake" por cima de tudo */
    /* Ícone de Menu (Quando fechado) */
    [data-testid="stSidebarCollapsedControl"]::after {
        content: "☰"; 
        font-size: 35px !important;
        color: #D90429 !important;
        position: absolute;
        top: 20px;
        left: 20px;
        pointer-events: none; /* O clique passa por ele e acerta o botão invisível embaixo */
    }

    /* Ícone de Fechar (Quando aberto) */
    [data-testid="stSidebarHeader"]::after {
        content: "✖"; 
        font-size: 25px !important;
        color: #666 !important;
        position: absolute;
        top: 20px;
        right: 20px;
        pointer-events: none;
    }

    /* ================================================================= */

    /* SIDEBAR RESPONSIVA */
    @media (min-width: 992px) { [data-testid="stSidebar"] { min-width: 300px !important; max-width: 350px !important; } }
    @media (max-width: 768px) { [data-testid="stSidebar"] { min-width: 220px !important; max-width: 85% !important; } }

    /* ESTILO DOS BOTÕES */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 15px 10px !important; background-color: #111111 !important; border: 1px solid #333 !important;
        color: #ddd !important; border-radius: 10px !important; margin-bottom: 10px !important; width: 100% !important;
        display: flex !important; align-items: center !important; justify-content: flex-start !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover { border-color: #D90429 !important; background-color: #1a1a1a !important; color: white !important; transform: scale(1.02); }
    [data-testid="stSidebar"] div[role="radiogroup"] [aria-checked="true"] { background: linear-gradient(90deg, #D90429 0%, #8D021F 100%) !important; color: white !important; border-color: #D90429 !important; }
    
    /* CAIXINHAS E CORES */
    .dash-card { border-radius: 15px; padding: 25px; color: white; margin-bottom: 20px; border: 1px solid #333; position: relative; overflow: hidden; height: 160px !important; display: flex; flex-direction: column; justify-content: center; }
    .card-icon-bg { position: absolute !important; top: -10px !important; right: -10px !important; font-size: 110px !important; opacity: 0.15 !important; transform: rotate(15deg) !important; pointer-events: none !important; color: white !important; }
    .agenda-card { background-color: #161616 !important; border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 6px solid #00B4DB; }
    .history-card { background-color: #161616 !important; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    
    .bg-orange { background: linear-gradient(145deg, #FF9800, #F57C00); }
    .bg-blue { background: linear-gradient(145deg, #00B4DB, #0083B0); }
    .bg-red { background: linear-gradient(145deg, #D90429, #8D021F); }
    .bg-green { background: linear-gradient(145deg, #11998e, #38ef7d); }
    .bg-purple { background: linear-gradient(145deg, #8E2DE2, #4A00E0); }
    .bg-dark { background: linear-gradient(145deg, #222, #111); }
    
    .custom-title { font-size: 2.5rem; font-weight: 800; color: white !important; margin-bottom: 25px; }
    div.stButton > button { background-color: #D90429 !important; color: white !important; border: none !important; height: 50px !important; font-size: 18px !important; border-radius: 8px !important; font-weight: 700 !important; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #000000; color: #888; text-align: center; padding: 15px; font-size: 14px; border-top: 1px solid #333; z-index: 9999; font-family: 'Montserrat', sans-serif; }
</style>
""", unsafe_allow_html=True)
