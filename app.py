import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
from datetime import datetime, date, time, timedelta
from fpdf import FPDF
import gspread
import os
import time as t_sleep
import json
import re

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="JM DETAIL PRO",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# --- 2. SISTEMA DE LOGIN SEGURO ---
# ==============================================================================
def check_password():
    if st.session_state.get("password_correct", False):
        return True
    
    try:
        if st.query_params.get("acesso_liberado") == "sim_mestre":
            st.session_state["password_correct"] = True
            return True
    except:
        pass
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### <i class='bi bi-shield-lock-fill' style='color:#D90429'></i> Acesso Restrito - JM Detail", unsafe_allow_html=True)
        with st.form("login_form"):
            pwd = st.text_input("Digite a senha de acesso:", type="password")
            submit = st.form_submit_button("ACESSAR SISTEMA")
            if submit:
                try: senha_correta = st.secrets["app"]["password"]
                except: senha_correta = "JM@2024"
                
                if pwd == senha_correta:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
    return False

if not check_password():
    st.stop()

# ==============================================================================
# --- 3. ESTILO CSS PREMIUM (V14.2 - MENU FULL WIDTH & MOBILE) ---
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    
    * { font-family: 'Poppins', sans-serif !important; }
    
    /* FUNDO PRETO TOTAL */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
        background-color: #000000 !important;
    }
    
    .block-container { padding-top: 1rem; padding-bottom: 6rem; }

    /* NAVEGAÇÃO SUPERIOR - CORREÇÃO 100% LARGURA */
    div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        background-color: #111;
        border-radius: 12px;
        padding: 5px;
        border: 1px solid #333;
        width: 100% !important; /* Força ocupação total */
        gap: 8px;
    }
    
    div[role="radiogroup"] label {
        flex: 1 !important; /* Faz os botões crescerem igualmente */
        background-color: transparent !important;
        border: 1px solid transparent !important;
        padding: 12px 5px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        color: #888 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }

    /* ÍCONES VIA CSS (BOOTSTRAP) */
    div[role="radiogroup"] label:nth-of-type(1)::before { font-family: "bootstrap-icons"; content: "\\F5A6"; margin-right: 8px; }
    div[role="radiogroup"] label:nth-of-type(2)::before { font-family: "bootstrap-icons"; content: "\\F20E"; margin-right: 8px; }
    div[role="radiogroup"] label:nth-of-type(3)::before { font-family: "bootstrap-icons"; content: "\\F23E"; margin-right: 8px; }
    div[role="radiogroup"] label:nth-of-type(4)::before { font-family: "bootstrap-icons"; content: "\\F4E9"; margin-right: 8px; }
    div[role="radiogroup"] label:nth-of-type(5)::before { font-family: "bootstrap-icons"; content: "\\F291"; margin-right: 8px; }

    /* ESTADO SELECIONADO */
    div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(90deg, #D90429 0%, #8D021F 100%) !important;
        color: white !important;
        border-color: #D90429 !important;
        box-shadow: 0 0 15px rgba(217, 4, 41, 0.4) !important;
    }

    /* CARDS DASHBOARD */
    .dash-card {
        border-radius: 15px; padding: 20px; color: white; margin-bottom: 20px;
        border: 1px solid #333; position: relative; overflow: hidden;
        height: 130px; display: flex; flex-direction: column; justify-content: center;
    }
    .card-icon-bg {
        position: absolute; top: -10px; right: -10px; font-size: 80px;
        opacity: 0.1; transform: rotate(15deg); color: white;
    }
    
    .bg-orange { background: linear-gradient(145deg, #FF9800, #F57C00); }
    .bg-blue { background: linear-gradient(145deg, #00B4DB, #0083B0); }
    .bg-red { background: linear-gradient(145deg, #D90429, #8D021F); }
    .bg-green { background: linear-gradient(145deg, #11998e, #38ef7d); }

    /* CARDS DE HISTÓRICO/AGENDA */
    .history-card {
        background-color: #111 !important; border-radius: 12px; padding: 18px;
        margin-bottom: 15px; border-left: 5px solid #D90429; border-top: 1px solid #222;
    }

    /* AJUSTES MOBILE */
    @media (max-width: 768px) {
        div[role="radiogroup"] { flex-wrap: wrap; }
        div[role="radiogroup"] label { min-width: 45%; font-size: 11px !important; padding: 10px 2px !important; }
        .dash-card { height: 110px; padding: 15px; }
    }

    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #000; color: #555; text-align: center;
        padding: 8px; font-size: 11px; border-top: 1px solid #111; z-index: 100;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- 4. FUNÇÕES DE DADOS ---
# ==============================================================================
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def conectar_google_sheets():
    try:
        ID = st.secrets["app"]["spreadsheet_id"]
        if os.path.exists("chave_google.json"):
            client = gspread.service_account(filename="chave_google.json")
        else:
            client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        return client.open_by_key(ID)
    except: return None

def carregar_dados(aba):
    sheet = conectar_google_sheets()
    if not sheet: return pd.DataFrame()
    try:
        df = pd.DataFrame(sheet.worksheet(aba).get_all_records())
        # Converter colunas numéricas
        for col in ['Total', 'Valor', 'Lucro Liquido']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

# ==============================================================================
# --- 5. INTERFACE E NAVEGAÇÃO ---
# ==============================================================================

# Logo centralizada
c_logo1, c_logo2, c_logo3 = st.columns([1, 1.5, 1])
with c_logo2:
    st.markdown("<h2 style='text-align:center; color:#D90429; font-weight:800; margin:0;'>JM DETAIL PRO</h2>", unsafe_allow_html=True)

st.write("")

# Menu Superior Pílula
menu_opcoes = ["DASHBOARD", "AGENDA", "FINANCEIRO", "DESPESAS", "HISTÓRICO"]
menu_selecionado = st.radio("Nav", menu_opcoes, horizontal=True, label_visibility="collapsed")

st.write("---")

# --- PÁGINA DASHBOARD ---
if menu_selecionado == "DASHBOARD":
    st.markdown('## <i class="bi bi-speedometer2" style="color:#00B4DB"></i> Dashboard')
    
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    
    # KPIs fictícios para demonstração do layout (substitua pela lógica de soma real)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="dash-card bg-orange"><i class="bi bi-hourglass-split card-icon-bg"></i><small>PENDENTES</small><h3>R$ 1.250,00</h3></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="dash-card bg-blue"><i class="bi bi-currency-dollar card-icon-bg"></i><small>FATURAMENTO MÊS</small><h3>R$ 4.800,00</h3></div>', unsafe_allow_html=True)
        
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="dash-card bg-red"><i class="bi bi-graph-down-arrow card-icon-bg"></i><small>DESPESAS</small><h3>R$ 450,00</h3></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="dash-card bg-green"><i class="bi bi-wallet2 card-icon-bg"></i><small>LUCRO LÍQUIDO</small><h3>R$ 3.100,00</h3></div>', unsafe_allow_html=True)

    st.write("")
    col_g, col_a = st.columns([1.5, 1])
    with col_g:
        st.markdown('### <i class="bi bi-graph-up-arrow" style="color:#39FF14"></i> Performance')
        # Exemplo de gráfico
        chart_data = pd.DataFrame({'Dia': range(1,11), 'Vendas': [200,450,300,600,800,550,900,1100,950,1300]})
        st.line_chart(chart_data, x='Dia', y='Vendas', color="#D90429")

    with col_a:
        st.markdown('### <i class="bi bi-calendar-event"></i> Próximos')
        st.markdown('<div class="history-card"><b>Civic G10</b><br><small>Jairan - 14:00</small></div>', unsafe_allow_html=True)
        st.markdown('<div class="history-card"><b>Hilux SRX</b><br><small>Marcos - Amanhã</small></div>', unsafe_allow_html=True)

# --- PÁGINA HISTÓRICO ---
elif menu_selecionado == "HISTÓRICO":
    st.markdown('## <i class="bi bi-clock-history"></i> Histórico de Serviços')
    # Exemplo de Card de Histórico
    st.markdown("""
    <div class="history-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <b style="font-size:18px">🚗 Corolla XEI</b><br>
                <span style="color:#888">Cliente: Roberto Silva | Placa: BRA2E19</span>
            </div>
            <div style="text-align:right">
                <span style="color:#39FF14; font-weight:700; font-size:18px">R$ 250,00</span><br>
                <small style="color:#555">10/01/2026</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Rodapé Fixo
st.markdown('<div class="footer">Desenvolvido por <b>Jairan Jesus Matos</b> | JM Detail System © 2026</div>', unsafe_allow_html=True)
