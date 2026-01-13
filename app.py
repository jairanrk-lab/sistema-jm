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

# --- 1. CONFIGURAÇÃO INICIAL (Obrigatório ser a primeira linha) ---
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# --- 2. CSS & ESTILO (CORREÇÃO DO MENU E VISUAL) ---
# ==============================================================================
st.markdown("""
<style>
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    
    html, body, p, h1, h2, h3, h4, h5, h6, li, a, button, input, textarea, label, .stTextInput, .stNumberInput, .stSelectbox {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Fundo Dark Glass */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #000000 80%);
    }
    .block-container { padding-top: 1rem; padding-bottom: 6rem; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    
    /* Inputs Estilizados */
    input, .stSelectbox > div > div, .stMultiSelect > div > div {
        background-color: rgba(30, 30, 30, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important; border-radius: 10px !important;
    }
    
    /* CORREÇÃO DO MENU SUPERIOR (Rolagem Lateral Suave) */
    div[role="radiogroup"] { 
        display: flex !important;
        flex-wrap: nowrap !important; /* Não quebra linha */
        overflow-x: auto !important; /* Permite rolar */
        white-space: nowrap !important;
        gap: 10px !important;
        padding-bottom: 10px !important; /* Espaço para não cortar a sombra */
        margin-bottom: 20px !important;
    }
    
    /* Botões do Menu */
    div[role="radiogroup"] label {
        flex: 0 0 auto !important; /* Tamanho fixo */
        min-width: 100px !important;
        text-align: center !important;
        background-color: rgba(40,40,40,0.6) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        padding: 10px 15px !important;
        color: #ccc !important;
        transition: all 0.3s ease !important;
    }
    
    div[role="radiogroup"] label:hover {
        border-color: #D90429 !important;
        color: white !important;
    }
    
    /* Botão Selecionado */
    div[role="radiogroup"] label[data-checked="true"] { 
        background: linear-gradient(135deg, #D90429, #8D021F) !important; 
        color: white !important; 
        border: 1px solid rgba(255,255,255,0.3) !important;
        box-shadow: 0 4px 10px rgba(217, 4, 41, 0.4) !important;
    }

    /* Cards e Métricas */
    .dash-card { 
        border-radius: 16px; padding: 20px; color: white; margin-bottom: 15px; height: 130px;
        display: flex; flex-direction: column; justify-content: center; 
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Bordas Coloridas dos Cards */
    .bg-orange { border-left: 5px solid #ff9800; }
    .bg-blue   { border-left: 5px solid #00b4db; }
    .bg-red    { border-left: 5px solid #D90429; }
    .bg-green  { border-left: 5px solid #39FF14; }
    .bg-gold   { border-left: 5px solid #FFD700; }

    /* Botão Principal */
    div.stButton > button { 
        background: #D90429 !important; color: white; border-radius: 10px; height: 50px; font-weight: bold; border:none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: rgba(0,0,0,0.9); text-align: center; padding: 10px; font-size: 12px; color: #666; z-index: 999; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- 3. FUNÇÕES DE BACKEND (Conexão e Dados) ---
# ==============================================================================

def check_password():
    if st.session_state.get("password_correct", False): return True
    if st.query_params.get("logado") == "true":
        st.session_state["password_correct"] = True
        return True
    return False

def converter_valor(valor):
    if isinstance(valor, (int, float)): return float(valor)
    try: return float(str(valor).replace("R$", "").replace(".", "").replace(",", ".").strip() or 0)
    except: return 0.0

def formatar_moeda(valor):
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def limpar_numero(num): return re.sub(r'\D', '', str(num)) if num else ""

def conectar_google_sheets():
    ID_FIXO = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg"
    try:
        if "app" in st.secrets: ID_FIXO = st.secrets["app"].get("spreadsheet_id", ID_FIXO)
        if os.path.exists("chave_google.json"): client = gspread.service_account(filename="chave_google.json")
        elif "gcp_service_account" in st.secrets: client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        else: return None
        return client.open_by_key(ID_FIXO)
    except: return None

def carregar_dados(aba):
    s = conectar_google_sheets()
    try: return pd.DataFrame(s.worksheet(aba).get_all_records()) if s else pd.DataFrame()
    except: return pd.DataFrame()

def salvar_no_google(aba, dados):
    s = conectar_google_sheets()
    if not s: return False
    try:
        ws = s.worksheet(aba)
        if not ws.row_values(1): ws.append_row(list(dados.keys()))
        ws.append_row([dados.get(c, "") for c in ws.row_values(1)])
        return True
    except: return False

def atualizar_estoque_auto():
    s = conectar_google_sheets()
    if s:
        try:
            ws = s.worksheet("Estoque"); d = ws.get_all_values(); head = [x.lower() for x in d[0]]
            ia, ig = -1, -1
            for i, h in enumerate(head):
                if "atual" in h: ia = i
                if "gasto" in h: ig = i
            if ia >= 0 and ig >= 0:
                for i in range(1, len(d)):
                    try: 
                        atual, gasto = float(d[i][ia].replace(",",".") or 0), float(d[i][ig].replace(",",".") or 0)
                        if gasto > 0: ws.update_cell(i+1, ia+1, max(0, atual - gasto))
                    except: pass
        except: pass

@st.cache_data(ttl=300)
def obter_custo_fixo():
    try:
        df = pd.DataFrame(conectar_google_sheets().worksheet("Config").get_all_records())
        return converter_valor(df[df["Chave"]=="CustoFixo"].iloc[0]["Valor"])
    except: return 0.0

@st.cache_data(ttl=60)
def carregar_catalogo():
    try: return pd.DataFrame(conectar_google_sheets().worksheet("Catalogo").get_all_records())
    except: return pd.DataFrame()

def buscar_cliente(placa):
    try:
        df = pd.concat([carregar_dados("Agendamentos"), carregar_dados("Vendas")], ignore_index=True)
        if df.empty: return None
        busca = placa.replace("-","").upper().strip()
        col = next((c for c in df.columns if "placa" in c.lower()), None)
        if col:
            res = df[df[col].astype(str).str.replace("-","").str.upper().str.strip() == busca]
            if not res.empty:
                r = res.iloc[-1]
                return {
                    "Cliente": r.get(next((c for c in df.columns if "cliente" in c.lower()), ""), ""),
                    "Veiculo": r.get(next((c for c in df.columns if "veic" in c.lower() or "carro" in c.lower()), ""), ""),
                    "Telefone": str(r.get(next((c for c in df.columns if "tel" in c.lower()), ""), ""))
                }
    except: pass
    return None

# --- PDF GENERATOR ---
def gerar_pdf(tipo, dados, imagens=None):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"JM DETAIL - {tipo.upper()}", ln=True, align='C')
    pdf.set_font("Arial", size=10); pdf.cell(0, 10, "Estetica Automotiva Premium | (75) 99830-3753", ln=True, align='C'); pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    texto_cli = f"CLIENTE: {dados.get('Cliente','')} | VEICULO: {dados.get('Veiculo','')} | DATA: {dados.get('Data','')}"
    pdf.cell(0, 8, texto_cli.encode('latin-1','replace').decode('latin-1'), ln=True); pdf.ln(5)
    if tipo == "Vistoria" and imagens:
        pdf.cell(0, 10, "REGISTRO FOTOGRAFICO", ln=True, align='C')
        x, y, w, h = 10, pdf.get_y(), 90, 65; col = 0
        for tit, path in imagens.items():
            if path and os.path.exists(path):
                if y + h > 260: pdf.add_page(); y = 20
                pdf.image(path, x=x + (col*95), y=y, w=w, h=h); col += 1
                if col > 1: col=0; y += h + 10
    elif tipo == "Orcamento":
        pdf.set_fill_color(220,220,220); pdf.cell(140, 8, "Descricao", 1, 0, 'L', 1); pdf.cell(50, 8, "Valor", 1, 1, 'C', 1)
        pdf.set_font("Arial", size=10); pdf.cell(140, 8, str(dados.get('Servicos','')).encode('latin-1','replace').decode('latin-1'), 1)
        pdf.cell(50, 8, formatar_moeda(dados.get('Total',0)), 1, 1, 'C')
    return pdf.output(dest="S").encode("latin-1")

# ==============================================================================
# --- 4. DEFINIÇÃO DAS PÁGINAS (IMPORTANTÍSSIMO: DEFINIR ANTES DE USAR) ---
# ==============================================================================

# 4.1 DASHBOARD
def page_dashboard():
    st.markdown("## 📊 Painel de Controle (BI)")
    try:
        df_v = carregar_dados("Vendas"); df_d = carregar_dados("Despesas")
        rec, desp, custo_f = 0.0, 0.0, obter_custo_fixo()
        
        if not df_v.empty:
            cols_v = [c.strip().capitalize() for c in df_v.columns]; df_v.columns = cols_v
            df_v["Total_N"] = df_v["Total"].apply(converter_valor)
            df_v["Data_dt"] = pd.to_datetime(df_v["Data"], dayfirst=True, errors='coerce')
            hoje = datetime.now()
            df_mes = df_v[(df_v["Data_dt"].dt.month == hoje.month) & (df_v["Data_dt"].dt.year == hoje.year)]
            rec = df_mes[df_mes["Status"].str.strip()=="Concluído"]["Total_N"].sum()
        
        if not df_d.empty:
            cols_d = [c.strip().capitalize() for c in df_d.columns]; df_d.columns = cols_d
            df_d["Valor_N"] = df_d["Valor"].apply(converter_valor)
            df_d["Data_dt"] = pd.to_datetime(df_d["Data"], dayfirst=True, errors='coerce')
            df_d_mes = df_d[(df_d["Data_dt"].dt.month == hoje.month) & (df_d["Data_dt"].dt.year == hoje.year)]
            desp = df_d_mes["Valor_N"].sum()

        lucro = (rec * 0.5) - desp - custo_f
        
        # KPIS (VISUAL RESTAURADO)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="dash-card bg-blue"><h3>FATURAMENTO</h3><h1>{formatar_moeda(rec)}</h1></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="dash-card bg-red"><h3>DESPESAS</h3><h1>{formatar_moeda(desp + custo_f)}</h1></div>', unsafe_allow_html=True)
        cor_lucro = "#39FF14" if lucro >= 0 else "#D90429"
        c3.markdown(f'<div class="dash-card bg-green"><h3>LUCRO LÍQUIDO</h3><h1 style="color:{cor_lucro}">{formatar_moeda(lucro)}</h1></div>', unsafe_allow_html=True)

        st.write("---")
        
        # GRÁFICOS
        if not df_v.empty:
            g1, g2 = st.columns(2)
            with g1:
                st.markdown("### 🍩 Serviços Mais Vendidos")
                if "Carro" in df_v.columns:
                    df_pie = df_v["Carro"].value_counts().reset_index().head(5)
                    df_pie.columns = ["Serviço/Carro", "Qtd"]
                    fig_pie = px.pie(df_pie, values="Qtd", names="Serviço/Carro", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                    st.plotly_chart(fig_pie, use_container_width=True)
            with g2:
                st.markdown("### 📈 Tendência Mensal")
                df_line = df_v.groupby(df_v["Data_dt"].dt.date)["Total_N"].sum().reset_index()
                df_line.columns = ["Data", "Valor"]
                # COR DO GRÁFICO: CINZA (ORIGINAL)
                fig_line = px.line(df_line, x="Data", y="Valor", markers=True)
                fig_line.update_traces(line_color="#E0E0E0", line_width=3)
                fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.05)", font_color="white", xaxis_showgrid=False)
                st.plotly_chart(fig_line, use_container_width=True)

    except Exception as e: st.error(f"Erro no Dashboard: {e}")

# 4.2 AGENDA
def page_agenda():
    st.markdown("## 📅 Agenda & Serviços")
    tab1, tab2 = st.tabs(["Novo", "Lista"])
    with tab1:
        with st.container(border=True):
            placa = st.text_input("Placa (Busca Rápida):")
            cli, veic, tel = "", "", ""
            if placa:
                res = buscar_cliente(placa)
                if res: 
                    st.success("Cliente Recorrente!")
                    cli, veic, tel = res["Cliente"], res["Veiculo"], res["Telefone"]
            c1, c2 = st.columns(2)
            nome = c1.text_input("Cliente", value=cli)
            zap = c2.text_input("WhatsApp", value=tel)
            carro = c1.text_input("Veículo", value=veic)
            dt = c2.date_input("Data", value=date.today())
            servs = st.multiselect("Serviços", ["Lavagem Simples", "Lavagem Detalhada", "Higienização", "Polimento", "Vitrificação"])
            total = st.number_input("Valor Total (R$)", min_value=0.0, step=10.0)
            if st.button("AGENDAR SERVIÇO", use_container_width=True):
                if salvar_no_google("Agendamentos", {"Data": dt.strftime("%d/%m/%Y"), "Cliente": nome, "Veiculo": carro, "Placa": placa, "Telefone": zap, "Servicos": ", ".join(servs), "Total": total, "Status": "Pendente"}):
                    st.success("Agendado!"); t_sleep.sleep(1); st.rerun()
    with tab2:
        df = carregar_dados("Agendamentos")
        if not df.empty:
            for i, r in df.iterrows():
                with st.expander(f"{r['Data']} - {r['Veiculo']} ({r['Cliente']})"):
                    st.write(f"**Serviços:** {r['Servicos']}")
                    c_ok, c_del = st.columns(2)
                    if c_ok.button("✅ Concluir", key=f"ok_{i}"):
                        atualizar_estoque_auto()
                        venda = r.to_dict(); venda["Status"] = "Concluído"; venda["Lucro Liquido"] = converter_valor(r["Total"])*0.5
                        salvar_no_google("Vendas", venda)
                        st.toast("Serviço Concluído!"); t_sleep.sleep(1); st.rerun()

# 4.3 VISTORIA
def page_vistoria():
    st.markdown("## 📷 Vistoria Cautelar")
    st.info("Use a câmera do celular para registrar avarias.")
    with st.form("vistoria_form"):
        placa = st.text_input("Placa do Veículo")
        avarias = st.multiselect("Avarias Visíveis", ["Risco Lataria", "Amassado", "Rodas Raladas", "Vidro Trincado", "Farol Quebrado"])
        fotos = st.file_uploader("Fotos", accept_multiple_files=True, type=["jpg","png"])
        if st.form_submit_button("GERAR PDF"):
            if placa:
                paths = {} 
                if fotos:
                    for i, f in enumerate(fotos):
                        p = f"temp_{i}.jpg"; 
                        with open(p, "wb") as w: w.write(f.getbuffer())
                        paths[f"Foto {i+1}"] = p
                pdf = gerar_pdf("Vistoria", {"Cliente": "Diverso", "Veiculo": "Ver Fotos", "Placa": placa, "Data": datetime.now().strftime("%d/%m/%Y"), "Avarias": avarias}, paths)
                st.download_button("BAIXAR PDF", pdf, "Vistoria.pdf", "application/pdf")
                for p in paths.values(): os.remove(p)

# 4.4 ESTOQUE
def page_estoque():
    st.markdown("## 📦 Estoque de Produtos")
    try:
        df = pd.DataFrame(conectar_google_sheets().worksheet("Estoque").get_all_records())
        if not df.empty:
            cols = st.columns(2)
            for i, r in df.iterrows():
                at = float(str(r["Atual_ml"]).replace(",","."))
                perc = min(at/5000, 1.0)
                cor = "#39FF14" if perc > 0.2 else "#D90429"
                with cols[i%2]:
                    st.markdown(f"""
                    <div style="border:1px solid #333; padding:10px; border-radius:10px; margin-bottom:10px; background:rgba(255,255,255,0.05)">
                        <b>{r['Produto']}</b><br><small>{int(at)} ml</small>
                        <div style="background:#444; height:5px; width:100%; margin-top:5px; border-radius:3px">
                            <div style="background:{cor}; height:5px; width:{int(perc*100)}%; border-radius:3px"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
    except: st.warning("Conexão necessária.")

# 4.5 FINANCEIRO
def page_financeiro():
    st.markdown("## 💰 Financeiro & Precificação")
    tab1, tab2 = st.tabs(["Caixa", "Calculadora"])
    with tab1:
        st.write("Resumo do Mês (Ver Dashboard para Gráficos)")
    with tab2:
        st.markdown("### 🧮 Calculadora de Lucro Real")
        c1, c2 = st.columns(2)
        prod_custo = c1.number_input("Custo Produtos (R$)", value=15.0)
        hora_trab = c2.number_input("Horas Trabalhadas", value=2.0)
        valor_hora = c1.number_input("Sua Hora (R$)", value=30.0)
        preco_venda = st.number_input("Preço Cobrado (R$)", value=100.0)
        custo_total = prod_custo + (hora_trab * valor_hora)
        lucro = preco_venda - custo_total
        margem = (lucro / preco_venda) * 100 if preco_venda else 0
        if lucro > 0: st.success(f"Lucro: {formatar_moeda(lucro)} ({margem:.1f}%)")
        else: st.error(f"Prejuízo: {formatar_moeda(lucro)}")

# 4.6 DESPESAS (ESSA FALTAVA!)
def page_despesas():
    st.markdown("## 📉 Lançar Despesas")
    with st.form("form_despesa"):
        desc = st.text_input("Descrição da Despesa")
        val = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
        dt = st.date_input("Data", value=date.today())
        if st.form_submit_button("LANÇAR DESPESA"):
            if salvar_no_google("Despesas", {"Data": dt.strftime("%d/%m/%Y"), "Descricao": desc, "Valor": val}):
                st.success("Despesa salva!")

# 4.7 HISTÓRICO (ESSA TAMBÉM!)
def page_historico():
    st.markdown("## 📜 Histórico de Clientes")
    try:
        df = carregar_dados("Vendas")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhuma venda registrada.")
    except: st.error("Erro ao carregar histórico.")

# ==============================================================================
# --- 5. CLIENTE (ÁREA PÚBLICA) ---
# ==============================================================================
def area_cliente():
    st.markdown("<br><br>", unsafe_allow_html=True)
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    st.markdown("<h2 style='text-align:center'>Agendamento Online</h2>", unsafe_allow_html=True)
    with st.container(border=True):
        nome = st.text_input("Seu Nome")
        carro = st.text_input("Modelo do Veículo")
        tel = st.text_input("WhatsApp")
        dt = st.date_input("Data Preferida", value=date.today())
        hr = st.selectbox("Horário", ["08:00 - Manhã", "13:00 - Tarde"])
        servs = st.multiselect("Serviços", ["Lavagem Simples", "Lavagem Detalhada", "Polimento", "Higienização"], placeholder="Selecione...")
        
        if st.button("SOLICITAR AGENDAMENTO", use_container_width=True):
            if nome and tel:
                dados = {"Data": dt.strftime("%d/%m/%Y"), "Hora": hr, "Cliente": nome, "Telefone": tel, "Veiculo": carro, "Servicos": ", ".join(servs), "Status": "Pendente (Site)"}
                salvar_no_google("Agendamentos", dados)
                st.success("Solicitação enviada! Entraremos em contato.")
                link = f"https://wa.me/5575998303753?text=Ola, agendei meu {carro} pelo site para dia {dt.strftime('%d/%m')}."
                st.markdown(f"<a href='{link}' target='_blank'><button style='background:#25D366; color:white; border:none; padding:10px; width:100%; border-radius:10px'>Finalizar no WhatsApp</button></a>", unsafe_allow_html=True)

# ==============================================================================
# --- 6. LOGO E NAVEGAÇÃO (LÓGICA PRINCIPAL) ---
# ==============================================================================

# Se estiver logado, mostra o Admin
if check_password():
    c_logo1, c_logo2, c_logo3 = st.columns([1,3,1])
    with c_logo2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    
    # Menu Superior
    menu = st.radio("", ["DASHBOARD", "AGENDA", "VISTORIA", "ESTOQUE", "FINANCEIRO", "DESPESAS", "HISTÓRICO"], horizontal=True, label_visibility="collapsed")
    
    # Controle de Páginas (AGORA TODAS DEFINIDAS)
    if menu == "DASHBOARD": page_dashboard()
    elif menu == "AGENDA": page_agenda()
    elif menu == "VISTORIA": page_vistoria()
    elif menu == "ESTOQUE": page_estoque()
    elif menu == "FINANCEIRO": page_financeiro()
    elif menu == "DESPESAS": page_despesas()
    elif menu == "HISTÓRICO": page_historico()
    
    # Botão Sair
    with st.sidebar:
        if st.button("SAIR DO SISTEMA"):
            st.session_state["password_correct"] = False
            st.rerun()

# Se NÃO estiver logado, mostra Área do Cliente + Botão de Login Discreto
else:
    area_cliente()
    st.write("---")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        with st.expander("🔒 Área Restrita"):
            pwd = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                try: s = st.secrets["app"]["password"]
                except: s = "1234"
                if pwd == s:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else: st.error("Senha incorreta")

st.markdown('<div class="footer">JM Detail System © 2026</div>', unsafe_allow_html=True)
