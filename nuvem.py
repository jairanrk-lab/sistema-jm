import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date, time
from fpdf import FPDF
import gspread
import os
import time as t_sleep

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide")

# ==============================================================================
# --- 2. SISTEMA DE LOGIN INTELIGENTE 🔒 ---
# ==============================================================================
def check_password():
    try:
        query_params = st.query_params
        if query_params.get("acesso_liberado") == "sim_mestre":
            return True
    except: pass

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Ícone Bootstrap no Login
    st.markdown("### <i class='bi bi-shield-lock-fill' style='color:#D90429'></i> Acesso Restrito - JM Detail", unsafe_allow_html=True)
    pwd = st.text_input("Digite a senha de acesso:", type="password")
    
    if st.button("ACESSAR SISTEMA"):
        if pwd == "J@i911458": 
            st.session_state["password_correct"] = True
            try: st.query_params["acesso_liberado"] = "sim_mestre"
            except: pass
            st.rerun()
        else:
            st.error("Senha incorreta.")
    return False

if not check_password():
    st.stop()

# ==============================================================================
# --- 3. ESTILO CSS "V6.42" (ESTILO MAXTON + ÍCONES DINÂMICOS) 🌑 ---
# ==============================================================================
st.markdown("""
<style>
    /* --- IMPORTANDO FONTE MONTSERRAT --- */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    
    /* --- IMPORTANDO ÍCONES BOOTSTRAP (PREMIUM) --- */
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif !important;
    }

    /* --- FUNDO GERAL (PRETO ABSOLUTO) --- */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { 
        background-color: #000000 !important;
    }
    [data-testid="stSidebar"] { border-right: 1px solid #1a1a1a !important; }

    /* --- AJUSTE DA LOGO NO SIDEBAR --- */
    [data-testid="stSidebar"] img {
        width: 100% !important;
        transform: scale(1.15); 
        margin-top: 0px !important;
        margin-bottom: 20px !important;
        filter: none !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1rem !important; 
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Textos Gerais */
    h1, h2, h3, h4, h5, h6, p, label, span, div { color: white !important; }

    /* Estilo para os Títulos com Ícones (H1 Customizado) */
    .custom-title {
        display: flex;
        align-items: center;
        gap: 15px;
        font-weight: 700;
        font-size: 2.2rem;
        margin-bottom: 20px;
        letter-spacing: -1px;
    }
     /* Estilo para os Subtítulos com Ícones (H3 Customizado) */
    .custom-subtitle {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 600;
        font-size: 1.5rem;
        margin-bottom: 15px;
        margin-top: 10px;
    }

    /* --- CORREÇÃO TOOLTIP DO GRÁFICO (TEXTO PRETO) --- */
    #vg-tooltip-element {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #333 !important;
        font-family: 'Montserrat', sans-serif !important;
        padding: 8px !important;
        border-radius: 6px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
    }
    #vg-tooltip-element span, #vg-tooltip-element div, #vg-tooltip-element td {
        color: #000000 !important;
    }

    /* --- INPUTS --- */
    input, textarea, select { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; 
        caret-color: #000000 !important; 
        font-family: 'Montserrat', sans-serif !important;
    }
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTimeInput input { background-color: #ffffff !important; border: 1px solid #333 !important; }

    /* --- CALENDÁRIO & DROPDOWNS --- */
    div[data-baseweb="calendar"], div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] { background-color: #ffffff !important; color: #000000 !important; }
    div[data-baseweb="calendar"] div, div[data-baseweb="select"] div, li[role="option"] div { color: #000000 !important; font-family: 'Montserrat', sans-serif !important; }
    div[data-baseweb="calendar"] button { color: #000000 !important; }
    div[data-baseweb="select"] svg { fill: #000000 !important; }
    li[role="option"] { background-color: #ffffff !important; }
    div[data-baseweb="calendar"] button[aria-selected="true"], li[role="option"][aria-selected="true"], li[role="option"]:hover { background-color: #D90429 !important; color: white !important; }
    div[data-baseweb="calendar"] button[aria-selected="true"] { color: white !important; }
    li[role="option"]:hover div, li[role="option"][aria-selected="true"] div { color: white !important; }

    /* BOTÕES GERAIS (TEXTO LIMPO) */
    div.stButton > button, div.stDownloadButton > button { 
        background-color: #D90429 !important; 
        color: white !important; 
        border: none !important; 
        font-weight: 700 !important; 
        border-radius: 6px !important; 
        font-family: 'Montserrat', sans-serif !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important; 
        font-size: 14px !important;
        padding: 10px 24px !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover { background-color: #EF233C !important; transform: scale(1.02); }

    /* --- SIDEBAR ITENS (BOTÕES DO MENU UNIFORMES) --- */
    div[role="radiogroup"] label > div:first-child { display: none !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] label { 
        padding: 14px 20px !important; 
        margin-bottom: 8px !important; 
        background-color: #0a0a0a !important; 
        border-radius: 8px !important; 
        border: 1px solid #222 !important; 
        color: #aaa !important; 
        display: flex !important; 
        width: 100% !important;
        transition: all 0.2s ease !important; 
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover { background-color: #1a1a1a !important; border-color: #D90429 !important; transform: translateX(5px); }
    [data-testid="stSidebar"] div[role="radiogroup"] [aria-checked="true"] { background-color: #D90429 !important; color: white !important; border: none !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] [aria-checked="true"] p { color: white !important; font-weight: bold !important; }

    /* CARDS ESTILIZADOS */
    .dash-card { border-radius: 12px; padding: 20px; color: white !important; margin-bottom: 15px; border: 1px solid #222; font-family: 'Montserrat', sans-serif !important; position: relative; overflow: hidden; }
    
    /* Ícone de fundo translúcido nos cards */
    .card-icon-bg { position: absolute; right: -10px; bottom: -10px; font-size: 80px; opacity: 0.15; color: white; transform: rotate(-15deg); pointer-events: none; }

    .history-card, .agenda-card { background-color: #111111 !important; border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 5px solid #28a745; box-shadow: 0 4px 10px rgba(255,255,255,0.03); font-family: 'Montserrat', sans-serif !important;}
    .agenda-card { border-left-color: #00B4DB; }
    
    .bg-orange { background: linear-gradient(160deg, #FF9800 0%, #F57C00 100%); }
    .bg-blue { background: linear-gradient(160deg, #00B4DB 0%, #0083B0 100%); }
    .bg-red { background: linear-gradient(160deg, #D90429 0%, #8D021F 100%); }
    .bg-green { background: linear-gradient(160deg, #11998e 0%, #38ef7d 100%); }
    .bg-purple { background: linear-gradient(160deg, #8E2DE2 0%, #4A00E0 100%); }
    .bg-dark { background: linear-gradient(160deg, #222 0%, #000000 100%); border: 1px solid #444; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES ---
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_resource
def conectar_google_sheets():
    ID = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg"
    try:
        if os.path.exists("chave_google.json"): client = gspread.service_account(filename="chave_google.json")
        else: client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        return client.open_by_key(ID)
    except: return None

def carregar_dados(aba):
    sheet = conectar_google_sheets()
    if sheet is None: return pd.DataFrame()
    try: return pd.DataFrame(sheet.worksheet(aba).get_all_records())
    except: return pd.DataFrame()

def salvar_no_google(aba, linha):
    sheet = conectar_google_sheets()
    if sheet is None: return False
    try:
        ws = sheet.worksheet(aba)
        if not ws.get_all_values(): ws.append_row(list(linha.keys()))
        ws.append_row(list(linha.values()))
        return True
    except: return False

def excluir_agendamento(indice_linha):
    sheet = conectar_google_sheets()
    if sheet is None: return False
    try:
        ws = sheet.worksheet("Agendamentos")
        ws.delete_rows(indice_linha + 2) 
        return True
    except: return False

@st.cache_data
def carregar_catalogo():
    return pd.DataFrame({
        "Categoria": ["Hatch/Compacto", "Sedã", "SUV/Caminhonete", "Picapes Grandes", "Vans/Utilitários", "Motocicleta"],
        "Lavagem Simples": [40.0, 50.0, 60.0, 70.0, 80.0, 30.0],
        "Lavagem Técnica": [150.0, 170.0, 190.0, 210.0, 230.0, 100.0],
        "Higienização Interna": [300.0, 300.0, 300.0, 350.0, 400.0, 0.0],
        "Restauração Faróis": [200.0, 200.0, 200.0, 200.0, 200.0, 100.0],
        "Cristalização Vidros": [90.0, 120.0, 150.0, 150.0, 150.0, 50.0],
        "Vitrificação Pintura": [800.0, 900.0, 1100.0, 1300.0, 1300.0, 500.0]
    })

def obter_icone_veiculo(categoria_texto):
    if not isinstance(categoria_texto, str): return '<i class="bi bi-car-front-fill"></i>'
    cat_lower = categoria_texto.lower()
    if "moto" in cat_lower: return '<i class="bi bi-motorcycle"></i>'
    elif "suv" in cat_lower or "picape" in cat_lower or "caminhonete" in cat_lower: return '<i class="bi bi-truck-front-fill"></i>'
    elif "van" in cat_lower or "utilit" in cat_lower: return '<i class="bi bi-bus-front-fill"></i>'
    else: return '<i class="bi bi-car-front-fill"></i>'

def gerar_pdf(cliente, carro, placa, data_servico, servicos_com_precos, total):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"): 
        pdf.image("logo.png", x=55, y=10, w=100) 
        pdf.ln(35) 
    else: 
        pdf.ln(20)
    def txt(t): return t.encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Arial", "B", 16); pdf.cell(0, 10, txt=txt("JM DETAIL - Estética Automotiva Premium"), ln=True, align='C')
    pdf.set_font("Arial", size=10); pdf.cell(0, 10, txt=txt("Tucano - BA | Rua São João, 54 | (75) 99830-3753"), ln=True, align='C')
    pdf.ln(10); pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt=txt(f"CLIENTE: {cliente}"), ln=True)
    pdf.cell(0, 10, txt=txt(f"VEÍCULO: {carro} | PLACA: {placa}"), ln=True)
    pdf.cell(0, 10, txt=txt(f"DATA: {data_servico}"), ln=True); pdf.ln(5)
    pdf.set_fill_color(240, 240, 240); pdf.cell(140, 10, txt("Pacote de Serviços"), border=1, fill=True)
    pdf.cell(50, 10, txt="Valor", border=1, ln=True, fill=True, align='C'); pdf.set_font("Arial", size=12)
    for s, v in servicos_com_precos.items():
        t_s = (s[:60] + '...') if len(s) > 60 else s
        pdf.cell(140, 10, txt=txt(t_s), border=1); pdf.cell(50, 10, txt=txt(f"R$ {v:.2f}"), border=1, ln=True, align='C')
    pdf.ln(5); pdf.set_font("Arial", "B", 14); pdf.cell(140, 10, txt="TOTAL", align='R')
    pdf.cell(50, 10, txt=txt(f"R$ {total:.2f}"), border=1, align='C')
    pdf.ln(20)
    if os.path.exists("assinatura.png"): pdf.image("assinatura.png", x=130, y=pdf.get_y(), w=40); pdf.ln(2); pdf.set_font("Arial", "I", 8); pdf.cell(0, 5, txt=txt("Assinado Digitalmente por JM Detail"), ln=True, align='R')
    return pdf.output(dest="S").encode("latin-1")

# --- PÁGINAS ---
def page_dashboard():
    # --- AQUI ESTA A ALTERACAO DO TESTE (PAINEL TESTE 123) ---
    st.markdown('<h1 class="custom-title"><i class="bi bi-speedometer2" style="color: #00B4DB;"></i> PAINEL GESTÃO PROFISSIONAL</h1>', unsafe_allow_html=True)
    
    df_v = carregar_dados("Vendas"); df_d = carregar_dados("Despesas"); df_a = carregar_dados("Agendamentos")
    receita, despesa, pendente, count_p, lucro_vendas = 0.0, 0.0, 0.0, 0, 0.0
    if not df_v.empty:
        for c in ["Total", "Lucro Liquido"]:
            df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0)
        receita = df_v[df_v["Status"]=="Concluído"]["Total"].sum()
        pendente = df_v[df_v["Status"]=="Orçamento/Pendente"]["Total"].sum()
        count_p = len(df_v[df_v["Status"]=="Orçamento/Pendente"])
        lucro_vendas = df_v[df_v["Status"]=="Concluído"]["Lucro Liquido"].sum()
    if not df_d.empty:
        despesa = pd.to_numeric(df_d["Valor"].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0).sum()
    lucro_total = lucro_vendas - despesa
    cor_lucro = "bg-green" if lucro_total >= 0 else "bg-red"
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="dash-card bg-orange"><i class="bi bi-hourglass-split card-icon-bg"></i><h4>PENDENTES ({count_p})</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(pendente)}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="dash-card bg-blue"><i class="bi bi-currency-dollar card-icon-bg"></i><h4>FATURAMENTO</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(receita)}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="dash-card bg-red"><i class="bi bi-graph-down-arrow card-icon-bg"></i><h4>DESPESAS</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(despesa)}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="dash-card {cor_lucro}"><i class="bi bi-wallet2 card-icon-bg"></i><h4>LUCRO LÍQUIDO</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_total)}</div></div>', unsafe_allow_html=True)
    st.write("---")
    col_g, col_a = st.columns([2, 1])
    with col_g:
        st.markdown('<h3 class="custom-subtitle"><i class="bi bi-graph-up-arrow" style="color: #39FF14;"></i> Performance</h3>', unsafe_allow_html=True)
        if not df_v.empty:
            # --- GRÁFICO ESTILO "MAXTON" (CURVAS + NEON) ---
            base = alt.Chart(df_v).encode(x=alt.X('Data', title=None, axis=alt.Axis(labelColor='white')))
            
            # Barras Neon
            bars = base.mark_bar(size=40, cornerRadiusEnd=10).encode(
                y=alt.Y('Total', axis=None),
                # Degradê simulado com cores vibrantes
                color=alt.Color('Status', scale=alt.Scale(domain=['Concluído', 'Orçamento/Pendente'], range=['#00F260', '#FF0080']), legend=None),
                tooltip=['Data', 'Cliente', 'Carro', 'Total', 'Lucro Liquido']
            )
            
            # Linha Curva (Interpolate = Natural para fazer ondas)
            line = base.mark_line(
                color='#0575E6', # Azul elétrico
                strokeWidth=4, 
                interpolate='natural' # AQUI ESTÁ O SEGREDO DA CURVA SUAVE
            ).encode(
                y=alt.Y('Lucro Liquido', axis=None),
                tooltip=['Data', 'Lucro Liquido']
            )
            
            chart = alt.layer(bars, line).properties(
                height=380, background='transparent'
            ).configure_view(strokeWidth=0).configure_axis(grid=False, domain=False, ticks=False)
            st.altair_chart(chart, use_container_width=True)
    with col_a:
        st.markdown('<h3 class="custom-subtitle"><i class="bi bi-calendar-event" style="color: white;"></i> Próximos na Agenda</h3>', unsafe_allow_html=True)
        if df_a.empty: st.info("Agenda livre.")
        else:
            for _, r in df_a.tail(4).iloc[::-1].iterrows():
                cat_atual = r.get("Categoria", "")
                icone_veiculo = obter_icone_veiculo(cat_atual)
                st.markdown(f"""
                <div class="agenda-card">
                    <div style="margin-bottom:8px; font-weight:bold; color:#00B4DB"><i class="bi bi-calendar4-week"></i> {r["Data"]} &nbsp;|&nbsp; <i class="bi bi-clock"></i> {r["Hora"]}</div>
                    <div style="font-size:18px; font-weight:bold; margin-bottom:5px">{icone_veiculo} {r["Veiculo"]}</div>
                    <div style="color:#aaa; font-size:14px; margin-bottom:5px"><i class="bi bi-person-fill"></i> {r["Cliente"]}</div>
                    <div style="font-size:13px; color:#ddd; margin-bottom:10px"><i class="bi bi-tools"></i> {r["Servicos"]}</div>
                    <div style="font-size:20px; font-weight:bold; color:#39FF14">{formatar_moeda(float(r["Total"]))}</div>
                </div>
                """, unsafe_allow_html=True)

def page_financeiro():
    st.markdown('<h1 class="custom-title"><i class="bi bi-cash-coin" style="color: #28a745;"></i> Gestão Financeira</h1>', unsafe_allow_html=True)
    st.info("💡 Como funciona: O saldo 'A Pagar' soma apenas o que está 'Pendente' na planilha.")
    df_v = carregar_dados("Vendas")
    comissao_pendente = 0.0
    fundo_caixa_acumulado = 0.0
    if not df_v.empty:
        if "Status Comissao" not in df_v.columns: df_v["Status Comissao"] = "Pendente"
        for c in ["Valor Comissao", "Fundo Caixa"]:
            if c in df_v.columns: df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0)
        df_pendentes = df_v[df_v["Status Comissao"] != "Pago"]
        comissao_pendente = df_pendentes["Valor Comissao"].sum()
        fundo_caixa_acumulado = df_v["Fundo Caixa"].sum()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="dash-card bg-purple"><i class="bi bi-person-badge-fill card-icon-bg"></i><h4>A PAGAR (PENDENTE)</h4><div style="font-size:32px;font-weight:bold">{formatar_moeda(comissao_pendente)}</div><p style="margin-top:10px; opacity:0.8">Comissão da Equipe/Irmão</p></div>""", unsafe_allow_html=True)
        if comissao_pendente > 0:
            if st.button("CONFIRMAR PAGAMENTO REALIZADO", use_container_width=True):
                sheet = conectar_google_sheets(); ws = sheet.worksheet("Vendas"); dados_planilha = ws.get_all_records()
                try:
                    header = ws.row_values(1); col_idx = header.index("Status Comissao") + 1; updates = []
                    for i, linha in enumerate(dados_planilha):
                        v_float = pd.to_numeric(str(linha.get("Valor Comissao", "0")).replace('R$', '').replace(',', '.'), errors='coerce')
                        if v_float > 0 and str(linha.get("Status Comissao", "")) != "Pago": ws.update_cell(i + 2, col_idx, "Pago")
                    st.success("Pagamento registrado!"); st.rerun()
                except ValueError: st.error("Erro: Coluna 'Status Comissao' não encontrada.")
    with c2:
        st.markdown(f"""<div class="dash-card bg-dark"><i class="bi bi-safe2-fill card-icon-bg"></i><h4>CAIXA EMPRESA (10%)</h4><div style="font-size:32px;font-weight:bold">{formatar_moeda(fundo_caixa_acumulado)}</div><p style="margin-top:10px; opacity:0.8">Acumulado total para insumos.</p></div>""", unsafe_allow_html=True)
    st.write("---"); st.subheader("Extrato de Comissões"); 
    if not df_v.empty: st.dataframe(df_v[df_v["Status Comissao"] != "Pago"][["Data", "Carro", "Valor Comissao", "Status Comissao"]], use_container_width=True)

def page_agendamento():
    st.markdown('<h1 class="custom-title"><i class="bi bi-calendar-check" style="color: white;"></i> Agenda Integrada</h1>', unsafe_allow_html=True)
    tab_list, tab_new = st.tabs(["LISTA DE SERVIÇOS", "NOVO AGENDAMENTO"]) 
    df_cat = carregar_catalogo()
    with tab_new:
        st.markdown("### Dados do Agendamento")
        c1, c2 = st.columns(2)
        cli = c1.text_input("Cliente"); veic = c1.text_input("Modelo Veículo"); placa = c1.text_input("Placa")
        dt = c2.date_input("Data", value=date.today(), format="DD/MM/YYYY")
        hr_obj = c2.time_input("Horário", value=time(8, 0), step=60); hr = hr_obj.strftime("%H:%M")
        cat = c2.selectbox("Categoria:", df_cat["Categoria"])
        servs_disp = [c for c in df_cat.columns if c != "Categoria"]
        escolhidos = st.multiselect("Serviços:", servs_disp, placeholder="Escolha os serviços do catálogo...")
        st.write("---")
        extra_n = st.text_input("Serviço Extra (Opcional)")
        extra_v = st.number_input("Valor do Serviço Extra (R$)", min_value=0.0)
        quem = st.radio("Quem vai executar?", ["Eu Mesmo", "Irmão/Equipe"], horizontal=True)
        precos_dict = {s: df_cat[df_cat["Categoria"] == cat][s].values[0] for s in escolhidos}
        total = sum(precos_dict.values()) + extra_v
        comissao_prev = total * 0.40 if "Irmão" in quem else 0.0
        fundo_prev = total * 0.10
        lucro_prev = total - comissao_prev - fundo_prev
        st.markdown(f"""<div style='background:#111;padding:15px;border-radius:10px;border:1px solid #333'><h4><i class="bi bi-tag-fill"></i> Orçamento: {formatar_moeda(total)}</h4><small>Fundo (10%): {formatar_moeda(fundo_prev)} | Comissão: {formatar_moeda(comissao_prev)}</small><p style='color:#39FF14; margin:5px 0 0 0; font-weight:bold'>Lucro Líquido Previsto: {formatar_moeda(lucro_prev)}</p></div>""", unsafe_allow_html=True)
        if st.button("CONFIRMAR AGENDAMENTO", use_container_width=True):
            if cli and veic and (escolhidos or extra_v > 0):
                servicos_finais = ", ".join(escolhidos)
                if extra_n: servicos_finais += f" (+ {extra_n})"
                dados = {"Data": dt.strftime("%d/%m/%Y"), "Hora": hr, "Cliente": cli, "Veiculo": veic, "Placa": placa, "Servicos": servicos_finais, "Total": total, "Executor": quem, "LucroPrevisto": lucro_prev, "Categoria": cat}
                if salvar_no_google("Agendamentos", dados): st.success("Agendado com sucesso!"); st.balloons()
                else: st.error("ERRO AO CONECTAR: Verifique se criou a coluna 'Categoria' na aba Agendamentos.")
            else: st.error("Preencha o cliente e pelo menos um serviço!")
    with tab_list:
        df_a = carregar_dados("Agendamentos")
        if df_a.empty: st.info("Sua agenda está vazia.")
        else:
            for i, r in df_a.iterrows():
                with st.container():
                    total_val = float(r["Total"])
                    cat_atual = r.get("Categoria", "")
                    icone_veiculo = obter_icone_veiculo(cat_atual)
                    st.markdown(f"""
                    <div class="agenda-card">
                        <div style="margin-bottom:8px; font-weight:bold; color:#00B4DB"><i class="bi bi-calendar4-week"></i> {r["Data"]} &nbsp;|&nbsp; <i class="bi bi-clock"></i> {r["Hora"]}</div>
                        <div style="font-size:18px; font-weight:bold; margin-bottom:5px">{icone_veiculo} {r["Veiculo"]}</div>
                        <div style="color:#aaa; font-size:14px; margin-bottom:5px"><i class="bi bi-person-fill"></i> {r["Cliente"]}</div>
                        <div style="font-size:13px; color:#ddd; margin-bottom:10px"><i class="bi bi-tools"></i> {r["Servicos"]}</div>
                        <div style="font-size:20px; font-weight:bold; color:#39FF14">{formatar_moeda(total_val)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(f"CONCLUIR SERVIÇO", key=f"efet_{i}"):
                            fundo_caixa = total_val * 0.10
                            comissao = total_val * 0.40 if "Irmão" in r["Executor"] else 0.0
                            lucro_liq = total_val - fundo_caixa - comissao
                            nova_venda = {
                                "Data": r["Data"], "Cliente": r["Cliente"], "Carro": r["Veiculo"], "Placa": r["Placa"], "Serviços": r["Servicos"], 
                                "Total": total_val, "Status": "Concluído", "Pagamento": "-", "Funcionario": r["Executor"], 
                                "Valor Comissao": comissao, "Fundo Caixa": fundo_caixa, "Lucro Liquido": lucro_liq, "Agendamentos": "",
                                "Status Comissao": "Pendente", "Categoria": r.get("Categoria", "")
                            }
                            if salvar_no_google("Vendas", nova_venda):
                                if excluir_agendamento(i): st.success("Serviço Concluído!"); t_sleep.sleep(1.5); st.rerun()
                                else: st.warning("Salvo em Vendas, mas erro ao limpar da Agenda.")
                            else: st.error("ERRO: Verifique se criou a coluna 'Categoria' na aba Vendas.")
                    with c2:
                        precos_pdf = {r["Servicos"]: total_val}
                        pdf_bytes = gerar_pdf(r["Cliente"], r["Veiculo"], r["Placa"], r["Data"], precos_pdf, total_val)
                        st.download_button("BAIXAR ORÇAMENTO (PDF)", data=pdf_bytes, file_name=f"Orcamento_{r['Cliente']}.pdf", mime="application/pdf", key=f"pdf_{i}")

def page_despesas():
    st.markdown('<h1 class="custom-title"><i class="bi bi-receipt" style="color: #D90429;"></i> Despesas Externas</h1>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1]); desc = c1.text_input("Descrição"); val = c2.number_input("Valor", min_value=0.0)
    if st.button("LANÇAR DESPESA"):
        if salvar_no_google("Despesas", {"Data": datetime.now().strftime("%d/%m/%Y"), "Descricao": desc, "Valor": val}): st.success("Salvo!")
        else: st.error("Erro ao conectar na planilha.")

def page_historico():
    st.markdown('<h1 class="custom-title"><i class="bi bi-clock-history" style="color: #FFC107;"></i> Garagem & Histórico</h1>', unsafe_allow_html=True)
    df = carregar_dados("Vendas")
    if df.empty: st.info("Sem registros."); return
    busca = st.text_input("Buscar...").strip().lower(); df_f = df.iloc[::-1]
    if busca: df_f = df_f[df_f.apply(lambda r: busca in str(r).lower(), axis=1)]
    for _, r in df_f.iterrows():
        cor = "#28a745" if r['Status'] == "Concluído" else "#ffc107"
        total_formatado = formatar_moeda(float(r["Total"]))
        cat_atual = r.get("Categoria", "")
        icone_veiculo = obter_icone_veiculo(cat_atual)
        st.markdown(f"""
        <div class="history-card" style="border-left-color: {cor}">
            <div style="display: flex; justify-content: space-between">
                <div>
                    <h3 style="margin:0">{icone_veiculo} {r["Carro"]}</h3>
                    <p style="margin:5px 0; color:#aaa"><i class="bi bi-person"></i> {r["Cliente"]} &nbsp;•&nbsp; <i class="bi bi-calendar"></i> {r["Data"]}</p>
                    <small style="color:#666"><i class="bi bi-tools"></i> {r["Serviços"]}</small>
                </div>
                <div style="text-align: right">
                    <h2 style="color: #38ef7d; margin:0">{total_formatado}</h2>
                    <span style="font-size:12px; text-transform:uppercase; letter-spacing:1px; background:#222; padding:3px 8px; border-radius:4px">{r["Status"]}</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

# --- MENU ---
with st.sidebar:
    if os.path.exists("logo_sidebar.png"): st.image("logo_sidebar.png", use_container_width=True)
    elif os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    menu = st.radio("NAVEGAÇÃO", ["DASHBOARD", "AGENDAMENTO", "FINANCEIRO", "DESPESAS", "HISTÓRICO"], label_visibility="collapsed")
    st.write("---")
    df_meta = carregar_dados("Vendas")
    if not df_meta.empty:
        for c in ["Total"]:
            df_meta[c] = pd.to_numeric(df_meta[c].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0)
        total_vendido = df_meta[df_meta["Status"]=="Concluído"]["Total"].sum()
        META_MENSAL = 5000.00
        progresso = min(total_vendido / META_MENSAL, 1.0)
        st.markdown(f"""<div style="background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; margin-bottom: 5px;"><p style="margin: 0; font-size: 14px; color: #aaa; text-transform: uppercase; letter-spacing: 1px;"><i class="bi bi-crosshair" style="color:#D90429"></i> Meta do Mês</p><p style="margin: 5px 0 0 0; font-size: 22px; font-weight: bold; color: #FFF;">{formatar_moeda(total_vendido)} <span style="font-size:14px; color:#666; font-weight:normal;">/ {formatar_moeda(META_MENSAL)}</span></p></div>""", unsafe_allow_html=True)
        st.progress(progresso)
    st.markdown("<div style='text-align: center; color: #444; font-size: 11px; margin-top: 30px;'>v6.42 Maxton Graphics • Jairan Jesus Matos</div>", unsafe_allow_html=True)

if menu == "DASHBOARD": page_dashboard()
elif menu == "AGENDAMENTO": page_agendamento()
elif menu == "FINANCEIRO": page_financeiro()
elif menu == "DESPESAS": page_despesas()
elif menu == "HISTÓRICO": page_historico()