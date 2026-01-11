import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date, time
from fpdf import FPDF
import gspread
import os
import time as t_sleep
import re 
import urllib.parse

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# --- 2. SISTEMA DE LOGIN PERSISTENTE ---
# ==============================================================================
def check_password():
    if st.session_state.get("password_correct", False):
        return True
    if st.query_params.get("logado") == "true":
        st.session_state["password_correct"] = True
        return True
    try:
        if st.query_params.get("acesso_liberado") == "sim_mestre":
            return True
    except: pass
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### <i class='bi bi-shield-lock-fill' style='color:#D90429'></i> Acesso Restrito - JM Detail", unsafe_allow_html=True)
        with st.form("login_form"):
            pwd = st.text_input("Digite a senha de acesso:", type="password")
            submit = st.form_submit_button("ACESSAR SISTEMA")
            if submit:
                try: senha_correta = st.secrets["app"]["password"]
                except: senha_correta = "1234"
                if pwd == senha_correta: 
                    st.session_state["password_correct"] = True
                    st.query_params["logado"] = "true"
                    st.rerun()
                else: st.error("Senha incorreta.")
    return False

if not check_password(): st.stop()

# ==============================================================================
# --- 3. ESTILO CSS (APPLE NATIVE + POLIMENTO LOGO) ---
# ==============================================================================
st.markdown("""
<style>
    /* FONTE NATIVA */
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    * { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important; }
    
    /* FUNDO GERAL COM GRADIENTE PROFUNDO */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #000000 80%);
    }
    .block-container { padding-top: 0.5rem; padding-bottom: 6rem; }
    [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebar"] { display: none !important; }
    #MainMenu, footer {visibility: hidden;}

    /* 💎 POLIMENTO DA LOGO (EFEITO VITRIFICADO) 💎 */
    [data-testid="stImage"] {
        filter: drop-shadow(0px 0px 15px rgba(217, 4, 41, 0.35)) brightness(1.2) contrast(1.1);
        transition: all 0.5s ease;
        padding: 10px 0;
    }
    [data-testid="stImage"]:hover {
        filter: drop-shadow(0px 0px 25px rgba(217, 4, 41, 0.6)) brightness(1.4);
        transform: scale(1.02);
    }

    /* INPUTS "GLASS" */
    input[type="text"], input[type="number"], input[type="date"], input[type="time"], .stSelectbox > div > div, .stMultiSelect > div > div {
        background-color: rgba(30, 30, 30, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important; border-radius: 10px !important;
        backdrop-filter: blur(5px) !important;
    }
    .stTextInput > div > div[data-baseweb="input"]:focus-within { border-color: #D90429 !important; box-shadow: 0 0 0 1px #D90429 !important; }

    /* MENU SUPERIOR (BLINDADO) */
    div[role="radiogroup"] { display: flex !important; width: 100% !important; justify-content: space-between !important; background: transparent !important; border: none !important; padding: 0 !important; gap: 8px !important; }
    div[role="radiogroup"] label {
        flex: 1 !important; background-color: rgba(30, 30, 30, 0.4) !important; backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; padding: 12px 2px !important; border-radius: 12px !important; transition: all 0.2s ease !important;
        margin: 0 !important; color: #aaa !important; font-weight: 500 !important; font-size: 14px !important; 
        white-space: nowrap !important; display: flex; align-items: center; justify-content: center !important;
    }
    div[role="radiogroup"] label:hover { border-color: #D90429 !important; color: white !important; background-color: rgba(217, 4, 41, 0.15) !important; }
    div[role="radiogroup"] label[data-checked="true"] { 
        background: linear-gradient(135deg, rgba(217, 4, 41, 0.8), rgba(141, 2, 31, 0.8)) !important; 
        backdrop-filter: blur(12px) !important; color: white !important; border-color: rgba(255,255,255,0.2) !important; 
        box-shadow: 0 4px 15px rgba(217, 4, 41, 0.3) !important; font-weight: 700 !important;
    }
    
    /* CARDS ESTILO VIDRO */
    .dash-card { 
        border-radius: 18px; padding: 20px; color: white; margin-bottom: 20px; position: relative; overflow: hidden; height: 140px !important; 
        display: flex; flex-direction: column; justify-content: center; border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    .card-icon-bg { position: absolute !important; top: -10px !important; right: -10px !important; font-size: 100px !important; opacity: 0.1 !important; transform: rotate(15deg) !important; pointer-events: none !important; color: white !important; }
    
    .bg-orange { background: linear-gradient(135deg, rgba(255, 152, 0, 0.3), rgba(245, 124, 0, 0.1)); border-top: 1px solid rgba(255, 152, 0, 0.5); }
    .bg-blue   { background: linear-gradient(135deg, rgba(0, 180, 219, 0.3), rgba(0, 131, 176, 0.1)); border-top: 1px solid rgba(0, 180, 219, 0.5); }
    .bg-red    { background: linear-gradient(135deg, rgba(217, 4, 41, 0.3), rgba(141, 2, 31, 0.1)); border-top: 1px solid rgba(217, 4, 41, 0.5); }
    .bg-green  { background: linear-gradient(135deg, rgba(17, 153, 142, 0.3), rgba(56, 239, 125, 0.1)); border-top: 1px solid rgba(56, 239, 125, 0.5); }
    .bg-gold   { background: linear-gradient(135deg, rgba(255, 215, 0, 0.3), rgba(184, 134, 11, 0.1)); color: #FFD700 !important; border-top: 1px solid rgba(255, 215, 0, 0.5); }
    
    .agenda-card, .history-card { 
        background-color: rgba(22, 22, 22, 0.6) !important; backdrop-filter: blur(12px) !important;
        border-radius: 16px; padding: 15px; margin-bottom: 12px; border: 1px solid rgba(255, 255, 255, 0.08); 
    }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: rgba(0,0,0,0.8); backdrop-filter: blur(5px); color: #666; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #222; z-index: 9999; }
    div.stButton > button { background-color: #D90429 !important; color: white !important; border-radius: 10px !important; font-weight: 700 !important; border: none !important; height: 45px !important; box-shadow: 0 4px 10px rgba(217, 4, 41, 0.3); }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---

def converter_valor(valor):
    if isinstance(valor, (int, float)): return float(valor)
    try:
        v = str(valor).replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
        if not v: return 0.0
        return float(v)
    except: return 0.0

def limpar_numero(num):
    if not num: return ""
    return re.sub(r'\D', '', str(num))

def formatar_moeda(valor):
    try: return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

def conectar_google_sheets():
    ID_FIXO = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg"
    try:
        if "app" in st.secrets and "spreadsheet_id" in st.secrets["app"]:
            ID_FIXO = st.secrets["app"]["spreadsheet_id"]
        if os.path.exists("chave_google.json"): 
            client = gspread.service_account(filename="chave_google.json")
        elif "gcp_service_account" in st.secrets:
            client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        else: return None
        return client.open_by_key(ID_FIXO)
    except: return None

def carregar_dados(aba):
    sheet = conectar_google_sheets()
    if sheet is None: return pd.DataFrame()
    try: return pd.DataFrame(sheet.worksheet(aba).get_all_records())
    except: return pd.DataFrame()

def salvar_no_google(aba, linha_dados):
    sheet = conectar_google_sheets()
    if sheet is None: return False, "Falha na conexão."
    try:
        ws = sheet.worksheet(aba)
        headers = ws.row_values(1)
        if not headers: headers = list(linha_dados.keys()); ws.append_row(headers)
        nova_linha = []
        for col in headers:
            nova_linha.append(linha_dados.get(col, ""))
        ws.append_row(nova_linha)
        return True, "Sucesso"
    except Exception as e: return False, str(e)

def excluir_agendamento(indice_linha):
    sheet = conectar_google_sheets()
    if sheet is None: return False
    try: ws = sheet.worksheet("Agendamentos"); ws.delete_rows(indice_linha + 2); return True
    except: return False

@st.cache_data(ttl=60)
def carregar_catalogo():
    try:
        sheet = conectar_google_sheets()
        if sheet:
            ws = sheet.worksheet("Catalogo")
            df = pd.DataFrame(ws.get_all_records())
            if not df.empty and "Categoria" in df.columns:
                cols_num = [c for c in df.columns if c != "Categoria"]
                for c in cols_num: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)
                return df
    except: pass
    
    return pd.DataFrame({
        "Categoria": ["Hatch/Compacto", "Sedã", "SUV/Caminhonete", "Picapes Grandes", "Vans/Utilitários", "Motocicleta"],
        "Lavagem Simples": [40.0, 50.0, 60.0, 70.0, 80.0, 30.0],
        "Lavagem Técnica": [150.0, 170.0, 190.0, 210.0, 230.0, 100.0],
        "Higi. Bancos": [80.0, 80.0, 80.0, 120.0, 150.0, 0.0], 
        "Higi. Interna (Teto/Carpete)": [150.0, 150.0, 180.0, 200.0, 250.0, 0.0],
        "Combo Premium": [300.0, 320.0, 350.0, 400.0, 450.0, 0.0],
        "Limpeza Motor": [100.0, 100.0, 120.0, 150.0, 150.0, 80.0],
        "Faróis": [200.0, 200.0, 200.0, 200.0, 200.0, 100.0],
        "Cristalização Vidros": [90.0, 120.0, 150.0, 150.0, 150.0, 50.0],
        "Vitrificação": [800.0, 900.0, 1100.0, 1300.0, 1300.0, 500.0]
    })

def obter_icone_html(cat):
    if not isinstance(cat, str): return '<i class="bi bi-car-front-fill"></i>'
    c = cat.lower()
    if "moto" in c: return '<i class="bi bi-motorcycle"></i>'
    elif "suv" in c or "picape" in c: return '<i class="bi bi-truck-front-fill"></i>'
    elif "van" in c: return '<i class="bi bi-bus-front-fill"></i>'
    else: return '<i class="bi bi-car-front-fill"></i>'

# --- BUSCA INTELIGENTE ---
def buscar_cliente_por_placa(placa_busca):
    df_a = carregar_dados("Agendamentos")
    df_v = carregar_dados("Vendas")
    df_c = pd.concat([df_a, df_v], ignore_index=True)
    if df_c.empty: return None
    
    placa_clean = placa_busca.replace("-", "").strip().upper()
    cols = {c.lower(): c for c in df_c.columns}
    col_placa = cols.get("placa")
    
    if col_placa:
        df_c[col_placa] = df_c[col_placa].astype(str).str.replace("-", "").str.strip().str.upper()
        res = df_c[df_c[col_placa] == placa_clean]
        if not res.empty:
            u = res.iloc[-1]
            col_tel = cols.get("telefone") or cols.get("whatsapp") or cols.get("celular")
            tel = u.get(col_tel, "") if col_tel else ""
            
            col_cli = cols.get("cliente", "Cliente")
            col_veic = cols.get("veiculo") or cols.get("carro") or "Veiculo"
            col_cat = cols.get("categoria", "Categoria")
            return {
                "Cliente": u.get(col_cli, ""),
                "Telefone": str(tel),
                "Veiculo": u.get(col_veic, ""),
                "Categoria": u.get(col_cat, "")
            }
    return None

# --- PDF ---
def gerar_pdf_orcamento(dados):
    pdf = FPDF()
    pdf.add_page()
    logo_file = next((f for f in ["logo.png", "Logo.png", "LOGO.png"] if os.path.exists(f)), None)
    if logo_file: pdf.image(logo_file, x=10, y=8, w=35)
    
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt("JM DETAIL - ORÇAMENTO"), ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt("Estética Automotiva Premium | (75) 99830-3753"), ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt(f"CLIENTE: {dados['Cliente']}"), ln=True)
    pdf.cell(0, 10, txt(f"VEÍCULO: {dados['Veiculo']} | PLACA: {dados['Placa']}"), ln=True)
    pdf.cell(0, 10, txt(f"DATA: {dados['Data']}"), ln=True)
    pdf.ln(5)
    
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(140, 10, txt("Descrição do Serviço"), 1, 0, 'L', 1)
    pdf.cell(50, 10, txt("Valor"), 1, 1, 'C', 1)
    
    pdf.set_font("Arial", size=12)
    
    if 'Itens' in dados and isinstance(dados['Itens'], list):
        for item in dados['Itens']:
            pdf.cell(140, 10, txt(item['desc']), 1)
            pdf.cell(50, 10, txt(f"R$ {item['val']:.2f}"), 1, 1, 'C')
    else:
        for s in str(dados['Servicos']).split(','):
            if s.strip():
                pdf.cell(140, 10, txt(s.strip()), 1)
                pdf.cell(50, 10, "", 1, 1, 'C') 
            
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(140, 10, "VALOR TOTAL", 1, 0, 'R')
    pdf.cell(50, 10, txt(f"R$ {dados['Total']:.2f}"), 1, 1, 'C')
    
    pdf.ln(20)
    sig_file = next((f for f in ["assinatura.png", "Assinatura.png"] if os.path.exists(f)), None)
    if sig_file: 
        x_centered = (210 - 50) / 2
        pdf.image(sig_file, x=x_centered, y=pdf.get_y() - 15, w=50)
    
    pdf.cell(0, 10, "________________________________________", ln=True, align='C')
    pdf.cell(0, 5, txt("Jairan Jesus Matos - JM Detail"), ln=True, align='C')
    return pdf.output(dest="S").encode("latin-1")

def gerar_relatorio_mensal(df_mes, resumo):
    pdf = FPDF()
    pdf.add_page()
    logo_file = next((f for f in ["logo.png", "Logo.png", "LOGO.png"] if os.path.exists(f)), None)
    if logo_file: pdf.image(logo_file, x=10, y=8, w=35)
    
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt("JM DETAIL - RELATÓRIO MENSAL"), ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt(f"Período: {resumo['mes']}"), ln=True, align='C')
    pdf.ln(10)
    
    # Resumo Financeiro
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt("RESUMO FINANCEIRO"), ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 8, txt("Faturamento Bruto:"), 0); pdf.cell(0, 8, txt(formatar_moeda(resumo['faturamento'])), 0, 1)
    pdf.cell(100, 8, txt("Despesas Totais:"), 0); pdf.cell(0, 8, txt(formatar_moeda(resumo['despesas'])), 0, 1)
    pdf.cell(100, 8, txt("Comissões (Total):"), 0); pdf.cell(0, 8, txt(formatar_moeda(resumo['comissoes'])), 0, 1)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 10, txt("LUCRO LÍQUIDO FINAL:"), 0); pdf.cell(0, 10, txt(formatar_moeda(resumo['lucro'])), 0, 1)
    pdf.ln(10)
    
    # Tabela de Serviços
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(30, 8, "DATA", 1, 0, 'C', 1)
    pdf.cell(60, 8, "CLIENTE", 1, 0, 'L', 1)
    pdf.cell(60, 8, "VEÍCULO", 1, 0, 'L', 1)
    pdf.cell(40, 8, "VALOR", 1, 1, 'C', 1)
    
    pdf.set_font("Arial", size=9)
    for _, r in df_mes.iterrows():
        dt = r['Data_dt'].strftime('%d/%m/%Y') if pd.notnull(r['Data_dt']) else str(r['Data'])
        val = formatar_moeda(converter_valor(r['Total']))
        pdf.cell(30, 7, txt(dt), 1, 0, 'C')
        pdf.cell(60, 7, txt(str(r['Cliente'])[:25]), 1, 0, 'L')
        pdf.cell(60, 7, txt(str(r['Carro'])[:25]), 1, 0, 'L')
        pdf.cell(40, 7, txt(val), 1, 1, 'C')
        
    return pdf.output(dest="S").encode("latin-1")

# ==============================================================================
# --- CABEÇALHO ---
# ==============================================================================
c_logo1, c_logo2, c_logo3 = st.columns([1,3,1]) # Logo maior para o efeito aparecer
with c_logo2:
    logo_path = next((f for f in ["logo.png", "Logo.png", "LOGO.png"] if os.path.exists(f)), None)
    if logo_path: st.image(logo_path, use_container_width=True)
    else: st.markdown("<h1 style='text-align:center; color:#D90429; font-weight:800'>JM DETAIL</h1>", unsafe_allow_html=True)

st.write("") 
menu_opcoes = ["DASHBOARD", "AGENDA", "FINANCEIRO", "DESPESAS", "HISTÓRICO"]
menu_selecionado = st.radio("Navegação", menu_opcoes, horizontal=True, label_visibility="collapsed")
st.write("---") 

# --- PÁGINAS ---

def page_dashboard():
    hoje = datetime.now()
    mes_atual, ano_atual = hoje.month, hoje.year
    nome_meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    st.markdown(f'## <i class="bi bi-speedometer2" style="color: #00B4DB;"></i> Painel Geral <small style="font-size:14px; color:#888">| {nome_meses[mes_atual]}/{ano_atual}</small>', unsafe_allow_html=True)
    
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    df_a = carregar_dados("Agendamentos")
    
    receita_mes, despesa_mes, pendente_total, count_p = 0.0, 0.0, 0.0, 0
    lucro_operacional = 0.0
    
    if not df_v.empty:
        df_v.columns = [c.strip().capitalize() for c in df_v.columns]
        for c in ["Total"]:
            if c in df_v.columns:
                df_v[c] = df_v[c].apply(converter_valor)
        df_v['Data_dt'] = pd.to_datetime(df_v['Data'], dayfirst=True, errors='coerce')
        df_mes = df_v[(df_v['Data_dt'].dt.month == mes_atual) & (df_v['Data_dt'].dt.year == ano_atual)]
        if "Status" in df_v.columns:
            receita_mes = df_mes[df_mes["Status"].str.strip() == "Concluído"]["Total"].sum()
            pendente_total = df_v[df_v["Status"].str.contains("Pendente|Orçamento", case=False, na=False)]["Total"].sum()
            count_p = len(df_v[df_v["Status"].str.contains("Pendente|Orçamento", case=False, na=False)])
            lucro_operacional = receita_mes * 0.50

    if not df_d.empty:
        df_d.columns = [c.strip().capitalize() for c in df_d.columns]
        df_d['Data_dt'] = pd.to_datetime(df_d['Data'], dayfirst=True, errors='coerce')
        df_d_mes = df_d[(df_d['Data_dt'].dt.month == mes_atual) & (df_d['Data_dt'].dt.year == ano_atual)]
        if "Valor" in df_d.columns:
            despesa_mes = df_d_mes["Valor"].apply(converter_valor).sum()
    
    lucro_final = lucro_operacional - despesa_mes
    META = 5000.00 
    pct = min((receita_mes / META) * 100, 100.0) if META > 0 else 0
    
    st.markdown(f'<div style="background-color: rgba(30,30,30,0.5); backdrop-filter: blur(10px); padding: 10px 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;"><div style="display:flex; justify-content:space-between; color:#bbb; font-size:12px; margin-bottom:5px;"><span>🎯 META: {formatar_moeda(META)}</span><span>ATUAL: <b style="color:white">{formatar_moeda(receita_mes)}</b></span></div><div style="width:100%; background-color:#333; border-radius:15px; height:22px;"><div style="width:{pct}%; background: linear-gradient(90deg, #00b09b, #96c93d); height:22px; border-radius:15px; display:flex; align-items:center; justify-content:flex-end; padding-right:10px; transition: width 1s ease-in-out; box-shadow: 0 0 10px rgba(150, 201, 61, 0.5);"><span style="color:white; font-weight:bold; font-size:12px; text-shadow: 1px 1px 2px black;">{pct:.1f}%</span></div></div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="dash-card bg-orange"><i class="bi bi-hourglass-split card-icon-bg"></i><h4>PENDENTES (GERAL)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(pendente_total)}</div><small>{count_p} carros na fila</small></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="dash-card bg-blue"><i class="bi bi-currency-dollar card-icon-bg"></i><h4>FATURAMENTO (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(receita_mes)}</div><small>Ref: {nome_meses[mes_atual]}</small></div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3: st.markdown(f'<div class="dash-card bg-red"><i class="bi bi-graph-down-arrow card-icon-bg"></i><h4>DESPESAS (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(despesa_mes)}</div><small>Gastos externos</small></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="dash-card {"bg-green" if lucro_final >= 0 else "bg-red"}"><i class="bi bi-wallet2 card-icon-bg"></i><h4>LUCRO LÍQUIDO</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_final)}</div><small>50% Bruto - Despesas</small></div>', unsafe_allow_html=True)

    st.write("---")
    col_graf, col_prox = st.columns([2, 1])
    with col_graf:
        st.markdown('### <i class="bi bi-graph-up-arrow" style="color: #39FF14;"></i> Performance Mensal', unsafe_allow_html=True)
        if not df_v.empty and 'df_mes' in locals() and not df_mes.empty:
            neon_scale = alt.Scale(range=['#39FF14', '#1F51FF', '#BC13FE', '#FFFF00', '#FF00FF', '#FF5F00', '#00FFFF'])
            base = alt.Chart(df_mes).encode(x=alt.X('Data_dt:T', title=None, axis=alt.Axis(labelColor='#aaa', grid=False, format='%d/%m')))
            bars = base.mark_bar(size=28, cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(y=alt.Y('Total:Q', title=None), color=alt.Color('Cliente', legend=None, scale=neon_scale), tooltip=['Data', 'Cliente', 'Carro', alt.Tooltip('Total:Q', format=',.2f')])
            line = base.mark_line(strokeWidth=3, color='#FFFFFF').encode(y='sum(Total):Q') + base.mark_circle(size=80, color='#FFFFFF').encode(y='sum(Total):Q', tooltip=[alt.Tooltip('sum(Total):Q', format=',.2f', title='Total do Dia')])
            chart = alt.layer(bars, line).properties(height=320, background='transparent')
            st.altair_chart(chart, use_container_width=True)
        else: st.info("Sem dados de vendas neste mês.")

    with col_prox:
        st.markdown('### <i class="bi bi-calendar-week"></i> Próximos', unsafe_allow_html=True)
        if not df_a.empty:
            df_a['Data_dt'] = pd.to_datetime(df_a['Data'], dayfirst=True, errors='coerce')
            hoje_dia = pd.to_datetime(date.today())
            df_futuro = df_a[df_a['Data_dt'] >= hoje_dia].sort_values(by="Data_dt").head(3)
            if not df_futuro.empty:
                for _, r in df_futuro.iterrows():
                    st.markdown(f'<div style="background-color: rgba(30,30,30,0.4); backdrop-filter: blur(5px); padding: 12px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1); border-left: 4px solid #39FF14;"><div style="font-weight:bold; color:white; font-size:14px;"><i class="bi bi-clock"></i> {r["Data"]} - {r["Hora"]}</div><div style="color:#ddd; font-size:13px; margin-top:4px;"><b>{r["Veiculo"]}</b></div><div style="color:#aaa; font-size:12px;">{r["Cliente"]}</div></div>', unsafe_allow_html=True)
            else: st.info("Sem agendamentos futuros.")
        else: st.info("Agenda vazia.")

def page_financeiro():
    st.markdown('## <i class="bi bi-cash-coin" style="color: #28a745;"></i> Gestão Financeira', unsafe_allow_html=True)
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    comissao_pendente, fundo_caixa, total_bruto, total_despesas = 0.0, 0.0, 0.0, 0.0
    if not df_v.empty:
        df_v.columns = [c.strip().capitalize() for c in df_v.columns]
        if "Status comissao" not in df_v.columns: df_v["Status comissao"] = "Pendente"
        for c in ["Total", "Valor comissao", "Fundo caixa"]:
            if c in df_v.columns: df_v[c] = df_v[c].apply(converter_valor)
        df_v['Data_dt'] = pd.to_datetime(df_v['Data'], dayfirst=True, errors='coerce')
        hoje = datetime.now()
        df_mes = df_v[(df_v['Data_dt'].dt.month == hoje.month) & (df_v['Data_dt'].dt.year == hoje.year)]
        total_bruto = df_mes[df_mes["Status"].str.strip()=="Concluído"]["Total"].sum()
        df_pendente = df_v[df_v["Status comissao"] != "Pago"]
        for index, row in df_pendente.iterrows():
             if row.get("Valor comissao", 0) > 0 or "Equipe" in str(row.get("Funcionario", "")): comissao_pendente += (row["Total"] * 0.40)
        if "Fundo caixa" in df_v.columns: fundo_caixa = df_v["Fundo caixa"].sum()
    if not df_d.empty:
        df_d.columns = [c.strip().capitalize() for c in df_d.columns]
        df_d['Data_dt'] = pd.to_datetime(df_d['Data'], dayfirst=True, errors='coerce')
        df_d_mes = df_d[(df_d['Data_dt'].dt.month == hoje.month) & (df_d['Data_dt'].dt.year == hoje.year)]
        if "Valor" in df_d.columns: total_despesas = df_d_mes["Valor"].apply(converter_valor).sum()
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="dash-card bg-red"><h4>A PAGAR (COMISSÃO)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(comissao_pendente)}</div><small>Pendente Equipe</small></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="dash-card bg-blue"><h4>CAIXA EMPRESA (10%)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(fundo_caixa)}</div><small>Acumulado Total</small></div>', unsafe_allow_html=True)
    lucro_liq_real = (total_bruto * 0.50) - total_despesas
    c3.markdown(f'<div class="dash-card bg-green"><h4>LUCRO LÍQUIDO REAL</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_liq_real)}</div><small>Mês Atual (Já descontado tudo)</small></div>', unsafe_allow_html=True)
    st.write("---")
    st.markdown("### 📋 Detalhe do que falta pagar")
    if not df_v.empty:
        df_p = df_pendente[["Data", "Cliente", "Carro", "Placa", "Total"]].copy()
        df_p["Comissão (40%)"] = df_p["Total"] * 0.40
        df_p["Total"] = df_p["Total"].apply(formatar_moeda)
        df_p["Comissão (40%)"] = df_p["Comissão (40%)"].apply(formatar_moeda)
        st.dataframe(df_p, use_container_width=True, hide_index=True)
    col_pay, col_pdf = st.columns([1, 2])
    with col_pay:
        if comissao_pendente > 0:
            if st.button("✅ Pagar Todas Comissões"):
                sheet = conectar_google_sheets(); ws = sheet.worksheet("Vendas"); dados = ws.get_all_records(); header = ws.row_values(1); col_idx = -1
                for idx, h in enumerate(header):
                    if "status" in h.lower() and "comiss" in h.lower(): col_idx = idx + 1; break
                if col_idx > 0:
                    for i, linha in enumerate(dados):
                        v = converter_valor(linha.get("Valor Comissao", "0"))
                        if v > 0 and str(linha.get("Status Comissao", "")) != "Pago": ws.update_cell(i + 2, col_idx, "Pago")
                    st.success("Pago!"); t_sleep.sleep(1); st.rerun()
    with col_pdf:
        if st.button("📄 Baixar Relatório Mensal", use_container_width=True):
            resumo = {"mes": datetime.now().strftime("%m/%Y"), "faturamento": total_bruto, "despesas": total_despesas, "comissoes": total_bruto * 0.40, "lucro": lucro_liq_real}
            st.download_button("📥 Download PDF", gerar_relatorio_mensal(df_mes, resumo), f"Relatorio_{resumo['mes'].replace('/','_')}.pdf", "application/pdf")

def page_agendamento():
    st.markdown('## <i class="bi bi-calendar-check" style="color: white;"></i> Agenda Integrada', unsafe_allow_html=True)
    tab_new, tab_list = st.tabs(["NOVO AGENDAMENTO", "LISTA DE SERVIÇOS"]) 
    df_cat = carregar_catalogo()
    with tab_new:
        with st.container(border=True):
            c_placa, c_buscar = st.columns([3, 1]); placa_input = c_placa.text_input("Digite a Placa para Buscar Cadastro (ou Nova Placa)", key="placa_input")
            val_cli, val_veic, val_zap, val_cat_idx = "", "", "", 0
            if placa_input:
                dados_cli = buscar_cliente_por_placa(placa_input)
                if dados_cli:
                    st.success(f"Cliente Encontrado: {dados_cli['Cliente']}"); val_cli, val_veic, val_zap = dados_cli['Cliente'], dados_cli['Veiculo'], dados_cli['Telefone']
                    cats_lista = df_cat["Categoria"].tolist() if not df_cat.empty else []
                    if dados_cli['Categoria'] in cats_lista: val_cat_idx = cats_lista.index(dados_cli['Categoria'])
                else:
                    if len(placa_input) > 5: st.warning("Placa nova.")
            c1, c2 = st.columns(2); cli, zap = c1.text_input("Nome do Cliente", value=val_cli), c2.text_input("WhatsApp (DDD+Número)", value=val_zap, placeholder="75999998888")
            c3, c4 = st.columns(2); veic = c3.text_input("Modelo do Veículo", value=val_veic)
            dt, hr = c4.date_input("Data", value=date.today()), c4.time_input("Horário", value=time(8, 0)).strftime("%H:%M")
            cat = st.selectbox("Categoria:", df_cat["Categoria"], index=val_cat_idx)
            servs = st.multiselect("Serviços:", [c for c in df_cat.columns if c not in ["Categoria", "Telefone", "telefone", "Obs"]], placeholder="Selecione os serviços...")
            ce1, ce2, ce3 = st.columns(3); ext, desc, qm = ce1.number_input("Valor Extra", min_value=0.0), ce2.number_input("Desconto", min_value=0.0), ce3.radio("Executor:", ["Eu Mesmo", "Equipe"], horizontal=True)
            if servs:
                itens_calc, total = [], 0.0
                for s in servs:
                    val = float(df_cat[df_cat["Categoria"] == cat][s].values[0]); total += val; itens_calc.append({'desc': s, 'val': val})
                total = total + ext - desc
                if ext > 0: itens_calc.append({'desc': "Extra", 'val': ext})
                if desc > 0: itens_calc.append({'desc': "Desconto", 'val': -desc})
                st.markdown(f"<h3 style='text-align:right; color:#39FF14'>Total: {formatar_moeda(total)}</h3>", unsafe_allow_html=True)
                b1, b2 = st.columns(2)
                if b1.button("CONFIRMAR AGENDAMENTO", use_container_width=True):
                    d = {"Data": dt.strftime("%d/%m/%Y"), "Hora": hr, "Cliente": cli, "Telefone": zap, "Veiculo": veic, "Placa": placa_input, "Servicos": ", ".join(servs), "Total": total, "Executor": qm, "Status": "Orçamento/Pendente", "Categoria": cat}
                    if salvar_no_google("Agendamentos", d)[0]:
                        st.success("Agendado!"); t_sleep.sleep(1); z_clean = limpar_numero(zap)
                        if z_clean:
                            msg_enc = urllib.parse.quote(f"Ola {cli}, agendamento confirmado na JM Detail:\n> Veiculo: {veic}\n> Data: {dt.strftime('%d/%m/%Y')} as {hr}\n> Valor Total: {formatar_moeda(total)}")
                            st.markdown(f'<a href="https://wa.me/55{z_clean}?text={msg_enc}" target="_blank"><button style="background:#25D366;color:white;width:100%;border:none;padding:10px;border-radius:5px">ENVIAR NO WHATSAPP</button></a>', unsafe_allow_html=True)
                if b2.button("📄 GERAR ORÇAMENTO PDF", use_container_width=True):
                    d_pdf = {"Cliente": cli, "Veiculo": veic, "Placa": placa_input, "Data": dt.strftime("%d/%m/%Y"), "Itens": itens_calc, "Total": total}
                    st.download_button("📥 BAIXAR PDF", gerar_pdf_orcamento(d_pdf), f"Orcamento_{cli}.pdf", "application/pdf", use_container_width=True)
    with tab_list:
        df_a = carregar_dados("Agendamentos")
        if df_a.empty: st.info("Vazio.")
        else:
            for i, r in df_a.iterrows():
                val_total = converter_valor(r.get('Total', 0))
                st.markdown(f'<div class="agenda-card"><div style="display:flex; justify-content:space-between;"><b>{r["Data"]} {r["Hora"]}</b><b style="color:#39FF14">{formatar_moeda(val_total)}</b></div><div style="font-size:18px"><b>{obter_icone_html(r.get("Categoria",""))} {r["Veiculo"]}</b> ({r["Placa"]})</div><div>{r["Cliente"]}</div><div style="color:#888">🔧 {r["Servicos"]}</div></div>', unsafe_allow_html=True)
                c_ok, c_zap, c_del = st.columns([2, 1, 1])
                with c_ok:
                    if st.button("✅ Concluir", key=f"ok_{i}", use_container_width=True):
                        t = converter_valor(r["Total"]); f, c = t * 0.10, (t * 0.40 if "Equipe" in r["Executor"] else 0.0)
                        venda = {"Data": r["Data"], "Cliente": r["Cliente"], "Telefone": r.get("Telefone", ""), "Carro": r["Veiculo"], "Placa": r["Placa"], "Serviços": r["Servicos"], "Total": t, "Status": "Concluído", "Funcionario": r["Executor"], "Valor Comissao": c, "Fundo Caixa": f, "Lucro Liquido": t-f-c, "Status Comissao": "Pendente", "Categoria": r.get("Categoria", "")}
                        salvar_no_google("Vendas", venda); excluir_agendamento(i); st.rerun()
                with c_zap:
                    if r.get("Telefone"):
                        z_clean = limpar_numero(r.get("Telefone"))
                        if z_clean:
                            val_fmt, msg_txt = formatar_moeda(converter_valor(r.get('Total', 0))), f"Ola {r['Cliente']}! Seu {r['Veiculo']} ja esta pronto na JM Detail.\n> Valor Total: {formatar_moeda(converter_valor(r.get('Total', 0)))}\n> Pode vir buscar!"
                            msg_enc = urllib.parse.quote(msg_txt)
                            st.markdown(f'<a href="https://wa.me/55{z_clean}?text={msg_enc}" target="_blank"><button style="background-color:#128C7E; color:white; border:none; border-radius:10px; height:45px; width:100%"><i class="bi bi-whatsapp"></i></button></a>', unsafe_allow_html=True)
                    else: st.markdown('<button disabled style="background-color:#333; color:#555; border:none; border-radius:10px; height:45px; width:100%"><i class="bi bi-whatsapp"></i></button>', unsafe_allow_html=True)
                with c_del:
                    if st.button("🗑️", key=f"del_{i}", use_container_width=True): excluir_agendamento(i); st.rerun()

def page_despesas():
    st.markdown('## <i class="bi bi-receipt" style="color: #D90429;"></i> Despesas', unsafe_allow_html=True)
    with st.form("form_desp"):
        desc, val = st.text_input("Descrição"), st.number_input("Valor", min_value=0.0)
        if st.form_submit_button("Lançar"): salvar_no_google("Despesas", {"Data": datetime.now().strftime("%d/%m/%Y"), "Descricao": desc, "Valor": val}); st.success("Salvo!")

def page_historico():
    st.markdown('## <i class="bi bi-clock-history"></i> Histórico', unsafe_allow_html=True)
    df = carregar_dados("Vendas")
    if not df.empty:
        df["Total_Num"] = df["Total"].apply(converter_valor); ranking = df.groupby("Cliente")["Total_Num"].sum().reset_index().sort_values(by="Total_Num", ascending=False).head(5)
        st.markdown("### 🏆 Ranking VIP (Top 5)")
        col_rank = st.columns(len(ranking))
        for idx, (i, r) in enumerate(ranking.iterrows()):
            medalha, cor = ("🥇" if idx==0 else "🥈" if idx==1 else "🥉" if idx==2 else f"{idx+1}º"), ("bg-gold" if idx==0 else "")
            st.markdown(f'<div class="dash-card {cor}" style="height:100px; padding:10px; margin-bottom:10px"><div style="font-size:20px">{medalha}</div><div style="font-weight:bold; font-size:14px">{r["Cliente"]}</div><div style="font-size:12px">{formatar_moeda(r["Total_Num"])}</div></div>', unsafe_allow_html=True)
        st.write("---")
        busca = st.text_input("🔍 Buscar...").strip().lower(); df_f = df.iloc[::-1]
        if busca: df_f = df_f[df_f.apply(lambda r: busca in str(r).lower(), axis=1)]
        for _, r in df_f.iterrows():
            total_hist = formatar_moeda(converter_valor(r["Total"]))
            st.markdown(f'<div class="history-card" style="border-left:5px solid #28a745"><div style="display:flex;justify-content:space-between;"><div><b>{r["Carro"]}</b><br>{r["Cliente"]} | {r["Placa"]}</div><div style="text-align:right"><b style="color:#39FF14">{total_hist}</b><br><small>{r["Data"]}</small></div></div><div style="color:#888">{r["Serviços"]}</div></div>', unsafe_allow_html=True)
    else: st.info("Vazio.")

if menu_selecionado == "DASHBOARD": page_dashboard()
elif menu_selecionado == "AGENDA": page_agendamento()
elif menu_selecionado == "HISTÓRICO": page_historico()
elif menu_selecionado == "FINANCEIRO": page_financeiro()
elif menu_selecionado == "DESPESAS": page_despesas()

st.markdown('<div class="footer">JM Detail System © 2026 | Desenvolvido por Jairan Jesus Matos</div>', unsafe_allow_html=True)
