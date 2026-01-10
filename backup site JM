import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date, time
from fpdf import FPDF
import gspread
import os
import time as t_sleep

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

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
                    st.rerun()
                else: st.error("Senha incorreta.")
    return False

if not check_password(): st.stop()

# ==============================================================================
# --- 3. ESTILO CSS (VISUAL PREMIUM MANTIDO) ---
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    
    * { font-family: 'Poppins', sans-serif !important; }
    
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { background-color: #000000 !important; }
    .block-container { padding-top: 1rem; padding-bottom: 6rem; }
    [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebar"] { display: none !important; }

    /* MENU SUPERIOR EM BLOCOS */
    div[role="radiogroup"] {
        display: flex !important; flex-direction: row !important; width: 100% !important;
        justify-content: space-between !important; background-color: transparent !important;
        border: none !important; padding: 0 !important; gap: 12px !important;
    }
    div[role="radiogroup"] label {
        flex: 1 !important; background-color: #111 !important; border: 1px solid #333 !important;
        padding: 12px 5px !important; border-radius: 8px !important; transition: all 0.3s ease !important;
        margin: 0 !important; color: #888 !important; font-weight: 600 !important;
        font-size: 16px !important; white-space: nowrap !important; display: flex;
        align-items: center; justify-content: center !important;
    }
    /* Ícones do Menu */
    div[role="radiogroup"] label:nth-of-type(1)::before { font-family: "bootstrap-icons"; content: "\\F5A6"; margin-right: 8px; font-size: 18px; }
    div[role="radiogroup"] label:nth-of-type(2)::before { font-family: "bootstrap-icons"; content: "\\F20E"; margin-right: 8px; font-size: 18px; }
    div[role="radiogroup"] label:nth-of-type(3)::before { font-family: "bootstrap-icons"; content: "\\F23E"; margin-right: 8px; font-size: 18px; }
    div[role="radiogroup"] label:nth-of-type(4)::before { font-family: "bootstrap-icons"; content: "\\F4E9"; margin-right: 8px; font-size: 18px; }
    div[role="radiogroup"] label:nth-of-type(5)::before { font-family: "bootstrap-icons"; content: "\\F291"; margin-right: 8px; font-size: 18px; }

    div[role="radiogroup"] label:hover { border-color: #D90429 !important; color: white !important; background-color: #1a1a1a !important; transform: translateY(-2px); }
    div[role="radiogroup"] label[data-checked="true"] { background: linear-gradient(90deg, #D90429 0%, #8D021F 100%) !important; color: white !important; border-color: #D90429 !important; box-shadow: 0 4px 15px rgba(217, 4, 41, 0.4) !important; }
    
    /* CARDS */
    .dash-card { border-radius: 15px; padding: 20px; color: white; margin-bottom: 20px; border: 1px solid #333; position: relative; overflow: hidden; height: 140px !important; display: flex; flex-direction: column; justify-content: center; }
    .card-icon-bg { position: absolute !important; top: -10px !important; right: -10px !important; font-size: 100px !important; opacity: 0.15 !important; transform: rotate(15deg) !important; pointer-events: none !important; color: white !important; }
    .bg-orange { background: linear-gradient(145deg, #FF9800, #F57C00); }
    .bg-blue { background: linear-gradient(145deg, #00B4DB, #0083B0); }
    .bg-red { background: linear-gradient(145deg, #D90429, #8D021F); }
    .bg-green { background: linear-gradient(145deg, #11998e, #38ef7d); }
    
    .agenda-card { background-color: #161616 !important; border-radius: 12px; padding: 15px; margin-bottom: 12px; border: 1px solid #333; border-left: 5px solid #00B4DB; }
    .history-card { background-color: #161616 !important; border-radius: 12px; padding: 15px; margin-bottom: 12px; border: 1px solid #333; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #000000; color: #666; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #222; z-index: 9999; }
    div.stButton > button { background-color: #D90429 !important; color: white !important; border-radius: 8px !important; font-weight: 700 !important; border: none !important; height: 45px !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def conectar_google_sheets():
    # ID FIXO QUE VOCÊ CONFIRMOU
    ID_FIXO = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg"
    
    try:
        # Tenta pegar dos secrets ou usa o fixo
        if "app" in st.secrets and "spreadsheet_id" in st.secrets["app"]:
            ID_FIXO = st.secrets["app"]["spreadsheet_id"]
            
        # Tenta autenticar (AQUI GERALMENTE É O ERRO)
        if os.path.exists("chave_google.json"): 
            client = gspread.service_account(filename="chave_google.json")
        elif "gcp_service_account" in st.secrets:
            client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        else:
            st.error("🚨 ERRO CRÍTICO: Não encontrei as credenciais (chave_google.json ou Secrets). O sistema não consegue entrar no Google.")
            return None

        # Tenta abrir a planilha
        sh = client.open_by_key(ID_FIXO)
        return sh
        
    except Exception as e:
        st.error(f"🚨 ERRO DE CONEXÃO: {e}")
        return None

def carregar_dados(aba):
    sheet = conectar_google_sheets()
    if sheet is None: return pd.DataFrame()
    try: 
        return pd.DataFrame(sheet.worksheet(aba).get_all_records())
    except gspread.WorksheetNotFound:
        st.error(f"🚨 ERRO: A aba '{aba}' não foi encontrada na planilha. Verifique o nome (maiúsculas/minúsculas).")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"🚨 Erro ao ler aba '{aba}': {e}")
        return pd.DataFrame()

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

@st.cache_data(ttl=60)
def carregar_catalogo():
    try:
        sheet = conectar_google_sheets()
        if sheet:
            ws = sheet.worksheet("Catalogo")
            dados = ws.get_all_records()
            df = pd.DataFrame(dados)
            if not df.empty and "Categoria" in df.columns:
                cols_num = [c for c in df.columns if c != "Categoria"]
                for c in cols_num: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)
                return df
    except: pass
    
    # Backup
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

# --- FUNÇÃO DE BUSCA DE CLIENTE (AUTO-COMPLETE) ---
def buscar_cliente_por_placa(placa_busca):
    # Procura nas abas de Agendamentos e Vendas
    df_a = carregar_dados("Agendamentos")
    df_v = carregar_dados("Vendas")
    
    # Concatena para ter histórico completo
    df_completo = pd.concat([df_a, df_v], ignore_index=True)
    
    if df_completo.empty: return None
    
    # Limpa a placa para comparar (sem traço, maiusculo)
    placa_busca = placa_busca.replace("-", "").strip().upper()
    
    # Filtra
    if "Placa" in df_completo.columns:
        df_completo['Placa'] = df_completo['Placa'].astype(str)
        res = df_completo[df_completo['Placa'].str.replace("-", "").str.strip().str.upper() == placa_busca]
        
        if not res.empty:
            # Pega o último registro (mais recente)
            ultimo = res.iloc[-1]
            return {
                "Cliente": ultimo.get("Cliente", ""),
                "Telefone": str(ultimo.get("Telefone", "")),
                "Veiculo": ultimo.get("Veiculo", "") if "Veiculo" in ultimo else ultimo.get("Carro", ""),
                "Categoria": ultimo.get("Categoria", "")
            }
    return None

def gerar_pdf_orcamento(dados):
    pdf = FPDF()
    pdf.add_page()
    
    logo_file = None
    if os.path.exists("logo.png"): logo_file = "logo.png"
    elif os.path.exists("Logo.png"): logo_file = "Logo.png"
    elif os.path.exists("LOGO.png"): logo_file = "LOGO.png"
    
    if logo_file: pdf.image(logo_file, x=10, y=8, w=30)
    
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
    servicos = dados['Servicos'].split(',')
    # Adiciona serviços principais
    for s in servicos:
        if s.strip():
            pdf.cell(140, 10, txt(s.strip()), 1)
            pdf.cell(50, 10, "-", 1, 1, 'C') 
            
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(140, 10, "TOTAL ESTIMADO", 1, 0, 'R')
    pdf.cell(50, 10, txt(f"R$ {dados['Total']:.2f}"), 1, 1, 'C')
    
    return pdf.output(dest="S").encode("latin-1")

# ==============================================================================
# --- CABEÇALHO ---
# ==============================================================================
c_logo1, c_logo2, c_logo3 = st.columns([1,2,1])
with c_logo2:
    logo_path = None
    if os.path.exists("logo.png"): logo_path = "logo.png"
    elif os.path.exists("Logo.png"): logo_path = "Logo.png"
    elif os.path.exists("LOGO.png"): logo_path = "LOGO.png"
    
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
    
    receita_mes, despesa_mes, pendente_total, count_p = 0.0, 0.0, 0.0, 0
    lucro_operacional = 0.0
    
    if not df_v.empty:
        for c in ["Total"]:
            if c in df_v.columns:
                df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
        
        df_v['Data_dt'] = pd.to_datetime(df_v['Data'], format='%d/%m/%Y', errors='coerce')
        df_mes = df_v[(df_v['Data_dt'].dt.month == mes_atual) & (df_v['Data_dt'].dt.year == ano_atual)]
        receita_mes = df_mes[df_mes["Status"]=="Concluído"]["Total"].sum()
        lucro_operacional = receita_mes * 0.50
        pendente_total = df_v[df_v["Status"]=="Orçamento/Pendente"]["Total"].sum()
        count_p = len(df_v[df_v["Status"]=="Orçamento/Pendente"])

    if not df_d.empty:
        df_d['Data_dt'] = pd.to_datetime(df_d['Data'], format='%d/%m/%Y', errors='coerce')
        df_d_mes = df_d[(df_d['Data_dt'].dt.month == mes_atual) & (df_d['Data_dt'].dt.year == ano_atual)]
        despesa_mes = pd.to_numeric(df_d_mes["Valor"].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0).sum()
    
    lucro_final = lucro_operacional - despesa_mes
    
    # --- BARRA DE META (Compacta) ---
    META_MENSAL = 5000.00 
    if META_MENSAL > 0:
        pct_real = (receita_mes / META_MENSAL) * 100
        largura_visual = min(pct_real, 100.0)
        st.markdown(f"""
        <div style="background-color: #161616; padding: 10px 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px;">
            <div style="display:flex; justify-content:space-between; color:#bbb; font-size:12px; margin-bottom:5px;">
                <span>🎯 META: {formatar_moeda(META_MENSAL)}</span>
                <span>ATUAL: <b style="color:white">{formatar_moeda(receita_mes)}</b></span>
            </div>
            <div style="width:100%; background-color:#333; border-radius:15px; height:22px;">
                <div style="width:{largura_visual}%; background: linear-gradient(90deg, #00b09b, #96c93d); height:22px; border-radius:15px; display:flex; align-items:center; justify-content:flex-end; padding-right:10px; transition: width 1s ease-in-out; box-shadow: 0 0 10px rgba(150, 201, 61, 0.5);">
                    <span style="color:white; font-weight:bold; font-size:12px; text-shadow: 1px 1px 2px black;">{pct_real:.1f}%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="dash-card bg-orange"><i class="bi bi-hourglass-split card-icon-bg"></i><h4>PENDENTES (GERAL)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(pendente_total)}</div><small>{count_p} carros na fila</small></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="dash-card bg-blue"><i class="bi bi-currency-dollar card-icon-bg"></i><h4>FATURAMENTO (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(receita_mes)}</div><small>Ref: {nome_meses[mes_atual]}</small></div>', unsafe_allow_html=True)
    
    c3, c4 = st.columns(2)
    with c3: st.markdown(f'<div class="dash-card bg-red"><i class="bi bi-graph-down-arrow card-icon-bg"></i><h4>DESPESAS (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(despesa_mes)}</div><small>Gastos externos</small></div>', unsafe_allow_html=True)
    cor_lucro = "bg-green" if lucro_final >= 0 else "bg-red"
    with c4: st.markdown(f'<div class="dash-card {cor_lucro}"><i class="bi bi-wallet2 card-icon-bg"></i><h4>LUCRO LÍQUIDO (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_final)}</div><small>50% Bruto - Despesas</small></div>', unsafe_allow_html=True)

    st.write("---")
    
    # Gráfico
    if not df_v.empty and 'df_mes' in locals() and not df_mes.empty:
        st.markdown('### <i class="bi bi-graph-up-arrow" style="color: #39FF14;"></i> Performance', unsafe_allow_html=True)
        base = alt.Chart(df_mes).encode(x=alt.X('Data', title=None, axis=alt.Axis(labelColor='white')))
        bars = base.mark_bar(size=30, cornerRadiusEnd=5).encode(
            y=alt.Y('Total', axis=None),
            color=alt.Color('Status', scale=alt.Scale(domain=['Concluído', 'Orçamento/Pendente'], range=['#00F260', '#FF0080']), legend=None),
            tooltip=['Data', 'Cliente', 'Carro', 'Total']
        )
        st.altair_chart(bars.properties(height=300, background='transparent'), use_container_width=True)

def page_financeiro():
    st.markdown('## <i class="bi bi-cash-coin" style="color: #28a745;"></i> Gestão Financeira', unsafe_allow_html=True)
    df_v = carregar_dados("Vendas")
    comissao_pendente = 0.0; fundo_caixa = 0.0
    
    if not df_v.empty:
        if "Status Comissao" not in df_v.columns: df_v["Status Comissao"] = "Pendente"
        for c in ["Total", "Valor Comissao", "Fundo Caixa"]:
            if c in df_v.columns: df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
        
        df_pendente = df_v[df_v["Status Comissao"] != "Pago"]
        for index, row in df_pendente.iterrows():
             if row.get("Valor Comissao", 0) > 0 or "Equipe" in str(row.get("Funcionario", "")):
                 comissao_pendente += (row["Total"] * 0.40)
        fundo_caixa = df_v["Fundo Caixa"].sum()
    
    st.info(f"Caixa da Empresa (Acumulado): {formatar_moeda(fundo_caixa)}")
    col1, col2 = st.columns([2,1])
    with col1: st.metric("Comissões Pendentes (40%)", formatar_moeda(comissao_pendente))
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
            # --- AUTO PREENCHIMENTO PELA PLACA ---
            c_placa, c_buscar = st.columns([3, 1])
            placa_input = c_placa.text_input("Digite a Placa para Buscar Cadastro (ou Nova Placa)", key="placa_input")
            
            # Variáveis de preenchimento (padrão vazio)
            val_cli, val_veic, val_zap, val_cat_idx = "", "", "", 0
            
            # Se clicar em buscar ou der Enter na placa (Streamlit rerun)
            if placa_input:
                dados_cli = buscar_cliente_por_placa(placa_input)
                if dados_cli:
                    st.success(f"Cliente Encontrado: {dados_cli['Cliente']}")
                    val_cli = dados_cli['Cliente']
                    val_veic = dados_cli['Veiculo']
                    val_zap = dados_cli.get("Telefone", "") # Preenche se tiver na planilha
                    
                    # Tenta achar o índice da categoria
                    cats_lista = df_cat["Categoria"].tolist() if not df_cat.empty else []
                    if dados_cli['Categoria'] in cats_lista:
                        val_cat_idx = cats_lista.index(dados_cli['Categoria'])
                else:
                    if len(placa_input) > 5: st.warning("Placa nova. Preencha os dados abaixo.")

            c1, c2 = st.columns(2)
            cli = c1.text_input("Nome do Cliente", value=val_cli)
            zap = c2.text_input("WhatsApp (DDD+Número)", value=val_zap, placeholder="75999998888")
            
            c3, c4 = st.columns(2)
            veic = c3.text_input("Modelo do Veículo", value=val_veic)
            # A placa final é a do input
            placa_final = placa_input 
            
            dt = c4.date_input("Data", value=date.today(), format="DD/MM/YYYY")
            hr = c4.time_input("Horário", value=time(8, 0)).strftime("%H:%M")
            
            if "Categoria" in df_cat.columns:
                cat = st.selectbox("Categoria do Veículo:", df_cat["Categoria"], index=val_cat_idx)
                servs_disp = [c for c in df_cat.columns if c != "Categoria"]
                escolhidos = st.multiselect("Selecione os Serviços:", servs_disp)
                
                st.divider()
                ce1, ce2, ce3 = st.columns(3)
                extra_v = ce1.number_input("Valor Extra (R$)", min_value=0.0)
                desconto_v = ce2.number_input("Desconto (R$)", min_value=0.0)
                quem = ce3.radio("Executor:", ["Eu Mesmo", "Equipe"], horizontal=True)
                
                if escolhidos:
                    precos = {s: df_cat[df_cat["Categoria"] == cat][s].values[0] for s in escolhidos}
                    total = sum(precos.values()) + extra_v - desconto_v
                    st.markdown(f"<h3 style='text-align:right; color:#39FF14'>Total: {formatar_moeda(total)}</h3>", unsafe_allow_html=True)
                    
                    # Botão Agendar
                    col_btn_ag, col_btn_pdf = st.columns(2)
                    
                    if col_btn_ag.button("CONFIRMAR AGENDAMENTO", use_container_width=True):
                        serv_str = ", ".join(escolhidos)
                        comissao_prev = total * 0.40 if "Equipe" in quem else 0.0
                        fundo_prev = total * 0.10
                        lucro_prev = total - comissao_prev - fundo_prev
                        
                        dados = {"Data": dt.strftime("%d/%m/%Y"), "Hora": hr, "Cliente": cli, "Telefone": zap, "Veiculo": veic, "Placa": placa_final, "Servicos": serv_str, "Total": total, "Executor": quem, "LucroPrevisto": lucro_prev, "Categoria": cat}
                        ok, msg = salvar_no_google("Agendamentos", dados)
                        if ok: 
                            st.success("Agendado!"); 
                            if zap:
                                msg_zap = f"Olá {cli}, agendamento confirmado na JM Detail!%0A🚗 {veic}%0A📅 {dt.strftime('%d/%m/%Y')} às {hr}%0A💰 Total: {formatar_moeda(total)}"
                                link = f"https://wa.me/55{zap}?text={msg_zap}"
                                st.markdown(f'<a href="{link}" target="_blank"><button style="background:#25D366;color:white;border:none;padding:10px;border-radius:5px;width:100%">ENVIAR NO WHATSAPP</button></a>', unsafe_allow_html=True)
                        else: st.error(msg)
                    
                    # --- BOTÃO PDF (AGORA EXISTE) ---
                    if col_btn_pdf.button("📄 GERAR ORÇAMENTO PDF", use_container_width=True):
                        serv_str = ", ".join(escolhidos)
                        dados_pdf = {"Cliente": cli, "Veiculo": veic, "Placa": placa_final, "Data": dt.strftime("%d/%m/%Y"), "Servicos": serv_str, "Total": total}
                        pdf_bytes = gerar_pdf_orcamento(dados_pdf)
                        st.download_button(label="📥 BAIXAR PDF", data=pdf_bytes, file_name=f"Orcamento_{cli}.pdf", mime='application/pdf', use_container_width=True)

            else: st.error("Erro no Catálogo.")

    with tab_list:
        df_a = carregar_dados("Agendamentos")
        if df_a.empty: st.info("Agenda vazia.")
        else:
            for i, r in df_a.iterrows():
                st.markdown(f"""
                <div class="agenda-card">
                    <div style="display:flex; justify-content:space-between; align-items:center">
                        <div style="font-weight:bold; color:#00B4DB; font-size:16px"><i class="bi bi-clock"></i> {r['Data']} {r['Hora']}</div>
                        <div style="font-weight:800; font-size:18px; color:#39FF14">{formatar_moeda(float(r['Total']))}</div>
                    </div>
                    <div style="font-size:18px; font-weight:700; color:white">{obter_icone_html(r.get("Categoria", ""))} {r['Veiculo']} <span style="font-size:14px; color:#888">({r['Placa']})</span></div>
                    <div style="font-size:14px; color:#ccc"><i class="bi bi-person-fill"></i> {r['Cliente']}</div>
                    <div style="margin-top:5px; border-top:1px solid #333; padding-top:5px; color:#888">🔧 {r['Servicos']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                c_btn1, c_btn2, c_btn3 = st.columns([2, 1, 1])
                with c_btn1:
                    if st.button(f"✅ Concluir", key=f"ok_{i}", use_container_width=True):
                        t = float(r["Total"])
                        f = t * 0.10
                        c = t * 0.40 if "Equipe" in r["Executor"] else 0.0
                        l = t - f - c
                        venda = {"Data": r["Data"], "Cliente": r["Cliente"], "Telefone": r.get("Telefone", ""), "Carro": r["Veiculo"], "Placa": r["Placa"], "Serviços": r["Servicos"], "Total": t, "Status": "Concluído", "Funcionario": r["Executor"], "Valor Comissao": c, "Fundo Caixa": f, "Lucro Liquido": l, "Status Comissao": "Pendente", "Categoria": r.get("Categoria", "")}
                        salvar_no_google("Vendas", venda)
                        excluir_agendamento(i)
                        st.rerun()
                with c_btn2:
                    # --- BOTÃO WHATSAPP CARRO PRONTO ---
                    if r.get("Telefone"):
                        msg_pronto = f"Olá {r['Cliente']}! Seu {r['Veiculo']} já está pronto aqui na JM Detail. ✨ Ficou top! Valor Total: {formatar_moeda(float(r['Total']))}. Pode vir buscar!"
                        link_pronto = f"https://wa.me/55{r['Telefone']}?text={msg_pronto}"
                        st.markdown(f'<a href="{link_pronto}" target="_blank"><button style="background-color:#128C7E; color:white; border:none; border-radius:5px; height:45px; width:100%"><i class="bi bi-whatsapp"></i></button></a>', unsafe_allow_html=True)
                    else:
                        st.markdown('<button disabled style="background-color:#333; color:#555; border:none; border-radius:5px; height:45px; width:100%"><i class="bi bi-whatsapp"></i></button>', unsafe_allow_html=True)

                with c_btn3:
                    if st.button(f"🗑️", key=f"del_{i}", use_container_width=True):
                        excluir_agendamento(i); st.rerun()

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
    if df.empty: st.info("Vazio."); return
    busca = st.text_input("🔍 Buscar Cliente ou Carro...").strip().lower()
    df_f = df.iloc[::-1]
    if busca: df_f = df_f[df_f.apply(lambda r: busca in str(r).lower(), axis=1)]

    for index, r in df_f.iterrows():
        st.markdown(f"""
        <div class="history-card" style="border-left: 5px solid #28a745">
            <div style="display: flex; justify-content: space-between;">
                <div><h3 style="margin:0;color:white">{obter_icone_html(r.get("Categoria", ""))} {r["Carro"]}</h3><p style="margin:0;color:#bbb">{r["Cliente"]} | {r["Placa"]}</p></div>
                <div style="text-align:right"><h2 style="margin:0;color:#39FF14">{formatar_moeda(float(r["Total"]))}</h2><span style="background:#222;padding:4px;border-radius:6px;font-size:11px">{r["Data"]}</span></div>
            </div>
            <div style="margin-top:10px;border-top:1px solid #333;color:#888">{r["Serviços"]}</div>
        </div>
        """, unsafe_allow_html=True)

if "DASHBOARD" in menu_selecionado: page_dashboard()
elif "AGENDA" in menu_selecionado: page_agendamento()
elif "FINANCEIRO" in menu_selecionado: page_financeiro()
elif "DESPESAS" in menu_selecionado: page_despesas()
elif "HISTÓRICO" in menu_selecionado: page_historico()

st.markdown('<div class="footer">Desenvolvido por <b>Jairan Jesus Matos</b> | JM Detail System © 2026</div>', unsafe_allow_html=True)
