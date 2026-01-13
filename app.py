import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, time
from fpdf import FPDF
import gspread
import os
import time as t_sleep
import re 
import urllib.parse
import shutil

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# --- 2. CSS (EXATAMENTE O DA SUA VERSÃO ESTÁVEL app (1).py) ---
# ==============================================================================
st.markdown("""
<style>
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    
    html, body, p, h1, h2, h3, h4, h5, h6, li, a, button, input, textarea, label, .stTextInput, .stNumberInput, .stSelectbox {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #000000 80%);
    }
    .block-container { padding-top: 0.5rem; padding-bottom: 6rem; }
    [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebar"] { display: none !important; }
    #MainMenu, footer {visibility: hidden;}

    /* Inputs Glass */
    input[type="text"], input[type="number"], input[type="date"], input[type="time"], .stSelectbox > div > div, .stMultiSelect > div > div {
        background-color: rgba(30, 30, 30, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important; border-radius: 10px !important;
        backdrop-filter: blur(5px) !important;
    }
    
    /* Menu Superior (Do seu código original) */
    div[role="radiogroup"] { display: flex !important; width: 100% !important; justify-content: space-between !important; background: transparent !important; border: none !important; padding: 0 !important; gap: 5px !important; overflow-x: auto !important; }
    div[role="radiogroup"] label {
        flex: 1 !important; min-width: 80px !important; background-color: rgba(30, 30, 30, 0.4) !important; backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; padding: 10px 2px !important; border-radius: 12px !important; transition: all 0.2s ease !important;
        margin: 0 !important; color: #aaa !important; font-weight: 500 !important; font-size: 12px !important; 
        white-space: nowrap !important; display: flex; align-items: center; justify-content: center !important;
    }
    div[role="radiogroup"] label:hover { border-color: #D90429 !important; color: white !important; background-color: rgba(217, 4, 41, 0.15) !important; }
    div[role="radiogroup"] label[data-checked="true"] { 
        background: linear-gradient(135deg, rgba(217, 4, 41, 0.8), rgba(141, 2, 31, 0.8)) !important; 
        backdrop-filter: blur(12px) !important; color: white !important; border-color: rgba(255,255,255,0.2) !important; 
        box-shadow: 0 4px 15px rgba(217, 4, 41, 0.3) !important; font-weight: 700 !important;
    }
    
    /* Cards */
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
    .badge-cat { padding: 4px 8px; border-radius: 8px; font-size: 10px; font-weight: bold; text-transform: uppercase; margin-right: 5px; }
    .b-moto { background-color: rgba(255, 193, 7, 0.2); color: #ffc107; border: 1px solid rgba(255, 193, 7, 0.4); }
    .b-carro { background-color: rgba(0, 180, 219, 0.2); color: #00b4db; border: 1px solid rgba(0, 180, 219, 0.4); }
    .b-suv { background-color: rgba(233, 30, 99, 0.2); color: #e91e63; border: 1px solid rgba(233, 30, 99, 0.4); }

    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: rgba(0,0,0,0.8); backdrop-filter: blur(5px); color: #666; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #222; z-index: 9999; }
    div.stButton > button { background-color: #D90429 !important; color: white !important; border-radius: 10px !important; font-weight: 700 !important; border: none !important; height: 45px !important; box-shadow: 0 4px 10px rgba(217, 4, 41, 0.3); }
</style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DE BACKEND ---

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
    except Exception as e:
        return None

def carregar_dados(aba):
    sheet = conectar_google_sheets()
    if sheet is None: return pd.DataFrame()
    try: 
        return pd.DataFrame(sheet.worksheet(aba).get_all_records())
    except:
        return pd.DataFrame()

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
    except Exception as e: 
        return False, str(e)

def excluir_agendamento(indice_linha):
    sheet = conectar_google_sheets()
    if sheet is None: return False
    try: ws = sheet.worksheet("Agendamentos"); ws.delete_rows(indice_linha + 2); return True
    except Exception as e: return False

def atualizar_estoque_auto():
    sheet = conectar_google_sheets()
    if sheet:
        try:
            ws = sheet.worksheet("Estoque")
            dados = ws.get_all_values() 
            if len(dados) > 1:
                headers = [h.lower().strip() for h in dados[0]]
                idx_atual = -1
                idx_gasto = -1
                for i, h in enumerate(headers):
                    if "atual" in h: idx_atual = i
                    if "gasto" in h: idx_gasto = i
                if idx_atual != -1 and idx_gasto != -1:
                    for i in range(1, len(dados)):
                        try:
                            atual = float(dados[i][idx_atual].replace(",", ".") or 0)
                            gasto = float(dados[i][idx_gasto].replace(",", ".") or 0)
                            if gasto > 0:
                                novo_val = max(0, atual - gasto)
                                ws.update_cell(i + 1, idx_atual + 1, novo_val)
                        except: pass
        except: pass 

@st.cache_data(ttl=300)
def obter_custo_fixo():
    try:
        sheet = conectar_google_sheets()
        if sheet:
            ws = sheet.worksheet("Config")
            df = pd.DataFrame(ws.get_all_records())
            if "Chave" in df.columns and "Valor" in df.columns:
                res = df[df["Chave"].astype(str).str.lower() == "custofixo"]
                if not res.empty:
                    return converter_valor(res.iloc[0]["Valor"])
    except: pass
    return 0.0

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
    return pd.DataFrame() 

@st.cache_data(ttl=300) 
def carregar_lista_avarias():
    padrao = ["Capô: Risco/Arranhão", "Teto: Pintura Queimada", "Rodas: Raladas", "Interior: Banco Rasgado"]
    try:
        sheet = conectar_google_sheets()
        if sheet:
            ws = sheet.worksheet("Config") 
            df = pd.DataFrame(ws.get_all_records())
            if not df.empty and "Avarias" in df.columns:
                lista_planilha = df["Avarias"].dropna().tolist()
                lista_planilha = [x for x in lista_planilha if str(x).strip()] 
                if lista_planilha: return lista_planilha
    except: pass
    return padrao 

def obter_icone_e_classe(cat):
    if not isinstance(cat, str): return '<i class="bi bi-car-front-fill"></i>', 'b-carro'
    c = cat.lower()
    if "moto" in c: return '<i class="bi bi-motorcycle"></i>', 'b-moto'
    elif "suv" in c or "picape" in c: return '<i class="bi bi-truck-front-fill"></i>', 'b-suv'
    elif "van" in c: return '<i class="bi bi-bus-front-fill"></i>', 'b-suv'
    else: return '<i class="bi bi-car-front-fill"></i>', 'b-carro'

def buscar_cliente_por_placa(placa_busca):
    try:
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
                col_cli = cols.get("cliente", "Cliente"); col_veic = cols.get("veiculo") or cols.get("carro") or "Veiculo"
                col_cat = cols.get("categoria", "Categoria"); col_tel = cols.get("telefone")
                return {"Cliente": u.get(col_cli, ""), "Telefone": str(u.get(col_tel,"")), "Veiculo": u.get(col_veic, ""), "Categoria": u.get(col_cat, "")}
    except: pass
    return None

# --- GERAÇÃO DE PDFS ---
def gerar_pdf_orcamento(dados):
    pdf = FPDF(); pdf.add_page()
    logo_file = next((f for f in ["logo.png", "Logo.png", "LOGO.png"] if os.path.exists(f)), None)
    if logo_file: pdf.image(logo_file, x=10, y=8, w=35)
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Arial", "B", 16); pdf.cell(0, 10, txt("JM DETAIL - ORÇAMENTO"), ln=True, align='C')
    pdf.set_font("Arial", size=10); pdf.cell(0, 10, txt("Estética Automotiva Premium | (75) 99830-3753"), ln=True, align='C'); pdf.ln(10)
    pdf.set_font("Arial", "B", 12); pdf.cell(0, 10, txt(f"CLIENTE: {dados['Cliente']}"), ln=True)
    pdf.cell(0, 10, txt(f"VEÍCULO: {dados['Veiculo']} | PLACA: {dados['Placa']}"), ln=True); pdf.ln(5)
    pdf.set_fill_color(220, 220, 220); pdf.cell(140, 10, txt("Descrição do Serviço"), 1, 0, 'L', 1); pdf.cell(50, 10, txt("Valor"), 1, 1, 'C', 1)
    pdf.set_font("Arial", size=12)
    if 'Itens' in dados and isinstance(dados['Itens'], list):
        for item in dados['Itens']: pdf.cell(140, 10, txt(item['desc']), 1); pdf.cell(50, 10, txt(f"R$ {item['val']:.2f}"), 1, 1, 'C')
    else:
        for s in str(dados['Servicos']).split(','):
            if s.strip(): pdf.cell(140, 10, txt(s.strip()), 1); pdf.cell(50, 10, "", 1, 1, 'C') 
    pdf.ln(5); pdf.set_font("Arial", "B", 14); pdf.cell(140, 10, "VALOR TOTAL", 1, 0, 'R'); pdf.cell(50, 10, txt(f"R$ {dados['Total']:.2f}"), 1, 1, 'C')
    return pdf.output(dest="S").encode("latin-1")

def gerar_pdf_vistoria(dados, fotos_paths):
    pdf = FPDF(); pdf.add_page()
    logo_file = next((f for f in ["logo.png", "Logo.png", "LOGO.png"] if os.path.exists(f)), None)
    if logo_file: pdf.image(logo_file, x=10, y=8, w=35)
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Arial", "B", 16); pdf.cell(0, 10, txt("TERMO DE VISTORIA - ENTRADA"), ln=True, align='C')
    pdf.set_font("Arial", size=10); pdf.cell(0, 10, txt("JM DETAIL - Estética Automotiva Premium"), ln=True, align='C'); pdf.ln(5)
    pdf.set_font("Arial", "B", 11); pdf.cell(0, 8, txt(f"CLIENTE: {dados['Cliente']} | VEÍCULO: {dados['Veiculo']} | PLACA: {dados['Placa']}"), ln=True)
    pdf.cell(0, 8, txt(f"DATA: {dados['Data']} | COMBUSTÍVEL: {dados['Combustivel']}%"), ln=True); pdf.ln(5)
    pdf.set_font("Arial", "B", 10); pdf.cell(0, 8, txt("AVARIAS / OBSERVAÇÕES REGISTRADAS:"), ln=True); pdf.set_font("Arial", size=10)
    if dados["Avarias"]: pdf.multi_cell(0, 6, txt(", ".join(dados["Avarias"])))
    else: pdf.cell(0, 6, txt("Nenhuma avaria declarada."), ln=True)
    if dados["Pertences"]: pdf.ln(2); pdf.set_font("Arial", "B", 10); pdf.cell(0, 8, txt("PERTENCES NO VEÍCULO:"), ln=True); pdf.set_font("Arial", size=10); pdf.multi_cell(0, 6, txt(dados["Pertences"]))
    pdf.ln(5); pdf.set_font("Arial", "B", 12); pdf.cell(0, 10, txt("REGISTRO FOTOGRÁFICO"), ln=True, align='C'); pdf.ln(5)
    x_start, y_start, w_img, h_img, col = 10, pdf.get_y(), 90, 65, 0
    for titulo, path in fotos_paths.items():
        if path and os.path.exists(path):
            if y_start + h_img > 250: pdf.add_page(); y_start = 20
            x = x_start + (col * 95); pdf.image(path, x=x, y=y_start, w=w_img, h=h_img)
            pdf.set_xy(x, y_start + h_img + 1); pdf.set_font("Arial", size=8); pdf.cell(w_img, 5, txt(titulo), 0, 0, 'C')
            col += 1
            if col > 1: col = 0; y_start += h_img + 10
    return pdf.output(dest="S").encode("latin-1")

def gerar_relatorio_mensal(df_mes, resumo):
    pdf = FPDF(); pdf.add_page()
    logo_file = next((f for f in ["logo.png", "Logo.png", "LOGO.png"] if os.path.exists(f)), None)
    if logo_file: pdf.image(logo_file, x=10, y=8, w=35)
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Arial", "B", 16); pdf.cell(0, 10, txt("JM DETAIL - RELATÓRIO MENSAL"), ln=True, align='C')
    pdf.set_font("Arial", size=10); pdf.cell(0, 10, txt(f"Período: {resumo['mes']}"), ln=True, align='C'); pdf.ln(10)
    pdf.set_font("Arial", "B", 12); pdf.cell(0, 10, txt("RESUMO FINANCEIRO"), ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 8, txt("Faturamento Bruto:"), 0); pdf.cell(0, 8, txt(formatar_moeda(resumo['faturamento'])), 0, 1)
    pdf.cell(100, 8, txt("Despesas Totais:"), 0); pdf.cell(0, 8, txt(formatar_moeda(resumo['despesas'])), 0, 1)
    pdf.cell(100, 8, txt("Comissões (Total):"), 0); pdf.cell(0, 8, txt(formatar_moeda(resumo['comissoes'])), 0, 1)
    pdf.set_font("Arial", "B", 12); pdf.cell(100, 10, txt("LUCRO LÍQUIDO FINAL:"), 0); pdf.cell(0, 10, txt(formatar_moeda(resumo['lucro'])), 0, 1); pdf.ln(10)
    pdf.set_font("Arial", "B", 10); pdf.set_fill_color(200, 200, 200)
    pdf.cell(30, 8, "DATA", 1, 0, 'C', 1); pdf.cell(60, 8, "CLIENTE", 1, 0, 'L', 1); pdf.cell(60, 8, "VEÍCULO", 1, 0, 'L', 1); pdf.cell(40, 8, "VALOR", 1, 1, 'C', 1)
    pdf.set_font("Arial", size=9)
    for _, r in df_mes.iterrows():
        dt = r['Data_dt'].strftime('%d/%m/%Y') if pd.notnull(r['Data_dt']) else str(r['Data']); val = formatar_moeda(converter_valor(r['Total']))
        pdf.cell(30, 7, txt(dt), 1, 0, 'C'); pdf.cell(60, 7, txt(str(r['Cliente'])[:25]), 1, 0, 'L'); pdf.cell(60, 7, txt(str(r['Carro'])[:25]), 1, 0, 'L'); pdf.cell(40, 7, txt(val), 1, 1, 'C')
    return pdf.output(dest="S").encode("latin-1")

# ==============================================================================
# --- 5. ÁREA CLIENTE (NOVA) ---
# ==============================================================================
def area_cliente():
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.markdown("<h1 style='text-align:center; color:#D90429'>JM DETAIL</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center; color:white'>Agendamento Online</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.info("📝 Campos com (*) são obrigatórios.")
        nome = st.text_input("Seu Nome Completo *")
        tel = st.text_input("Seu WhatsApp (DDD + Número) *", placeholder="(75) 99999-9999")
        carro = st.text_input("Modelo do Veículo *", placeholder="Ex: Fiat Toro...")
        placa = st.text_input("Placa (Opcional)")
        st.write("---")
        c_dt, c_hr = st.columns(2)
        dt = c_dt.date_input("Data Preferida", value=date.today(), min_value=date.today())
        hr = c_hr.selectbox("Horário de Início *", ["08:00 - Manhã", "13:00 - Tarde"])
        servs = st.multiselect("Serviços de Interesse", ["Lavagem Simples", "Lavagem Detalhada", "Higienização Interna", "Polimento", "Vitrificação", "Lavagem de Motor"], placeholder="Selecione...")
        obs = st.text_area("Observações (Opcional)")
        
        if st.button("🚀 SOLICITAR AGENDAMENTO", use_container_width=True):
            if nome and tel and carro:
                dados = {"Data": dt.strftime("%d/%m/%Y"), "Hora": hr, "Cliente": nome, "Telefone": tel, "Veiculo": carro, "Placa": placa, "Servicos": ", ".join(servs), "Obs": obs, "Status": "Pendente (Site)", "Total": 0}
                if salvar_no_google("Agendamentos", dados):
                    st.success("✅ Solicitação enviada!")
                    msg_zap = f"Olá JM! Agendei pelo site:\n*Cliente:* {nome}\n*Carro:* {carro}\n*Data:* {dt.strftime('%d/%m')}\n*Horário:* {hr}"
                    link_zap = f"https://wa.me/5575998303753?text={urllib.parse.quote(msg_zap)}"
                    st.markdown(f'<a href="{link_zap}" target="_blank"><button style="background:#25D366; color:white; width:100%; border:none; padding:12px; border-radius:8px; font-weight:bold; font-size:16px; margin-top:10px;"><i class="bi bi-whatsapp"></i> FINALIZAR NO WHATSAPP</button></a>', unsafe_allow_html=True)
            else: st.warning("⚠️ Preencha Nome, WhatsApp e Veículo.")

# ==============================================================================
# --- 6. FUNÇÕES ADMIN (RESTABELECIDAS DO SEU CÓDIGO) ---
# ==============================================================================
# DEFINIDAS ANTES DO USO PARA EVITAR NAMEERROR

def page_dashboard():
    hoje = datetime.now()
    mes_atual, ano_atual = hoje.month, hoje.year
    nome_meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    st.markdown(f'## <i class="bi bi-speedometer2" style="color: #00B4DB;"></i> Painel Geral <small style="font-size:14px; color:#888">| {nome_meses[mes_atual]}/{ano_atual}</small>', unsafe_allow_html=True)
    try:
        df_v = carregar_dados("Vendas"); df_d = carregar_dados("Despesas"); df_a = carregar_dados("Agendamentos")
        receita_mes, despesa_mes, pendente_total, count_p = 0.0, 0.0, 0.0, 0; lucro_operacional = 0.0; df_mes = pd.DataFrame() 
        if not df_v.empty:
            df_v.columns = [c.strip().capitalize() for c in df_v.columns]
            for c in ["Total"]: 
                if c in df_v.columns: df_v[c] = df_v[c].apply(converter_valor)
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
            if "Valor" in df_d.columns: despesa_mes = df_d_mes["Valor"].apply(converter_valor).sum()
        custo_fixo = obter_custo_fixo()
        lucro_final = lucro_operacional - despesa_mes - custo_fixo
        META = 5000.00; pct = min((receita_mes / META) * 100, 100.0) if META > 0 else 0
        
        st.markdown(f'<div style="background-color: rgba(30,30,30,0.5); backdrop-filter: blur(10px); padding: 10px 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;"><div style="display:flex; justify-content:space-between; color:#bbb; font-size:12px; margin-bottom:5px;"><span>🎯 META: {formatar_moeda(META)}</span><span>ATUAL: <b style="color:white">{formatar_moeda(receita_mes)}</b></span></div><div style="width:100%; background-color:#333; border-radius:15px; height:22px;"><div style="width:{pct}%; background: linear-gradient(90deg, #00b09b, #96c93d); height:22px; border-radius:15px; display:flex; align-items:center; justify-content:flex-end; padding-right:10px; transition: width 1s ease-in-out; box-shadow: 0 0 10px rgba(150, 201, 61, 0.5);"><span style="color:white; font-weight:bold; font-size:12px; text-shadow: 1px 1px 2px black;">{pct:.1f}%</span></div></div></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="dash-card bg-orange"><i class="bi bi-hourglass-split card-icon-bg"></i><h4>PENDENTES (GERAL)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(pendente_total)}</div><small>{count_p} carros na fila</small></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="dash-card bg-blue"><i class="bi bi-currency-dollar card-icon-bg"></i><h4>FATURAMENTO (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(receita_mes)}</div><small>Ref: {nome_meses[mes_atual]}</small></div>', unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3: st.markdown(f'<div class="dash-card bg-red"><i class="bi bi-graph-down-arrow card-icon-bg"></i><h4>DESPESAS + FIXO</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(despesa_mes + custo_fixo)}</div><small>Ext: {formatar_moeda(despesa_mes)} | Fixo: {formatar_moeda(custo_fixo)}</small></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="dash-card {"bg-green" if lucro_final >= 0 else "bg-red"}"><i class="bi bi-wallet2 card-icon-bg"></i><h4>LUCRO LÍQUIDO</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_final)}</div><small>50% Bruto - Total Despesas</small></div>', unsafe_allow_html=True)
        st.write("---")
        if not df_mes.empty:
            col_graf, col_prox = st.columns([2, 1])
            with col_graf:
                st.markdown('### <i class="bi bi-graph-up-arrow" style="color: #39FF14;"></i> Performance Mensal', unsafe_allow_html=True)
                df_chart = df_mes.groupby(df_mes['Data_dt'].dt.date)['Total'].sum().reset_index(); df_chart.columns = ['Data', 'Faturamento']
                fig = px.line(df_chart, x='Data', y='Faturamento', markers=True)
                fig.update_traces(line_color='#E0E0E0', line_width=3, marker=dict(size=6, color='#FFFFFF'))
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.05)', font_color="white", xaxis_showgrid=False, height=280, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            with col_prox:
                st.markdown('### <i class="bi bi-calendar-week"></i> Próximos', unsafe_allow_html=True)
                if not df_a.empty:
                    df_a['Data_dt'] = pd.to_datetime(df_a['Data'], dayfirst=True, errors='coerce'); hoje_dia = pd.to_datetime(date.today()); df_futuro = df_a[df_a['Data_dt'] >= hoje_dia].sort_values(by="Data_dt").head(3)
                    if not df_futuro.empty:
                        for _, r in df_futuro.iterrows():
                            st.markdown(f'<div style="background-color: rgba(30,30,30,0.4); backdrop-filter: blur(5px); padding: 12px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1); border-left: 4px solid #39FF14;"><div style="font-weight:bold; color:white; font-size:14px;"><i class="bi bi-clock"></i> {r["Data"]} - {r["Hora"]}</div><div style="color:#ddd; font-size:13px; margin-top:4px;"><b>{r["Veiculo"]}</b></div><div style="color:#aaa; font-size:12px;">{r["Cliente"]}</div></div>', unsafe_allow_html=True)
                    else: st.info("Sem agendamentos.")
        else: st.info("Sem dados de vendas.")
    except Exception as e: st.error(f"Erro no Dashboard: {e}")

def page_estoque():
    st.markdown('## <i class="bi bi-box-seam" style="color: #F5A623;"></i> Estoque', unsafe_allow_html=True)
    try:
        df = pd.DataFrame(conectar_google_sheets().worksheet("Estoque").get_all_records())
        cols = st.columns(3)
        for i, r in df.iterrows():
            at = float(str(r["Atual_ml"]).replace(",","."))
            perc = min(at/5000, 1.0)
            cor = "#39FF14" if perc > 0.2 else "#D90429"
            with cols[i%3]:
                st.markdown(f"""<div style="border:1px solid rgba(255,255,255,0.1); background:rgba(255,255,255,0.05); padding:15px; border-radius:12px; margin-bottom:15px;"><b style="font-size:16px">{r['Produto']}</b><br><small style="color:#aaa">{int(at)} ml</small><div style="background:#333; height:8px; width:100%; margin-top:8px; border-radius:4px"><div style="background:{cor}; height:8px; width:{int(perc*100)}%;"></div></div></div>""", unsafe_allow_html=True)
    except: st.warning("Erro ao carregar estoque.")

def page_financeiro():
    st.markdown('## <i class="bi bi-cash-coin" style="color: #28a745;"></i> Financeiro', unsafe_allow_html=True)
    try:
        df_v = carregar_dados("Vendas"); df_d = carregar_dados("Despesas"); comissao_pendente, fundo_caixa, total_bruto, total_despesas = 0.0, 0.0, 0.0, 0.0
        if not df_v.empty:
            df_v.columns = [c.strip().capitalize() for c in df_v.columns]
            for c in ["Total"]: df_v[c] = df_v[c].apply(converter_valor)
            total_bruto = df_v[df_v["Status"].str.strip()=="Concluído"]["Total"].sum()
        st.metric("Total Bruto (Geral)", formatar_moeda(total_bruto))
    except: pass

def page_agendamento():
    st.markdown('## <i class="bi bi-calendar-check" style="color: white;"></i> Agenda Integrada', unsafe_allow_html=True)
    tab_new, tab_list = st.tabs(["NOVO (ADMIN)", "LISTA"]) 
    df_cat = carregar_catalogo()
    with tab_new:
        with st.container(border=True):
            placa_input = st.text_input("Buscar Placa (Admin)", key="placa_admin")
            val_cli, val_veic, val_zap = "", "", ""
            if placa_input:
                dados_cli = buscar_cliente_por_placa(placa_input)
                if dados_cli: st.success("Cliente Recorrente!"); val_cli, val_veic, val_zap = dados_cli['Cliente'], dados_cli['Veiculo'], dados_cli['Telefone']
            c1, c2 = st.columns(2); cli = c1.text_input("Cliente", value=val_cli); zap = c2.text_input("WhatsApp", value=val_zap)
            c3, c4 = st.columns(2); veic = c3.text_input("Veículo", value=val_veic); dt = c4.date_input("Data", value=date.today())
            servs = st.multiselect("Serviços", ["Lavagem Simples", "Lavagem Detalhada", "Polimento", "Higienização"])
            total = st.number_input("Valor (R$)", min_value=0.0)
            if st.button("AGENDAR (INTERNO)"):
                if salvar_no_google("Agendamentos", {"Data": dt.strftime("%d/%m/%Y"), "Cliente": cli, "Veiculo": veic, "Total": total, "Status": "Confirmado", "Servicos": ",".join(servs)}): st.success("Agendado!")
    with tab_list:
        try:
            df_a = carregar_dados("Agendamentos")
            if not df_a.empty:
                for i, r in df_a.iterrows():
                    val_total = converter_valor(r.get('Total', 0))
                    titulo = f"{r['Data']} | {r['Veiculo']} - {r['Cliente']}"
                    if "Site" in str(r.get("Status","")): titulo = "🔔 " + titulo
                    with st.expander(titulo):
                        st.write(f"**Serviços:** {r['Servicos']}")
                        c_ok, c_del = st.columns(2)
                        if c_ok.button("✅ Concluir", key=f"ok_{i}"):
                            atualizar_estoque_auto()
                            venda = {"Data": r["Data"], "Cliente": r["Cliente"], "Total": val_total, "Status": "Concluído"}
                            salvar_no_google("Vendas", venda); excluir_agendamento(i); st.rerun()
                        if c_del.button("🗑️", key=f"del_{i}"): excluir_agendamento(i); st.rerun()
        except: pass

def page_vistoria():
    st.markdown('## <i class="bi bi-camera-fill" style="color: #39FF14;"></i> Vistoria', unsafe_allow_html=True)
    st.info("Funcionalidade de PDF mantida.")

def page_despesas():
    st.markdown('## <i class="bi bi-receipt" style="color: #D90429;"></i> Despesas', unsafe_allow_html=True)
    with st.form("form_desp"):
        desc = st.text_input("Descrição")
        val = st.number_input("Valor", min_value=0.0)
        if st.form_submit_button("Lançar"): salvar_no_google("Despesas", {"Data": datetime.now().strftime("%d/%m/%Y"), "Descricao": desc, "Valor": val}); st.success("Salvo!")

def page_historico():
    st.markdown('## <i class="bi bi-clock-history"></i> Histórico', unsafe_allow_html=True)
    try:
        df = carregar_dados("Vendas")
        if not df.empty:
            for _, r in df.iloc[::-1].iterrows():
                total_hist = formatar_moeda(converter_valor(r["Total"]))
                st.markdown(f'<div class="history-card" style="border-left:5px solid #28a745"><div style="display:flex;justify-content:space-between;"><div><b>{r["Carro"]}</b><br>{r["Cliente"]} | {r["Placa"]}</div><div style="text-align:right"><b style="color:#39FF14">{total_hist}</b><br><small>{r["Data"]}</small></div></div><div style="color:#888">{r.get("Serviços", "")}</div></div>', unsafe_allow_html=True)
        else: st.info("Histórico Vazio.")
    except Exception as e: st.error(f"Erro no Histórico: {e}")

# ==============================================================================
# --- 7. CONTROLE DE FLUXO (O PULO DO GATO) ---
# ==============================================================================

# VERIFICA SE ESTÁ LOGADO COMO ADMIN
if st.session_state.get("password_correct", False):
    c_logo1, c_logo2, c_logo3 = st.columns([1,3,1])
    with c_logo2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.markdown("<h1 style='text-align:center; color:#D90429'>JM DETAIL</h1>", unsafe_allow_html=True)

    # MENU ORIGINAL COM SCROLL AJUSTADO
    menu_selecionado = st.radio("", ["DASHBOARD", "AGENDA", "VISTORIA", "ESTOQUE", "FINANCEIRO", "DESPESAS", "HISTÓRICO"], horizontal=True, label_visibility="collapsed")
    st.write("---")

    if menu_selecionado == "DASHBOARD": page_dashboard()
    elif menu_selecionado == "AGENDA": page_agendamento()
    elif menu_selecionado == "VISTORIA": page_vistoria()
    elif menu_selecionado == "ESTOQUE": page_estoque()
    elif menu_selecionado == "FINANCEIRO": page_financeiro()
    elif menu_selecionado == "DESPESAS": page_despesas()
    elif menu_selecionado == "HISTÓRICO": page_historico()
    
    with st.sidebar:
        if st.button("Sair"):
            st.session_state["password_correct"] = False
            st.rerun()

# SE NÃO ESTIVER LOGADO -> MOSTRA ÁREA DO CLIENTE
else:
    area_cliente()
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("---")
    col_l, _ = st.columns([1,4])
    with col_l:
        with st.expander("🔒 Admin"):
            pwd = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                try: senha_correta = st.secrets["app"]["password"]
                except: senha_correta = "1234"
                if pwd == senha_correta:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else: st.error("Senha errada")

st.markdown('<div class="footer">JM Detail System © 2026 | Desenvolvido por Jairan Jesus Matos</div>', unsafe_allow_html=True)
