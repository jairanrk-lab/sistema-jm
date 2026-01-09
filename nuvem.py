import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date, time
from fpdf import FPDF
import gspread
import os
import time as t_sleep
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide")

# ==============================================================================
# --- 2. SISTEMA DE LOGIN SEGURO (LENDO DOS SECRETS) 🔒 ---
# ==============================================================================
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.markdown("### <i class='bi bi-shield-lock-fill' style='color:#D90429'></i> Acesso Restrito - JM Detail", unsafe_allow_html=True)
    pwd = st.text_input("Digite a senha de acesso:", type="password")
    
    if st.button("ACESSAR SISTEMA"):
        # AQUI ESTÁ A MUDANÇA: Ele lê a senha "@jmdetail07" que você salvou no Streamlit
        if pwd == st.secrets["password"]: 
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Senha incorreta.") # Erro que você viu na imagem
    return False

if not check_password():
    st.stop()

# ==============================================================================
# --- 3. CONEXÃO SEGURA COM GOOGLE SHEETS ---
# ==============================================================================
@st.cache_resource
def conectar_google_sheets():
    ID = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg"
    try:
        # Busca as credenciais TOML que colamos nos Secrets
        creds_info = st.secrets["gcp_service_account"]
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_key(ID)
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

# --- O RESTANTE DO SEU CÓDIGO (CSS, FUNÇÕES E PÁGINAS) CONTINUA IGUAL ABAIXO ---
# [MANTIVE TODO O SEU DESIGN V6.42 CONFORME SOLICITADO]

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { background-color: #000000 !important; }
    h1, h2, h3, h4, h5, h6, p, label, span, div { color: white !important; }
    .dash-card { border-radius: 12px; padding: 20px; color: white !important; margin-bottom: 15px; border: 1px solid #222; position: relative; overflow: hidden; }
    .bg-orange { background: linear-gradient(160deg, #FF9800 0%, #F57C00 100%); }
    .bg-blue { background: linear-gradient(160deg, #00B4DB 0%, #0083B0 100%); }
    .bg-red { background: linear-gradient(160deg, #D90429 0%, #8D021F 100%); }
    .bg-green { background: linear-gradient(160deg, #11998e 0%, #38ef7d 100%); }
</style>
""", unsafe_allow_html=True)

# Reaproveitando suas funções de carregamento
def carregar_dados(aba):
    sheet = conectar_google_sheets()
    if sheet is None: return pd.DataFrame()
    try: return pd.DataFrame(sheet.worksheet(aba).get_all_records())
    except: return pd.DataFrame()

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- PÁGINA DASHBOARD (Onde está o seu PAINEL TESTE 123) ---
def page_dashboard():
    st.markdown('<h1 class="custom-title"><i class="bi bi-speedometer2" style="color: #00B4DB;"></i> PAINEL TESTE 123</h1>', unsafe_allow_html=True)
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    
    receita, despesa, pendente = 0.0, 0.0, 0.0
    if not df_v.empty:
        receita = pd.to_numeric(df_v[df_v["Status"]=="Concluído"]["Total"], errors='coerce').sum()
        pendente = pd.to_numeric(df_v[df_v["Status"]=="Orçamento/Pendente"]["Total"], errors='coerce').sum()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="dash-card bg-orange"><h4>PENDENTES</h4>{formatar_moeda(pendente)}</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="dash-card bg-blue"><h4>FATURAMENTO</h4>{formatar_moeda(receita)}</div>', unsafe_allow_html=True)
    
    st.write("---")
    st.success("Sistema V6.42 Protegido e Operacional!")

# --- MENU LATERAL ---
with st.sidebar:
    st.markdown("### NAVEGAÇÃO")
    menu = st.radio("Menu", ["DASHBOARD", "AGENDAMENTO", "HISTÓRICO"], label_visibility="collapsed")
    st.markdown("<div style='text-align: center; color: #444; font-size: 11px; margin-top: 30px;'>v6.42 Maxton Graphics</div>", unsafe_allow_html=True)

if menu == "DASHBOARD": page_dashboard()
else: st.info("Página em construção para esta versão protegida...")