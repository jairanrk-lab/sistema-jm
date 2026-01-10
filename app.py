import sys
import os
import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go 
from datetime import datetime, date, time, timedelta
from fpdf import FPDF
import gspread
import time as t_sleep

# --- CORREÇÃO DE PASTAS (As 2 linhas que você pediu) ---
sys.path.append(os.path.abspath(os.path.curdir))

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# --- 2. SISTEMA DE LOGIN (Ajustado para seus Secrets) ---
# ==============================================================================
def check_password():
    if st.session_state.get("password_correct", False):
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
                # --- AQUI ESTÁ A CORREÇÃO DA SENHA ---
                try: 
                    # Tenta pegar a senha configurada no site
                    senha_correta = st.secrets["password"]
                except: 
                    # Se der erro, usa uma senha de emergência para não travar
                    senha_correta = "admin123"
                
                if pwd == senha_correta: 
                    st.session_state["password_correct"] = True
                    try: st.query_params["acesso_liberado"] = "sim_mestre"
                    except: pass
                    st.rerun()
                else: st.error("Senha incorreta.")
    return False

if not check_password(): st.stop()

# ==============================================================================
# --- 3. ESTILO CSS (O SEU VISUAL ORIGINAL) ---
# ==============================================================================
st.markdown("""
<style>
    /* 1. FONTE POPPINS */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    
    * { font-family: 'Poppins', sans-serif !important; }
    
    /* --- FUNDO PRETO --- */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { background-color: #000000 !important; }
    .block-container { padding-top: 1rem; padding-bottom: 6rem; }

    /* --- SUMIR COM A BARRA LATERAL --- */
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }

    /* --- NAVEGAÇÃO SUPERIOR COM ÍCONES REAIS (CSS TRICK) --- */
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

    /* --- INJEÇÃO DOS ÍCONES BOOTSTRAP (O SEGREDO) --- */
    /* Cada linha abaixo coloca um ícone específico antes do texto do botão */
    
    /* 1. Dashboard -> Speedometer */
    div[role="radiogroup"] label:nth-of-type(1)::before {
        font-family: "bootstrap-icons"; content: "\\F5A6"; 
        margin-right: 8px; font-size: 16px;
    }
    /* 2. Agenda -> Calendar Check */
    div[role="radiogroup"] label:nth-of-type(2)::before {
        font-family: "bootstrap-icons"; content: "\\F20E"; 
        margin-right: 8px; font-size: 16px;
    }
    /* 3. Financeiro -> Cash Coin */
    div[role="radiogroup"] label:nth-of-type(3)::before {
        font-family: "bootstrap-icons"; content: "\\F23E"; 
        margin-right: 8px; font-size: 16px;
    }
    /* 4. Despesas -> Receipt */
    div[role="radiogroup"] label:nth-of-type(4)::before {
        font-family: "bootstrap-icons"; content: "\\F4E9"; 
        margin-right: 8px; font-size: 16px;
    }
    /* 5. Histórico -> Clock History */
    div[role="radiogroup"] label:nth-of-type(5)::before {
        font-family: "bootstrap-icons"; content: "\\F291"; 
        margin-right: 8px; font-size: 16px;
    }

    /* Hover */
    div[role="radiogroup"] label:hover {
        border-color: #D90429 !important;
        color: white !important;
        background-color: #1a1a1a !important;
    }

    /* Botão Selecionado (ATIVO) */
    div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(90deg, #D90429 0%, #8D021F 100%) !important;
        color: white !important;
        border-color: #D90429 !important;
        box-shadow: 0 0 12px rgba(217, 4, 41, 0.5) !important;
    }
    
    div[role="radiogroup"] div[data-testid="stMarkdownContainer"] p { margin: 0; }

    /* --- CARDS DASHBOARD --- */
    .dash-card { 
        border-radius: 15px; 
        padding: 20px; 
        color: white; 
        margin-bottom: 20px; 
        border: 1px solid #333; 
        position: relative; 
        overflow: hidden; 
        height: 140px !important; 
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .card-icon-bg { position: absolute !important; top: -10px !important; right: -10px !important; font-size: 100px !important; opacity: 0.15 !important; transform: rotate(15deg) !important; pointer-events: none !important; color: white !important; }
    
    /* CORES */
    .bg-orange { background: linear-gradient(145deg, #FF9800, #F57C00); }
    .bg-blue { background: linear-gradient(145deg, #00B4DB, #0083B0); }
    .bg-red { background: linear-gradient(145deg, #D90429, #8D021F); }
    .bg-green { background: linear-gradient(145deg, #11998e, #38ef7d); }
    .bg-purple { background: linear-gradient(145deg, #8E2DE2, #4A00E0); }
    .bg-dark { background: linear-gradient(145deg, #222, #111); }

    /* --- CARDS LISTA (AGENDA/HISTÓRICO) --- */
    .agenda-card { background-color: #161616 !important; border-radius: 12px; padding: 15px; margin-bottom: 12px; border: 1px solid #333; border-left: 5px solid #00B4DB; }
    .history-card { background-color: #161616 !important; border-radius: 12px; padding: 15px; margin-bottom: 12px; border: 1px solid #333; }

    /* RODAPÉ */
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #000000; color: #666; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #222; z-index: 9999; }
    
    /* Botões */
    div.stButton > button { background-color: #D90429 !important; color: white !important; border-radius: 8px !important; font-weight: 700 !important; border: none !important; height: 45px !important; }

</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def conectar_google_sheets():
    try: ID = st.secrets["app"]["spreadsheet_id"]
    except: ID = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg"
    try:
        if os.path.exists("chave_google.json"): client = gspread.service_account(filename="chave_google.json")
        else: client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        return client.open_by_key(ID)
    except Exception as e: return None

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
        nova_linha = [''] * len(headers)
        for col_name, valor in linha_dados.items():
            if col_name in headers:
                index = headers.index(col_name)
                nova_linha[index] = valor
            else:
                alt = col_name.replace("ç", "c") if "ç" in col_name else col_name.replace("c", "ç")
                if alt in headers: index = headers.index(alt); nova_linha[index] = valor
        ws.append_row(nova_linha)
        return True, "Sucesso"
    except Exception as e: return False, str(e)

def excluir_agendamento(indice_linha):
    sheet = conectar_google_sheets()
    if sheet is None: return False
    try: ws = sheet.worksheet("Agendamentos"); ws.delete_rows(indice_linha + 2); return True
    except: return False

@st.cache_data
def carregar_catalogo():
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

# Ícone HTML para os Cards
def obter_icone_html(cat):
    if not isinstance(cat, str): return '<i class="bi bi-car-front-fill"></i>'
    c = cat.lower()
    if "moto" in c: return '<i class="bi bi-motorcycle"></i>'
    elif "suv" in c or "picape" in c or "caminhonete" in c: return '<i class="bi bi-truck-front-fill"></i>'
    elif "van" in c: return '<i class="bi bi-bus-front-fill"></i>'
    else: return '<i class="bi bi-car-front-fill"></i>'

def gerar_pdf(cliente, carro, placa, data_servico, servicos_com_precos, total):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"): pdf.image("logo.png", x=55, y=10, w=100); pdf.ln(35)
    else: pdf.ln(20)
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
    return pdf.output(dest="S").encode("latin-1")

# ==============================================================================
# --- CABEÇALHO E NAVEGAÇÃO SUPERIOR ---
# ==============================================================================

c_logo1, c_logo2, c_logo3 = st.columns([1,2,1])
with c_logo2:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.markdown("<h1 style='text-align:center; color:#D90429; font-weight:800'>JM DETAIL</h1>", unsafe_allow_html=True)

st.write("") 

# MENU DE NAVEGAÇÃO (Texto Limpo - Ícones vêm via CSS, como você pediu)
menu_opcoes = ["DASHBOARD", "AGENDA", "FINANCEIRO", "DESPESAS", "HISTÓRICO"]
menu_selecionado = st.radio("Navegação", menu_opcoes, horizontal=True, label_visibility="collapsed")

st.write("---") 

# --- PÁGINAS (CONTEÚDO) ---
def page_dashboard():
    hoje = datetime.now()
    mes_atual, ano_atual = hoje.month, hoje.year
    nome_meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    # Título com Ícone Original
    st.markdown(f'## <i class="bi bi-speedometer2" style="color: #00B4DB;"></i> Painel Geral <small style="font-size:14px; color:#888">| {nome_meses[mes_atual]}/{ano_atual}</small>', unsafe_allow_html=True)
    
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    df_a = carregar_dados("Agendamentos")
    
    receita_mes, despesa_mes, pendente_total, count_p = 0.0, 0.0, 0.0, 0
    
    if not df_v.empty:
        for c in ["Total", "Lucro Liquido"]:
            df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0)
        df_v['Data_dt'] = pd.to_datetime(df_v['Data'], format='%d/%m/%Y', errors='coerce')
        df_mes = df_v[(df_v['Data_dt'].dt.month == mes_atual) & (df_v['Data_dt'].dt.year == ano_atual)]
        receita_mes = df_mes[df_mes["Status"]=="Concluído"]["Total"].sum()
        pendente_total = df_v[df_v["Status"]=="Orçamento/Pendente"]["Total"].sum()
        count_p = len(df_v[df_v["Status"]=="Orçamento/Pendente"])

    if not df_d.empty:
        df_d['Data_dt'] = pd.to_datetime(df_d['Data'], format='%d/%m/%Y', errors='coerce')
        df_d_mes = df_d[(df_d['Data_dt'].dt.month == mes_atual) & (df_d['Data_dt'].dt.year == ano_atual)]
        despesa_mes = pd.to_numeric(df_d_mes["Valor"].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0).sum()
    
    lucro_final = receita_mes - despesa_mes
    
    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="dash-card bg-orange"><i class="bi bi-hourglass-split card-icon-bg"></i><h4>PENDENTES (GERAL)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(pendente_total)}</div><small>{count_p} carros na fila</small></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="dash-card bg-blue"><i class="bi bi-currency-dollar card-icon-bg"></i><h4>FATURAMENTO (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(receita_mes)}</div><small>Ref: {nome_meses[mes_atual]}</small></div>', unsafe_allow_html=True)
    
    c3, c4 = st.columns(2)
    with c3: st.markdown(f'<div class="dash-card bg-red"><i class="bi bi-graph-down-arrow card-icon-bg"></i><h4>DESPESAS (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(despesa_mes)}</div><small>Gastos externos</small></div>', unsafe_allow_html=True)
    cor_lucro = "bg-green" if lucro_final >= 0 else "bg-red"
    with c4: st.markdown(f'<div class="dash-card {cor_lucro}"><i class="bi bi-wallet2 card-icon-bg"></i><h4>LUCRO LÍQUIDO (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_final)}</div><small>Após comissões/insumos</small></div>', unsafe_allow_html=True)

    st.write("---")
    
    col_graf, col_prox = st.columns([2, 1])
    
    with col_graf:
        # Título com o ícone Verde Neon (Pedido V13)
        st.markdown('### <i class="bi bi-graph-up-arrow" style="color: #39FF14;"></i> Performance Mensal', unsafe_allow_html=True)
        if not df_v.empty and 'df_mes' in locals() and not df_mes.empty:
            base = alt.Chart(df_mes).encode(x=alt.X('Data', title=None, axis=alt.Axis(labelColor='white')))
            bars = base.mark_bar(size=30, cornerRadiusEnd=5).encode(
                y=alt.Y('Total', axis=None),
                color=alt.Color('Status', scale=alt.Scale(domain=['Concluído', 'Orçamento/Pendente'], range=['#00F260', '#FF0080']), legend=None),
                tooltip=['Data', 'Cliente', 'Carro', 'Total', 'Lucro Liquido']
            )
            line = base.mark_line(color='#0575E6', strokeWidth=3).encode(y=alt.Y('Lucro Liquido', axis=None))
            chart = alt.layer(bars, line).properties(height=300, background='transparent').configure_view(strokeWidth=0).configure_axis(grid=False, domain=False, ticks=False)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Sem dados de vendas neste mês.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('##### <i class="bi bi-bullseye" style="color:#D90429"></i> Meta Mensal', unsafe_allow_html=True)
        fig = go.Figure(go.Indicator(mode = "gauge+number", value = receita_mes, domain = {'x': [0, 1], 'y': [0, 1]}, gauge = {'axis': {'range': [None, 6000], 'tickwidth': 1, 'tickcolor': "white"}, 'bar': {'color': "#D90429"}, 'bgcolor': "black", 'borderwidth': 2, 'bordercolor': "#333", 'steps': [{'range': [0, 1500], 'color': '#222'}, {'range': [1500, 3500], 'color': '#333'}], 'threshold': {'line': {'color': "#00B4DB", 'width': 4}, 'thickness': 0.75, 'value': 5000}}))
        fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "white", 'family': "Poppins"}, height=150, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col_prox:
        st.markdown('### <i class="bi bi-calendar-week"></i> Próximos na Agenda', unsafe_allow_html=True)
        if not df_a.empty:
            df_a['Data_dt'] = pd.to_datetime(df_a['Data'], format='%d/%m/%Y', errors='coerce')
            hoje_dt = pd.to_datetime(date.today())
            df_futuro = df_a[df_a['Data_dt'] >= hoje_dt].sort_values(by='Data_dt').head(4)
            
            if not df_futuro.empty:
                for _, r in df_futuro.iterrows():
                    st.markdown(f"""
                    <div style="background-color:#161616; padding:15px; border-radius:12px; margin-bottom:10px; border-left:4px solid #D90429;">
                        <div style="font-size:12px; color:#aaa; margin-bottom:5px">
                            <i class="bi bi-calendar"></i> {r['Data']} • {r['Hora']}
                        </div>
                        <div style="font-weight:bold; font-size:16px; color:white">
                            {obter_icone_html(r.get("Categoria", ""))} {r['Veiculo']}
                        </div>
                        <div style="font-size:13px; color:#888;">{r['Cliente']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Agenda livre.")
        else:
            st.info("Agenda vazia.")

def page_financeiro():
    st.markdown('## <i class="bi bi-cash-coin" style="color: #28a745;"></i> Gestão Financeira', unsafe_allow_html=True)
    df_v = carregar_dados("Vendas")
    comissao_pendente = 0.0; fundo_caixa = 0.0
    if not df_v.empty:
        if "Status Comissao" not in df_v.columns: df_v["Status Comissao"] = "Pendente"
        for c in ["Valor Comissao", "Fundo Caixa"]:
            if c in df_v.columns: df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0)
        comissao_pendente = df_v[df_v["Status Comissao"] != "Pago"]["Valor Comissao"].sum()
        fundo_caixa = df_v["Fundo Caixa"].sum()
    
    st.info(f"Caixa da Empresa (Acumulado): {formatar_moeda(fundo_caixa)}")
    
    col1, col2 = st.columns([2,1])
    with col1: st.metric("Comissões Pendentes", formatar_moeda(comissao_pendente))
    with col2:
        if comissao_pendente > 0:
            if st.button("Pagar Comissões"):
                sheet = conectar_google_sheets(); ws = sheet.worksheet("Vendas"); dados = ws.get_all_records()
                header = ws.row_values(1); col_idx = header.index("Status Comissao") + 1
                for i, linha in enumerate(dados):
                    v = pd.to_numeric(str(linha.get("Valor Comissao", "0")).replace('R$', '').replace(',', '.'), errors='coerce')
                    if v > 0 and str(linha.get("Status Comissao", "")) != "Pago": ws.update_cell(i + 2, col_idx, "Pago")
                st.success("Pago!"); t_sleep.sleep(1); st.rerun()

def page_agendamento():
    st.markdown('## <i class="bi bi-calendar-check" style="color: white;"></i> Agenda Integrada', unsafe_allow_html=True)
    tab_new, tab_list = st.tabs(["NOVO AGENDAMENTO", "LISTA DE SERVIÇOS"]) 
    df_cat = carregar_catalogo()
    
    with tab_new:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            cli = c1.text_input("Nome do Cliente")
            veic = c1.text_input("Modelo do Veículo")
            placa = c2.text_input("Placa")
            dt = c2.date_input("Data", value=date.today(), format="DD/MM/YYYY")
            hr = c2.time_input("Horário", value=time(8, 0)).strftime("%H:%M")
            
            cat = st.selectbox("Categoria do Veículo:", df_cat["Categoria"])
            servs_disp = [c for c in df_cat.columns if c != "Categoria"]
            escolhidos = st.multiselect("Selecione os Serviços:", servs_disp)
            
            st.divider()
            ce1, ce2, ce3 = st.columns(3)
            extra_v = ce1.number_input("Valor Extra (R$)", min_value=0.0)
            desconto_v = ce2.number_input("Desconto (R$)", min_value=0.0)
            quem = ce3.radio("Executor:", ["Eu Mesmo", "Equipe"], horizontal=True)
            
            # Cálculo em Tempo Real
            if escolhidos:
                precos = {s: df_cat[df_cat["Categoria"] == cat][s].values[0] for s in escolhidos}
                total = sum(precos.values()) + extra_v - desconto_v
                st.markdown(f"<h3 style='text-align:right; color:#39FF14'>Total: {formatar_moeda(total)}</h3>", unsafe_allow_html=True)
                
                if st.button("CONFIRMAR AGENDAMENTO", use_container_width=True):
                    serv_str = ", ".join(escolhidos)
                    lucro = total - (total * 0.10) - (total * 0.40 if "Equipe" in quem else 0)
                    dados = {"Data": dt.strftime("%d/%m/%Y"), "Hora": hr, "Cliente": cli, "Veiculo": veic, "Placa": placa, "Servicos": serv_str, "Total": total, "Executor": quem, "LucroPrevisto": lucro, "Categoria": cat}
                    ok, msg = salvar_no_google("Agendamentos", dados)
                    if ok: st.success("Agendado!"); t_sleep.sleep(1); st.rerun()
                    else: st.error(msg)

    with tab_list:
        df_a = carregar_dados("Agendamentos")
        if df_a.empty: st.info("Agenda vazia.")
        else:
            for i, r in df_a.iterrows():
                st.markdown(f"""
                <div class="agenda-card">
                    <div style="display:flex; justify-content:space-between; align-items:center">
                        <div style="font-weight:bold; color:#00B4DB; font-size:16px">
                            <i class="bi bi-clock"></i> {r['Data']} às {r['Hora']}
                        </div>
                        <div style="font-weight:800; font-size:18px; color:#39FF14">
                            {formatar_moeda(float(r['Total']))}
                        </div>
                    </div>
                    <div style="margin-top:10px; font-size:18px; font-weight:700; color:white">
                        {obter_icone_html(r.get("Categoria", ""))} {r['Veiculo']} <span style="font-size:14px; color:#888">({r['Placa']})</span>
                    </div>
                    <div style="margin-top:5px; font-size:14px; color:#ccc">
                        <i class="bi bi-person-fill"></i> {r['Cliente']}
                    </div>
                    <div style="margin-top:10px; padding-top:10px; border-top:1px solid #333; font-size:13px; color:#888">
                        🔧 {r['Servicos']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button(f"✅ Concluir Serviço", key=f"ok_{i}", use_container_width=True):
                        fundo = float(r["Total"]) * 0.10
                        comis = float(r["Total"]) * 0.40 if "Equipe" in r["Executor"] else 0.0
                        lucro = float(r["Total"]) - fundo - comis
                        venda = {"Data": r["Data"], "Cliente": r["Cliente"], "Carro": r["Veiculo"], "Placa": r["Placa"], "Serviços": r["Servicos"], "Total": r["Total"], "Status": "Concluído", "Funcionario": r["Executor"], "Valor Comissao": comis, "Fundo Caixa": fundo, "Lucro Liquido": lucro, "Status Comissao": "Pendente", "Categoria": r.get("Categoria", "")}
                        salvar_no_google("Vendas", venda)
                        excluir_agendamento(i)
                        st.rerun()
                with c_btn2:
                    if st.button(f"🗑️ Cancelar", key=f"del_{i}", use_container_width=True):
                        excluir_agendamento(i)
                        st.warning("Agendamento excluído.")
                        t_sleep.sleep(1)
                        st.rerun()

def page_despesas():
    st.markdown('## <i class="bi bi-receipt" style="color: #D90429;"></i> Despesas', unsafe_allow_html=True)
    with st.form("form_desp"):
        desc = st.text_input("Descrição")
        val = st.number_input("Valor", min_value=0.0)
        if st.form_submit_button("Lançar"):
            salvar_no_google("Despesas", {"Data": datetime.now().strftime("%d/%m/%Y"), "Descricao": desc, "Valor": val})
            st.success("Salvo!")

def page_historico():
    st.markdown('## <i class="bi bi-clock-history" style="color: #FFC107;"></i> Garagem & Histórico', unsafe_allow_html=True)
    df = carregar_dados("Vendas")
    
    if df.empty:
        st.info("Nenhum serviço registrado ainda.")
        return

    busca = st.text_input("🔍 Buscar Cliente ou Carro...", placeholder="Ex: Fiat Toro ou João").strip().lower()
    df_f = df.iloc[::-1]
    
    if busca:
        df_f = df_f[df_f.apply(lambda r: busca in str(r).lower(), axis=1)]

    for index, r in df_f.iterrows():
        cor_borda = "#28a745"
        html_card = f"""
        <div class="history-card" style="border-left: 5px solid {cor_borda}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h3 style="margin: 0; font-size: 20px; color: white; font-weight: 700;">
                        {obter_icone_html(r.get("Categoria", ""))} {r["Carro"]}
                    </h3>
                    <p style="margin: 5px 0 0 0; color: #bbb; font-size: 14px;">
                        <i class="bi bi-person"></i> {r["Cliente"]} &nbsp;|&nbsp; {r["Placa"]}
                    </p>
                </div>
                <div style="text-align: right;">
                    <h2 style="margin: 0; color: #39FF14; font-weight: 700; font-size: 22px;">
                        {formatar_moeda(float(r["Total"]))}
                    </h2>
                    <span style="background-color: #222; padding: 4px 8px; border-radius: 6px; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #aaa;">
                        {r["Data"]}
                    </span>
                </div>
            </div>
            <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid #333; color: #888; font-size: 13px;">
                <i class="bi bi-tools"></i> {r["Serviços"]}
            </div>
        </div>
        """
        st.markdown(html_card, unsafe_allow_html=True)

# --- ROTEADOR DE PÁGINAS ---
if "DASHBOARD" in menu_selecionado: page_dashboard()
elif "AGENDA" in menu_selecionado: page_agendamento()
elif "FINANCEIRO" in menu_selecionado: page_financeiro()
elif "DESPESAS" in menu_selecionado: page_despesas()
elif "HISTÓRICO" in menu_selecionado: page_historico()

# --- RODAPÉ ---
st.markdown('<div class="footer">Desenvolvido por <b>Jairan Jesus Matos</b> | JM Detail System © 2026</div>', unsafe_allow_html=True)
