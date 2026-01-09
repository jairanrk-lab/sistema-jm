import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go 
from datetime import datetime, date, time, timedelta
from fpdf import FPDF
import gspread
import os
import time as t_sleep

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide", initial_sidebar_state="expanded")

# ==============================================================================
# --- 2. SISTEMA DE LOGIN ---
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
                try: senha_correta = st.secrets["app"]["password"]
                except: senha_correta = "1234"
                if pwd == senha_correta: 
                    st.session_state["password_correct"] = True
                    try: st.query_params["acesso_liberado"] = "sim_mestre"
                    except: pass
                    st.rerun()
                else: st.error("Senha incorreta.")
    return False

if not check_password(): st.stop()

# ==============================================================================
# --- 3. ESTILO CSS (V10.16 - CORREÇÃO AGRESSIVA DO BOTÃO DE ABRIR) ---
# ==============================================================================
st.markdown("""
<style>
    /* 1. FONTES */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    
    * { font-family: 'Montserrat', sans-serif !important; }
    
    /* --- FUNDO PRETO --- */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { background-color: #000000 !important; }
    .block-container { padding-bottom: 6rem; }

    /* --- 2. VACINA NUCLEAR PRO TEXTO TEIMOSO --- */
    
    /* PARTE 1: O BOTÃO DE ABRIR (Main Screen) - Onde aparece 'keyboard...' */
    [data-testid="stSidebarCollapsedControl"] {
        color: transparent !important;
        font-size: 0px !important; /* Mata o texto no container */
    }
    
    [data-testid="stSidebarCollapsedControl"] button {
        color: transparent !important;
        font-size: 0px !important; /* Mata o texto no botão */
        background: transparent !important;
        border: none !important;
        width: 50px !important;
        height: 50px !important;
    }

    /* Garante que qualquer SPAN ou DIV filho (o texto) desapareça */
    [data-testid="stSidebarCollapsedControl"] button > * {
        display: none !important;
    }

    /* Cria o ÍCONE DE MENU (☰) no lugar */
    [data-testid="stSidebarCollapsedControl"] button::after {
        content: "☰"; 
        font-size: 35px !important; /* Restaura o tamanho só pro nosso ícone */
        color: #D90429 !important; /* Vermelho JM */
        font-weight: 800 !important;
        display: block !important;
        position: absolute !important;
        top: 5px !important;
        left: 5px !important;
    }

    /* PARTE 2: O BOTÃO DE FECHAR (Dentro do Menu) - Onde aparece o X */
    [data-testid="stSidebarHeader"] button {
        color: transparent !important;
        font-size: 0px !important;
    }
    [data-testid="stSidebarHeader"] button > * { display: none !important; }
    
    [data-testid="stSidebarHeader"] button::after {
        content: "✖"; 
        font-size: 28px !important;
        color: #666 !important; 
        font-weight: bold !important;
        display: block !important;
    }
    [data-testid="stSidebarHeader"] button:hover::after { color: #D90429 !important; }

    /* --- SIDEBAR RESPONSIVA --- */
    @media (min-width: 992px) { 
        [data-testid="stSidebar"] { min-width: 300px !important; max-width: 350px !important; } 
    }
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            min-width: 220px !important;
            max-width: 85% !important;
        }
    }

    /* --- ESTILO DOS BOTÕES DO MENU LATERAL --- */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 15px 10px !important; background-color: #111111 !important; border: 1px solid #333 !important;
        color: #ddd !important; border-radius: 10px !important; margin-bottom: 10px !important; width: 100% !important;
        display: flex !important; align-items: center !important; justify-content: flex-start !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover { border-color: #D90429 !important; background-color: #1a1a1a !important; color: white !important; transform: scale(1.02); }
    [data-testid="stSidebar"] div[role="radiogroup"] [aria-checked="true"] { background: linear-gradient(90deg, #D90429 0%, #8D021F 100%) !important; color: white !important; border-color: #D90429 !important; }
    
    /* --- 3. CORREÇÃO DAS CAIXINHAS --- */
    .dash-card { 
        border-radius: 15px; 
        padding: 25px; 
        color: white; 
        margin-bottom: 20px; 
        border: 1px solid #333; 
        position: relative; 
        overflow: hidden; 
        height: 160px !important; 
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .card-icon-bg { position: absolute !important; top: -10px !important; right: -10px !important; font-size: 110px !important; opacity: 0.15 !important; transform: rotate(15deg) !important; pointer-events: none !important; color: white !important; }
    
    .agenda-card { background-color: #161616 !important; border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 6px solid #00B4DB; }
    .history-card { background-color: #161616 !important; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    
    /* CORES */
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
    except Exception as e:
        print(f"ERRO CONEXÃO GOOGLE: {e}")
        return None

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
    # Atualizado: Higi. Bancos SUV (Fiat Toro) ajustado para R$ 80,00 e Moto R$ 80
    return pd.DataFrame({
        "Categoria": ["Hatch/Compacto", "Sedã", "SUV/Caminhonete", "Picapes Grandes", "Vans/Utilitários", "Motocicleta"],
        "Lavagem Simples": [40.0, 50.0, 60.0, 70.0, 80.0, 30.0],
        "Lavagem Técnica": [150.0, 170.0, 190.0, 210.0, 230.0, 100.0],
        "Higi. Bancos": [80.0, 80.0, 80.0, 120.0, 150.0, 0.0], 
        "Higi. Interna (Teto/Carpete)": [150.0, 150.0, 180.0, 200.0, 250.0, 0.0],
        "Combo Premium (Téc+Higi+Ozônio)": [300.0, 320.0, 350.0, 400.0, 450.0, 0.0],
        "Limpeza Técnica Motor": [100.0, 100.0, 120.0, 150.0, 150.0, 80.0],
        "Restauração Faróis": [200.0, 200.0, 200.0, 200.0, 200.0, 100.0],
        "Cristalização Vidros": [90.0, 120.0, 150.0, 150.0, 150.0, 50.0],
        "Vitrificação Pintura": [800.0, 900.0, 1100.0, 1300.0, 1300.0, 500.0]
    })

def obter_icone_veiculo(cat):
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

# --- PÁGINAS ---
def page_dashboard():
    # Identificar Mês Atual para filtrar
    hoje = datetime.now()
    mes_atual = hoje.month
    ano_atual = hoje.year
    nome_meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    st.markdown(f'<h1 class="custom-title"><i class="bi bi-speedometer2" style="color: #00B4DB;"></i> PAINEL GERAL <small style="font-size:16px; color:#888">| {nome_meses[mes_atual]} de {ano_atual}</small></h1>', unsafe_allow_html=True)
    
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    df_a = carregar_dados("Agendamentos")
    
    receita_mes, despesa_mes, lucro_vendas_mes = 0.0, 0.0, 0.0
    pendente_total, count_p = 0.0, 0
    
    # 1. Processar Vendas (Filtrar Mês Atual para Finanças / Tudo para Pendentes)
    if not df_v.empty:
        # Converter colunas numéricas
        for c in ["Total", "Lucro Liquido"]:
            df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0)
        
        # Converter Data para filtrar mês
        df_v['Data_dt'] = pd.to_datetime(df_v['Data'], format='%d/%m/%Y', errors='coerce')
        
        # Filtro Mês Atual (Apenas para Receita e Lucro)
        df_mes = df_v[(df_v['Data_dt'].dt.month == mes_atual) & (df_v['Data_dt'].dt.year == ano_atual)]
        receita_mes = df_mes[df_mes["Status"]=="Concluído"]["Total"].sum()
        lucro_vendas_mes = df_mes[df_mes["Status"]=="Concluído"]["Lucro Liquido"].sum()
        
        # Pendentes (Pega de TODOS os meses, pois ainda tem que fazer)
        pendente_total = df_v[df_v["Status"]=="Orçamento/Pendente"]["Total"].sum()
        count_p = len(df_v[df_v["Status"]=="Orçamento/Pendente"])

    # 2. Processar Despesas (Filtrar Mês Atual)
    if not df_d.empty:
        df_d['Data_dt'] = pd.to_datetime(df_d['Data'], format='%d/%m/%Y', errors='coerce')
        df_d_mes = df_d[(df_d['Data_dt'].dt.month == mes_atual) & (df_d['Data_dt'].dt.year == ano_atual)]
        despesa_mes = pd.to_numeric(df_d_mes["Valor"].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0).sum()
    
    lucro_final_mes = lucro_vendas_mes - despesa_mes
    cor_lucro = "bg-green" if lucro_final_mes >= 0 else "bg-red"
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="dash-card bg-orange"><i class="bi bi-hourglass-split card-icon-bg"></i><h4>PENDENTES (GERAL)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(pendente_total)}</div><small>{count_p} carros na fila</small></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="dash-card bg-blue"><i class="bi bi-currency-dollar card-icon-bg"></i><h4>FATURAMENTO (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(receita_mes)}</div><small>Ref: {nome_meses[mes_atual]}</small></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="dash-card bg-red"><i class="bi bi-graph-down-arrow card-icon-bg"></i><h4>DESPESAS (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(despesa_mes)}</div><small>Gastos externos</small></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="dash-card {cor_lucro}"><i class="bi bi-wallet2 card-icon-bg"></i><h4>LUCRO LÍQUIDO (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_final_mes)}</div><small>Após comissões/insumos</small></div>', unsafe_allow_html=True)
    
    st.write("---")
    col_g, col_a = st.columns([2, 1])
    with col_g:
        st.markdown('<h3><i class="bi bi-graph-up-arrow" style="color: #39FF14;"></i> Performance Mensal</h3>', unsafe_allow_html=True)
        if not df_v.empty and not df_mes.empty:
            base = alt.Chart(df_mes).encode(x=alt.X('Data', title=None, axis=alt.Axis(labelColor='white')))
            bars = base.mark_bar(size=40, cornerRadiusEnd=10).encode(y=alt.Y('Total', axis=None), color=alt.Color('Status', scale=alt.Scale(domain=['Concluído', 'Orçamento/Pendente'], range=['#00F260', '#FF0080']), legend=None), tooltip=['Data', 'Cliente', 'Carro', 'Total', 'Lucro Liquido'])
            line = base.mark_line(color='#0575E6', strokeWidth=4, interpolate='natural').encode(y=alt.Y('Lucro Liquido', axis=None), tooltip=['Data', 'Lucro Liquido'])
            chart = alt.layer(bars, line).properties(height=380, background='transparent').configure_view(strokeWidth=0).configure_axis(grid=False, domain=False, ticks=False)
            st.altair_chart(chart, use_container_width=True)
        else: st.info(f"Nenhuma venda registrada em {nome_meses[mes_atual]}.")
    with col_a:
        st.markdown('<h3><i class="bi bi-calendar-event" style="color: white;"></i> Próximos na Agenda</h3>', unsafe_allow_html=True)
        if df_a.empty: st.info("Agenda livre.")
        else:
            for _, r in df_a.tail(4).iloc[::-1].iterrows():
                icone_veiculo = obter_icone_veiculo(r.get("Categoria", ""))
                st.markdown(f"""<div class="agenda-card"><div style="margin-bottom:8px; font-weight:bold; color:#00B4DB"><i class="bi bi-calendar4-week"></i> {r["Data"]} &nbsp;|&nbsp; <i class="bi bi-clock"></i> {r["Hora"]}</div><div style="font-size:18px; font-weight:bold; margin-bottom:5px">{icone_veiculo} {r["Veiculo"]}</div><div style="color:#aaa; font-size:14px; margin-bottom:5px"><i class="bi bi-person-fill"></i> {r["Cliente"]}</div><div style="font-size:20px; font-weight:bold; color:#39FF14">{formatar_moeda(float(r["Total"]))}</div></div>""", unsafe_allow_html=True)

def page_financeiro():
    st.markdown('<h1 class="custom-title"><i class="bi bi-cash-coin" style="color: #28a745;"></i> Gestão Financeira</h1>', unsafe_allow_html=True)
    df_v = carregar_dados("Vendas")
    comissao_pendente = 0.0; fundo_caixa_acumulado = 0.0
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
            if st.button("CONFIRMAR PAGAMENTO", use_container_width=True):
                sheet = conectar_google_sheets(); ws = sheet.worksheet("Vendas"); dados_planilha = ws.get_all_records()
                try:
                    header = ws.row_values(1); col_idx = header.index("Status Comissao") + 1
                    for i, linha in enumerate(dados_planilha):
                        v_float = pd.to_numeric(str(linha.get("Valor Comissao", "0")).replace('R$', '').replace(',', '.'), errors='coerce')
                        if v_float > 0 and str(linha.get("Status Comissao", "")) != "Pago": ws.update_cell(i + 2, col_idx, "Pago")
                    st.success("Pagamento registrado!"); st.rerun()
                except: st.error("Erro na atualização.")
        else: st.info("Nenhuma comissão pendente no momento.")
    with c2: st.markdown(f"""<div class="dash-card bg-dark"><i class="bi bi-safe2-fill card-icon-bg"></i><h4>CAIXA EMPRESA (10%)</h4><div style="font-size:32px;font-weight:bold">{formatar_moeda(fundo_caixa_acumulado)}</div><p style="margin-top:10px; opacity:0.8">Acumulado total para insumos.</p></div>""", unsafe_allow_html=True)

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
        
        # Seleção de Serviços
        cat = c2.selectbox("Categoria:", df_cat["Categoria"])
        servs_disp = [c for c in df_cat.columns if c != "Categoria"]
        escolhidos = st.multiselect("Serviços:", servs_disp, placeholder="Escolha os serviços...")
        
        st.write("---")
        # Área Financeira (Extras e Descontos)
        ce1, ce2 = st.columns(2)
        extra_n = ce1.text_input("Serviço Extra (Nome)")
        extra_v = ce2.number_input("Valor Extra (+ R$)", min_value=0.0)
        
        # NOVO: Campo de Desconto
        desconto_v = ce2.number_input("Desconto (- R$)", min_value=0.0, step=5.0, help="Use com sabedoria! Desconto sai do seu lucro.")
        
        quem = st.radio("Quem vai executar?", ["Eu Mesmo", "Irmão/Equipe"], horizontal=True)
        
        # Cálculos Matemáticos
        precos_dict = {s: df_cat[df_cat["Categoria"] == cat][s].values[0] for s in escolhidos}
        subtotal = sum(precos_dict.values()) + extra_v
        total_final = subtotal - desconto_v # Aplica o desconto
        
        # Proteção para não ficar negativo
        if total_final < 0: total_final = 0.0
        
        # Comissões baseadas no valor FINAL (Já com desconto, para dividir o prejuízo do desconto)
        comissao_prev = total_final * 0.40 if "Irmão" in quem else 0.0
        fundo_prev = total_final * 0.10
        lucro_prev = total_final - comissao_prev - fundo_prev
        
        # Exibição do Card de Orçamento
        cor_valor = "#39FF14" if desconto_v == 0 else "#FFC107" # Muda cor se tiver desconto
        html_desconto = f"<span style='color:#FF5555; font-size:16px'> (Desc: -{formatar_moeda(desconto_v)})</span>" if desconto_v > 0 else ""
        
        st.markdown(f"""<div style='background:#111;padding:15px;border-radius:10px;border:1px solid #333'>
        <h4><i class="bi bi-tag-fill"></i> Total Final: <span style='color:{cor_valor}'>{formatar_moeda(total_final)}</span>{html_desconto}</h4>
        <small>Fundo (10%): {formatar_moeda(fundo_prev)} | Comissão: {formatar_moeda(comissao_prev)}</small>
        <p style='color:#ddd; margin:5px 0 0 0; font-weight:bold'>Lucro Líquido Previsto: {formatar_moeda(lucro_prev)}</p>
        </div>""", unsafe_allow_html=True)
        
        if st.button("CONFIRMAR AGENDAMENTO", use_container_width=True):
            if cli and veic and (escolhidos or extra_v > 0):
                servicos_finais = ", ".join(escolhidos)
                if extra_n: servicos_finais += f" (+ {extra_n})"
                # Salva o Total Final já com o desconto aplicado
                dados = {"Data": dt.strftime("%d/%m/%Y"), "Hora": hr, "Cliente": cli, "Veiculo": veic, "Placa": placa, "Servicos": servicos_finais, "Total": total_final, "Executor": quem, "LucroPrevisto": lucro_prev, "Categoria": cat}
                sucesso, msg = salvar_no_google("Agendamentos", dados)
                if sucesso: st.success("Agendado com sucesso!"); st.balloons()
                else: st.error(f"ERRO AO CONECTAR: {msg}")
            else: st.error("Preencha o cliente e pelo menos um serviço!")
            
    with tab_list:
        df_a = carregar_dados("Agendamentos")
        if df_a.empty: st.info("Sua agenda está vazia.")
        else:
            for i, r in df_a.iterrows():
                with st.container():
                    total_val = float(r["Total"])
                    st.markdown(f"""<div class="agenda-card"><div style="margin-bottom:8px; font-weight:bold; color:#00B4DB"><i class="bi bi-calendar4-week"></i> {r["Data"]} &nbsp;|&nbsp; <i class="bi bi-clock"></i> {r["Hora"]}</div><div style="font-size:18px; font-weight:bold; margin-bottom:5px">{obter_icone_veiculo(r.get("Categoria", ""))} {r["Veiculo"]}</div><div style="color:#aaa; font-size:14px; margin-bottom:5px"><i class="bi bi-person-fill"></i> {r["Cliente"]}</div><div style="font-size:20px; font-weight:bold; color:#39FF14">{formatar_moeda(total_val)}</div></div>""", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(f"CONCLUIR SERVIÇO", key=f"efet_{i}"):
                            fundo_caixa = total_val * 0.10
                            comissao = total_val * 0.40 if "Irmão" in r["Executor"] else 0.0
                            lucro_liq = total_val - fundo_caixa - comissao
                            data_retorno_str = ""
                            if "vitrific" in r["Servicos"].lower():
                                try:
                                    dt_obj = datetime.strptime(r["Data"], "%d/%m/%Y")
                                    data_retorno_str = (dt_obj + timedelta(days=180)).strftime("%d/%m/%Y")
                                    st.toast(f"📅 Retorno de Vitrificação: {data_retorno_str}", icon="💎")
                                except: pass
                            nova_venda = {"Data": r["Data"], "Cliente": r["Cliente"], "Carro": r["Veiculo"], "Placa": r["Placa"], "Serviços": r["Servicos"], "Total": total_val, "Status": "Concluído", "Pagamento": "-", "Funcionario": r["Executor"], "Valor Comissao": comissao, "Fundo Caixa": fundo_caixa, "Lucro Liquido": lucro_liq, "Agendamentos": "", "Status Comissao": "Pendente", "Categoria": r.get("Categoria", ""), "Data Retorno": data_retorno_str}
                            sucesso_v, msg_v = salvar_no_google("Vendas", nova_venda)
                            if sucesso_v:
                                if excluir_agendamento(i): st.success("Serviço Concluído!"); t_sleep.sleep(1.5); st.rerun()
                            else: st.error(f"ERRO: {msg_v}")
                    with c2:
                        precos_pdf = {r["Servicos"]: total_val}
                        pdf_bytes = gerar_pdf(r["Cliente"], r["Veiculo"], r["Placa"], r["Data"], precos_pdf, total_val)
                        st.download_button("BAIXAR ORÇAMENTO (PDF)", data=pdf_bytes, file_name=f"Orcamento_{r['Cliente']}.pdf", mime="application/pdf", key=f"pdf_{i}")

def page_despesas():
    st.markdown('<h1 class="custom-title"><i class="bi bi-receipt" style="color: #D90429;"></i> Despesas Externas</h1>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1]); desc = c1.text_input("Descrição"); val = c2.number_input("Valor", min_value=0.0)
    if st.button("LANÇAR DESPESA"):
        sucesso, msg = salvar_no_google("Despesas", {"Data": datetime.now().strftime("%d/%m/%Y"), "Descricao": desc, "Valor": val})
        if sucesso: st.success("Salvo!")
        else: st.error(f"Erro ao conectar na planilha: {msg}")

def page_historico():
    st.markdown('<h1 class="custom-title"><i class="bi bi-clock-history" style="color: #FFC107;"></i> Garagem & Histórico</h1>', unsafe_allow_html=True)
    df = carregar_dados("Vendas")
    if df.empty: st.info("Sem registros."); return
    busca = st.text_input("Buscar...").strip().lower(); df_f = df.iloc[::-1]
    if busca: df_f = df_f[df_f.apply(lambda r: busca in str(r).lower(), axis=1)]
    for _, r in df_f.iterrows():
        cor = "#28a745" if r['Status'] == "Concluído" else "#ffc107"
        st.markdown(f"""<div class="history-card" style="border-left: 5px solid {cor}"><div style="display: flex; justify-content: space-between"><div><h3 style="margin:0">{obter_icone_veiculo(r.get("Categoria", ""))} {r["Carro"]}</h3><p style="margin:5px 0; color:#aaa"><i class="bi bi-person"></i> {r["Cliente"]} &nbsp;•&nbsp; <i class="bi bi-calendar"></i> {r["Data"]}</p><small style="color:#666"><i class="bi bi-tools"></i> {r["Serviços"]}</small></div><div style="text-align: right"><h2 style="color: #38ef7d; margin:0">{formatar_moeda(float(r["Total"]))}</h2><span style="font-size:12px; text-transform:uppercase; letter-spacing:1px; background:#222; padding:3px 8px; border-radius:4px">{r["Status"]}</span></div></div></div>""", unsafe_allow_html=True)

# --- MENU LATERAL ---
with st.sidebar:
    if os.path.exists("logo_sidebar.png"): st.image("logo_sidebar.png", use_container_width=True)
    elif os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    
    menu = st.radio("NAVEGAÇÃO", ["DASHBOARD", "AGENDAMENTO", "FINANCEIRO", "DESPESAS", "HISTÓRICO"], label_visibility="collapsed")
    st.write("---")
    
    # --- GRÁFICO VELOCÍMETRO (INTELIGENTE: SÓ MÊS ATUAL) ---
    df_meta = carregar_dados("Vendas")
    total_vendido_mes = 0.0
    hoje = datetime.now()
    if not df_meta.empty:
        # Converter números
        for c in ["Total"]: df_meta[c] = pd.to_numeric(df_meta[c].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0)
        # Converter datas e filtrar mês
        df_meta['Data_dt'] = pd.to_datetime(df_meta['Data'], format='%d/%m/%Y', errors='coerce')
        df_meta_mes = df_meta[(df_meta['Data_dt'].dt.month == hoje.month) & (df_meta['Data_dt'].dt.year == hoje.year)]
        # Somar apenas concluídos deste mês
        total_vendido_mes = df_meta_mes[df_meta_mes["Status"]=="Concluído"]["Total"].sum()
    
    META_MENSAL = 5000.00
    fig = go.Figure(go.Indicator(mode = "gauge+number", value = total_vendido_mes, domain = {'x': [0, 1], 'y': [0, 1]}, title = {'text': "META MENSAL", 'font': {'size': 18, 'color': "white"}}, gauge = {'axis': {'range': [None, 6000], 'tickwidth': 1, 'tickcolor': "white"}, 'bar': {'color': "#D90429"}, 'bgcolor': "black", 'borderwidth': 2, 'bordercolor': "#333", 'steps': [{'range': [0, 1500], 'color': '#333'}, {'range': [1500, 3500], 'color': '#444'}], 'threshold': {'line': {'color': "#00B4DB", 'width': 4}, 'thickness': 0.75, 'value': META_MENSAL}}))
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "white", 'family': "Montserrat"}, height=250, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

if menu == "DASHBOARD": page_dashboard()
elif menu == "AGENDAMENTO": page_agendamento()
elif menu == "FINANCEIRO": page_financeiro()
elif menu == "DESPESAS": page_despesas()
elif menu == "HISTÓRICO": page_historico()

# --- RODAPÉ FIXO ---
st.markdown('<div class="footer">Desenvolvido por <b>Jairan Jesus Matos</b> | JM Detail System © 2026</div>', unsafe_allow_html=True)
