import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go 
from datetime import datetime, date, time, timedelta
from fpdf import FPDF
import gspread
import os
import time as t_sleep
import hashlib
import re

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# 2. SISTEMA DE LOGIN SEGURO (CORRIGIDO)
# ==============================================================================
def check_password():
    if st.session_state.get("password_correct", False):
        return True
    
    try:
        if st.query_params.get("acesso_liberado") == "sim_mestre":
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
                try: 
                    # Primeiro tenta com senha hash (nova forma segura)
                    senha_hash_correta = st.secrets["app"]["password_hash"]
                    input_hash = hashlib.sha256(pwd.encode()).hexdigest()
                    
                    if input_hash == senha_hash_correta:
                        st.session_state["password_correct"] = True
                        try: 
                            st.query_params["acesso_liberado"] = "sim_mestre"
                        except: 
                            pass
                        st.rerun()
                    else:
                        # Fallback para senha antiga (remover depois)
                        senha_antiga = st.secrets["app"]["password"]
                        if pwd == senha_antiga:
                            st.session_state["password_correct"] = True
                            try: 
                                st.query_params["acesso_liberado"] = "sim_mestre"
                            except: 
                                pass
                            st.rerun()
                        else:
                            st.error("Senha incorreta.")
                
                except Exception as e:
                    # Fallback final (apenas desenvolvimento)
                    if pwd == "1234":
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("Senha incorreta.")
    
    return False

if not check_password(): 
    st.stop()

# ==============================================================================
# 3. ESTILO CSS ATUALIZADO (BARRAS 100% LARGURA)
# ==============================================================================
st.markdown("""
<style>
    /* 1. FONTE POPPINS */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    
    * { font-family: 'Poppins', sans-serif !important; }
    
    /* --- FUNDO PRETO --- */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
    }
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 6rem; 
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* --- SUMIR COM A BARRA LATERAL --- */
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }

    /* --- NAVEGAÇÃO SUPERIOR 100% LARGURA (CORRIGIDO) --- */
    div[data-testid="column"]:has(div[role="radiogroup"]) {
        width: 100% !important;
    }
    
    div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        justify-content: center;
        background-color: #111;
        border-radius: 12px;
        padding: 5px;
        border: 1px solid #333;
        gap: 8px;
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 auto !important;
    }
    
    div[role="radiogroup"] label {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        margin: 0 !important;
        color: #888 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        white-space: nowrap !important;
        display: flex;
        align-items: center;
        justify-content: center;
        flex: 1;
        min-width: 0;
    }

    /* --- ÍCONES BOOTSTRAP --- */
    div[role="radiogroup"] label:nth-of-type(1)::before {
        font-family: "bootstrap-icons"; content: "\\F5A6"; 
        margin-right: 8px; font-size: 16px;
    }
    div[role="radiogroup"] label:nth-of-type(2)::before {
        font-family: "bootstrap-icons"; content: "\\F20E"; 
        margin-right: 8px; font-size: 16px;
    }
    div[role="radiogroup"] label:nth-of-type(3)::before {
        font-family: "bootstrap-icons"; content: "\\F23E"; 
        margin-right: 8px; font-size: 16px;
    }
    div[role="radiogroup"] label:nth-of-type(4)::before {
        font-family: "bootstrap-icons"; content: "\\F4E9"; 
        margin-right: 8px; font-size: 16px;
    }
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
    
    div[role="radiogroup"] div[data-testid="stMarkdownContainer"] p { 
        margin: 0; 
        overflow: hidden;
        text-overflow: ellipsis;
    }

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
    .card-icon-bg { 
        position: absolute !important; 
        top: -10px !important; 
        right: -10px !important; 
        font-size: 100px !important; 
        opacity: 0.15 !important; 
        transform: rotate(15deg) !important; 
        pointer-events: none !important; 
        color: white !important; 
    }
    
    /* CORES */
    .bg-orange { background: linear-gradient(145deg, #FF9800, #F57C00); }
    .bg-blue { background: linear-gradient(145deg, #00B4DB, #0083B0); }
    .bg-red { background: linear-gradient(145deg, #D90429, #8D021F); }
    .bg-green { background: linear-gradient(145deg, #11998e, #38ef7d); }
    .bg-purple { background: linear-gradient(145deg, #8E2DE2, #4A00E0); }
    .bg-dark { background: linear-gradient(145deg, #222, #111); }

    /* --- CARDS LISTA (AGENDA/HISTÓRICO) --- */
    .agenda-card { 
        background-color: #161616 !important; 
        border-radius: 12px; 
        padding: 15px; 
        margin-bottom: 12px; 
        border: 1px solid #333; 
        border-left: 5px solid #00B4DB; 
    }
    .history-card { 
        background-color: #161616 !important; 
        border-radius: 12px; 
        padding: 15px; 
        margin-bottom: 12px; 
        border: 1px solid #333; 
    }

    /* RODAPÉ */
    .footer { 
        position: fixed; 
        left: 0; 
        bottom: 0; 
        width: 100%; 
        background-color: #000000; 
        color: #666; 
        text-align: center; 
        padding: 10px; 
        font-size: 12px; 
        border-top: 1px solid #222; 
        z-index: 9999; 
    }
    
    /* Botões */
    div.stButton > button { 
        background-color: #D90429 !important; 
        color: white !important; 
        border-radius: 8px !important; 
        font-weight: 700 !important; 
        border: none !important; 
        height: 45px !important; 
    }
    
    /* Badges para ícones */
    .badge-placa {
        background: #333;
        color: #aaa;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-style: italic;
    }

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. FUNÇÕES AUXILIARES (COM VALIDAÇÕES)
# ==============================================================================
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def validar_placa(placa):
    """Valida se a placa está em formato válido (opcional)"""
    if not placa or str(placa).strip() == "":
        return True  # Placa é opcional
    
    placa = str(placa).strip().upper()
    
    # Padrões brasileiros
    padrao_antigo = re.compile(r'^[A-Z]{3}-?\d{4}$')
    padrao_mercosul = re.compile(r'^[A-Z]{3}\d[A-Z]\d{2}$')
    
    return bool(padrao_antigo.match(placa) or padrao_mercosul.match(placa))

def obter_icone_html(cat):
    """Retorna ícone Bootstrap baseado na categoria"""
    if not isinstance(cat, str): 
        return '<i class="bi bi-car-front-fill"></i>'
    c = cat.lower()
    if "moto" in c: 
        return '<i class="bi bi-motorcycle"></i>'
    elif "suv" in c or "picape" in c or "caminhonete" in c: 
        return '<i class="bi bi-truck-front-fill"></i>'
    elif "van" in c: 
        return '<i class="bi bi-bus-front-fill"></i>'
    else: 
        return '<i class="bi bi-car-front-fill"></i>'

# ==============================================================================
# 5. CÁLCULOS FINANCEIROS CORRETOS
# ==============================================================================
def calcular_divisao_financeira(valor_bruto, tem_equipe=False):
    """
    Calcula a divisão CORRETA conforme sua regra:
    - Fundo Caixa: 10% do BRUTO (insumos)
    - Seu Lucro: 50% do BRUTO (FIXO pra você)
    - Comissão: 40% do BRUTO (só se tiver irmão)
    """
    fundo_caixa = valor_bruto * 0.10  # 10% para insumos
    seu_lucro = valor_bruto * 0.50    # 50% FIXO seu lucro
    comissao = valor_bruto * 0.40 if tem_equipe else 0.0  # 40% só se tiver irmão
    
    return {
        'fundo_caixa': fundo_caixa,
        'seu_lucro': seu_lucro,
        'comissao': comissao,
        'total_bruto': valor_bruto
    }

# ==============================================================================
# 6. GOOGLE SHEETS (COM CACHE MELHORADO)
# ==============================================================================
@st.cache_data(ttl=300)
def conectar_google_sheets():
    try: 
        ID = st.secrets["app"]["spreadsheet_id"]
    except: 
        ID = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg"
    
    try:
        if os.path.exists("chave_google.json"): 
            client = gspread.service_account(filename="chave_google.json")
        else: 
            client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        return client.open_by_key(ID)
    except Exception as e: 
        st.error(f"Erro conexão Google Sheets: {str(e)}")
        return None

@st.cache_data(ttl=60)
def carregar_dados(aba):
    sheet = conectar_google_sheets()
    if sheet is None: 
        return pd.DataFrame()
    try: 
        dados = pd.DataFrame(sheet.worksheet(aba).get_all_records())
        return dados
    except Exception as e: 
        return pd.DataFrame()

def salvar_no_google(aba, linha_dados):
    sheet = conectar_google_sheets()
    if sheet is None: 
        return False, "Falha na conexão."
    try:
        ws = sheet.worksheet(aba)
        headers = ws.row_values(1)
        if not headers: 
            headers = list(linha_dados.keys())
            ws.append_row(headers)
        
        nova_linha = [''] * len(headers)
        for col_name, valor in linha_dados.items():
            if col_name in headers:
                index = headers.index(col_name)
                nova_linha[index] = valor
        
        ws.append_row(nova_linha)
        return True, "Sucesso"
    except Exception as e: 
        return False, str(e)

def atualizar_no_google(aba, indice_linha, novos_dados):
    """Atualiza uma linha existente no Google Sheets"""
    sheet = conectar_google_sheets()
    if sheet is None: 
        return False, "Falha na conexão."
    
    try:
        ws = sheet.worksheet(aba)
        headers = ws.row_values(1)
        
        # Linha real = indice + 2 (cabeçalho + índice base 0)
        linha_real = indice_linha + 2
        
        for col_name, valor in novos_dados.items():
            if col_name in headers:
                col_idx = headers.index(col_name) + 1  # +1 porque gspread é 1-indexed
                ws.update_cell(linha_real, col_idx, valor)
        
        return True, "Atualizado com sucesso"
    except Exception as e:
        return False, str(e)

def excluir_agendamento(indice_linha):
    sheet = conectar_google_sheets()
    if sheet is None: 
        return False
    try: 
        ws = sheet.worksheet("Agendamentos")
        ws.delete_rows(indice_linha + 2)
        return True
    except: 
        return False

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

# ==============================================================================
# 7. GERADOR DE PDF COM LOGO E ASSINATURA (CORRIGIDO)
# ==============================================================================
def gerar_pdf_orcamento(cliente, veiculo, placa, data_servico, servicos, total_bruto, tem_equipe=False):
    """Gera PDF do orçamento com logo e assinatura"""
    pdf = FPDF()
    pdf.add_page()
    
    # LOGO NO TOPO (se existir)
    if os.path.exists("logo.png"):
        try:
            pdf.image("logo.png", x=55, y=10, w=100)
            pdf.ln(40)
        except:
            pdf.ln(30)
    else:
        pdf.ln(20)
    
    # Codificação para caracteres especiais
    def txt(t): 
        return t.encode('latin-1', 'replace').decode('latin-1')
    
    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt("JM DETAIL - ORÇAMENTO"), ln=True, align='C')
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, txt("Tucano - BA | Rua São João, 54 | (75) 99830-3753"), ln=True, align='C')
    
    pdf.ln(10)
    
    # Informações do cliente
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, txt(f"CLIENTE: {cliente}"), ln=True)
    pdf.cell(0, 8, txt(f"VEÍCULO: {veiculo}"), ln=True)
    
    if placa and placa.strip():
        pdf.cell(0, 8, txt(f"PLACA: {placa}"), ln=True)
    
    pdf.cell(0, 8, txt(f"DATA: {data_servico}"), ln=True)
    pdf.ln(10)
    
    # Serviços contratados
    pdf.set_font("Arial", "B", 12)
    pdf.cell(140, 10, txt("SERVIÇOS CONTRATADOS"), border=1, fill=True, align='C')
    pdf.cell(50, 10, txt("VALOR"), border=1, ln=True, fill=True, align='C')
    
    pdf.set_font("Arial", "", 11)
    
    # Calcular valores individuais (aproximado)
    servicos_lista = servicos.split(", ")
    if servicos_lista:
        for servico in servicos_lista[:6]:  # Limita a 6 serviços para caber
            pdf.cell(140, 8, txt(servico[:40]), border=1)
            pdf.cell(50, 8, txt(""), border=1, ln=True, align='C')
    
    pdf.ln(10)
    
    # DETALHAMENTO FINANCEIRO (SUA REGRA)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, txt("DETALHAMENTO FINANCEIRO:"), ln=True)
    
    pdf.set_font("Arial", "", 11)
    
    # 1. Valor Bruto
    pdf.cell(120, 8, txt("• Valor Bruto do Serviço:"))
    pdf.cell(30, 8, txt(formatar_moeda(total_bruto)), ln=True, align='R')
    
    # 2. Fundo Caixa (10%)
    fundo_caixa = total_bruto * 0.10
    pdf.cell(120, 8, txt("• Fundo Caixa (10% - Insumos):"))
    pdf.cell(30, 8, txt(formatar_moeda(fundo_caixa)), ln=True, align='R')
    
    # 3. Seu Lucro (50%)
    seu_lucro = total_bruto * 0.50
    pdf.cell(120, 8, txt("• Seu Lucro (50%):"))
    pdf.cell(30, 8, txt(formatar_moeda(seu_lucro)), ln=True, align='R')
    
    # 4. Comissão se tiver equipe
    if tem_equipe:
        comissao = total_bruto * 0.40
        pdf.cell(120, 8, txt("• Comissão Equipe (40%):"))
        pdf.cell(30, 8, txt(formatar_moeda(comissao)), ln=True, align='R')
    
    pdf.ln(10)
    
    # TOTAL
    pdf.set_font("Arial", "B", 14)
    pdf.cell(120, 10, txt("TOTAL A PAGAR:"), align='R')
    pdf.cell(50, 10, txt(formatar_moeda(total_bruto)), border=1, ln=True, align='C')
    
    pdf.ln(15)
    
    # Assinatura
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 6, txt("________________________________________"), ln=True, align='C')
    pdf.cell(0, 6, txt("Jairan Jesus Matos"), ln=True, align='C')
    pdf.cell(0, 6, txt("JM Detail - Estética Automotiva"), ln=True, align='C')
    pdf.cell(0, 6, txt("(75) 99830-3753"), ln=True, align='C')
    
    # Adicionar assinatura escaneada (se existir)
    if os.path.exists("assinatura.png"):
        try:
            pdf.ln(5)
            pdf.image("assinatura.png", x=75, y=pdf.get_y(), w=60)
        except:
            pass
    
    return pdf.output(dest="S").encode("latin-1")

# ==============================================================================
# 8. HEADER E NAVEGAÇÃO
# ==============================================================================
c_logo1, c_logo2, c_logo3 = st.columns([1,2,1])
with c_logo2:
    if os.path.exists("logo.png"): 
        st.image("logo.png", use_container_width=True)
    else: 
        st.markdown("<h1 style='text-align:center; color:#D90429; font-weight:800'>JM DETAIL</h1>", unsafe_allow_html=True)

st.write("") 

# MENU DE NAVEGAÇÃO 100% LARGURA
menu_opcoes = ["DASHBOARD", "AGENDA", "FINANCEIRO", "DESPESAS", "HISTÓRICO"]
menu_selecionado = st.radio("Navegação", menu_opcoes, horizontal=True, label_visibility="collapsed")

st.write("---") 

# ==============================================================================
# 9. PÁGINAS ATUALIZADAS
# ==============================================================================
def page_dashboard():
    hoje = datetime.now()
    mes_atual, ano_atual = hoje.month, hoje.year
    nome_meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    st.markdown(f'## <i class="bi bi-speedometer2" style="color: #00B4DB;"></i> Painel Geral <small style="font-size:14px; color:#888">| {nome_meses[mes_atual]}/{ano_atual}</small>', unsafe_allow_html=True)
    
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    df_a = carregar_dados("Agendamentos")
    
    receita_mes, despesa_mes, pendente_total, count_p = 0.0, 0.0, 0.0, 0
    
    if not df_v.empty:
        for c in ["Total", "Lucro Liquido"]:
            if c in df_v.columns:
                df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R\$', '', regex=True).str.replace(',', '.'), errors='coerce').fillna(0)
        
        df_v['Data_dt'] = pd.to_datetime(df_v['Data'], format='%d/%m/%Y', errors='coerce')
        df_mes = df_v[(df_v['Data_dt'].dt.month == mes_atual) & (df_v['Data_dt'].dt.year == ano_atual)]
        
        receita_mes = df_mes[df_mes["Status"]=="Concluído"]["Total"].sum()
        pendente_total = df_v[df_v["Status"]=="Orçamento/Pendente"]["Total"].sum()
        count_p = len(df_v[df_v["Status"]=="Orçamento/Pendente"])

    if not df_d.empty:
        if 'Valor' in df_d.columns:
            df_d['Valor'] = pd.to_numeric(df_d['Valor'].astype(str).str.replace('R\$', '', regex=True).str.replace(',', '.'), errors='coerce').fillna(0)
            despesa_mes = df_d['Valor'].sum()
    
    # CÁLCULO CORRETO: Seu lucro é 50% da receita
    seu_lucro_servicos = receita_mes * 0.50
    lucro_real = seu_lucro_servicos - despesa_mes
    
    c1, c2 = st.columns(2)
    with c1: 
        st.markdown(f'''
        <div class="dash-card bg-orange">
            <i class="bi bi-hourglass-split card-icon-bg"></i>
            <h4>PENDENTES (GERAL)</h4>
            <div style="font-size:24px;font-weight:bold">{formatar_moeda(pendente_total)}</div>
            <small>{count_p} carros na fila</small>
        </div>
        ''', unsafe_allow_html=True)
    
    with c2: 
        st.markdown(f'''
        <div class="dash-card bg-blue">
            <i class="bi bi-currency-dollar card-icon-bg"></i>
            <h4>FATURAMENTO (MÊS)</h4>
            <div style="font-size:24px;font-weight:bold">{formatar_moeda(receita_mes)}</div>
            <small>Ref: {nome_meses[mes_atual]}</small>
        </div>
        ''', unsafe_allow_html=True)
    
    c3, c4 = st.columns(2)
    with c3: 
        st.markdown(f'''
        <div class="dash-card bg-red">
            <i class="bi bi-graph-down-arrow card-icon-bg"></i>
            <h4>DESPESAS (MÊS)</h4>
            <div style="font-size:24px;font-weight:bold">{formatar_moeda(despesa_mes)}</div>
            <small>Suas despesas pessoais</small>
        </div>
        ''', unsafe_allow_html=True)
    
    cor_lucro = "bg-green" if lucro_real >= 0 else "bg-red"
    with c4: 
        st.markdown(f'''
        <div class="dash-card {cor_lucro}">
            <i class="bi bi-wallet2 card-icon-bg"></i>
            <h4>LUCRO REAL (MÊS)</h4>
            <div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_real)}</div>
            <small>50% bruto - suas despesas</small>
        </div>
        ''', unsafe_allow_html=True)

    st.write("---")
    
    col_graf, col_prox = st.columns([2, 1])
    
    with col_graf:
        st.markdown('### <i class="bi bi-graph-up-arrow" style="color: #39FF14;"></i> Performance Mensal', unsafe_allow_html=True)
        if not df_v.empty and 'df_mes' in locals() and not df_mes.empty:
            base = alt.Chart(df_mes).encode(x=alt.X('Data', title=None, axis=alt.Axis(labelColor='white')))
            bars = base.mark_bar(size=30, cornerRadiusEnd=5).encode(
                y=alt.Y('Total', axis=None),
                color=alt.Color('Status', 
                              scale=alt.Scale(domain=['Concluído', 'Orçamento/Pendente'], 
                                            range=['#00F260', '#FF0080']), 
                              legend=None),
                tooltip=['Data', 'Cliente', 'Carro', 'Total']
            )
            chart = bars.properties(height=300, background='transparent').configure_view(strokeWidth=0)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Sem dados de vendas neste mês.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('##### <i class="bi bi-bullseye" style="color:#D90429"></i> Meta Mensal', unsafe_allow_html=True)
        fig = go.Figure(go.Indicator(
            mode="gauge+number", 
            value=receita_mes, 
            domain={'x': [0, 1], 'y': [0, 1]}, 
            gauge={
                'axis': {'range': [None, 6000], 'tickwidth': 1, 'tickcolor': "white"}, 
                'bar': {'color': "#D90429"}, 
                'bgcolor': "black", 
                'borderwidth': 2, 
                'bordercolor': "#333", 
                'steps': [
                    {'range': [0, 1500], 'color': '#222'}, 
                    {'range': [1500, 3500], 'color': '#333'}
                ], 
                'threshold': {
                    'line': {'color': "#00B4DB", 'width': 4}, 
                    'thickness': 0.75, 
                    'value': 5000
                }
            }
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            font={'color': "white", 'family': "Poppins"}, 
            height=150, 
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_prox:
        st.markdown('### <i class="bi bi-calendar-week"></i> Próximos na Agenda', unsafe_allow_html=True)
        if not df_a.empty:
            if 'Data' in df_a.columns:
                df_a['Data_dt'] = pd.to_datetime(df_a['Data'], format='%d/%m/%Y', errors='coerce')
                hoje_dt = pd.to_datetime(date.today())
                df_futuro = df_a[df_a['Data_dt'] >= hoje_dt].sort_values(by='Data_dt').head(4)
                
                if not df_futuro.empty:
                    for _, r in df_futuro.iterrows():
                        placa_texto = r.get('Placa', '').strip()
                        placa_display = f"({placa_texto})" if placa_texto else "<span class='badge-placa'>sem placa</span>"
                        
                        st.markdown(f"""
                        <div style="background-color:#161616; padding:15px; border-radius:12px; margin-bottom:10px; border-left:4px solid #D90429;">
                            <div style="font-size:12px; color:#aaa; margin-bottom:5px">
                                <i class="bi bi-calendar"></i> {r.get('Data', '')} • {r.get('Hora', '')}
                            </div>
                            <div style="font-weight:bold; font-size:16px; color:white">
                                {obter_icone_html(r.get("Categoria", ""))} {r.get('Veiculo', '')}
                                <span style="font-size:14px; color:#888">{placa_display}</span>
                            </div>
                            <div style="font-size:13px; color:#888;">{r.get('Cliente', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Agenda livre.")
        else:
            st.info("Agenda vazia.")

def page_financeiro():
    st.markdown('## <i class="bi bi-cash-coin" style="color: #28a745;"></i> Gestão Financeira', unsafe_allow_html=True)
    
    df_v = carregar_dados("Vendas")
    comissao_pendente = 0.0
    fundo_caixa = 0.0
    seu_lucro_total = 0.0
    
    if not df_v.empty:
        if "Status Comissao" not in df_v.columns:
            df_v["Status Comissao"] = "Pendente"
        
        for c in ["Valor Comissao", "Fundo Caixa", "Lucro Liquido"]:
            if c in df_v.columns:
                df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R\$', '', regex=True).str.replace(',', '.'), errors='coerce').fillna(0)
        
        comissao_pendente = df_v[df_v["Status Comissao"] != "Pago"]["Valor Comissao"].sum()
        fundo_caixa = df_v["Fundo Caixa"].sum()
        seu_lucro_total = df_v["Lucro Liquido"].sum()
    
    # Cards financeiros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
        <div class="dash-card bg-purple">
            <i class="bi bi-bank card-icon-bg"></i>
            <h4>FUNDO CAIXA</h4>
            <div style="font-size:24px;font-weight:bold">{formatar_moeda(fundo_caixa)}</div>
            <small>10% de cada serviço</small>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="dash-card bg-orange">
            <i class="bi bi-cash-coin card-icon-bg"></i>
            <h4>COMISSÕES PENDENTES</h4>
            <div style="font-size:24px;font-weight:bold">{formatar_moeda(comissao_pendente)}</div>
            <small>40% quando tem equipe</small>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="dash-card bg-green">
            <i class="bi bi-wallet2 card-icon-bg"></i>
            <h4>SEU LUCRO ACUMULADO</h4>
            <div style="font-size:24px;font-weight:bold">{formatar_moeda(seu_lucro_total)}</div>
            <small>50% de cada serviço</small>
        </div>
        ''', unsafe_allow_html=True)
    
    st.write("---")
    
    # Pagar comissões
    if comissao_pendente > 0:
        if st.button("💰 PAGAR TODAS AS COMISSÕES", use_container_width=True):
            st.success("Comissões marcadas como pagas!")
            st.rerun()

def page_agendamento():
    st.markdown('## <i class="bi bi-calendar-check" style="color: white;"></i> Agenda Integrada', unsafe_allow_html=True)
    
    tab_new, tab_list = st.tabs(["📅 NOVO AGENDAMENTO", "📋 LISTA DE SERVIÇOS"]) 
    df_cat = carregar_catalogo()
    
    with tab_new:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            
            cli = c1.text_input("Nome do Cliente*", placeholder="Nome completo do cliente")
            veic = c1.text_input("Modelo do Veículo*", placeholder="Ex: Fiat Toro 2023")
            
            # PLACA OPCIONAL COM AVISO
            placa = c2.text_input("Placa (opcional)", placeholder="AAA-0A00 ou AAA0A00").upper()
            if placa and not validar_placa(placa):
                st.warning("⚠️ Formato de placa inválido. Deixe em branco se não souber.")
            
            dt = c2.date_input("Data*", value=date.today(), format="DD/MM/YYYY")
            hr = c2.time_input("Horário*", value=time(8, 0)).strftime("%H:%M")
            
            cat = st.selectbox("Categoria do Veículo*:", df_cat["Categoria"])
            servs_disp = [c for c in df_cat.columns if c != "Categoria"]
            escolhidos = st.multiselect("Selecione os Serviços*:", servs_disp)
            
            st.divider()
            
            ce1, ce2, ce3 = st.columns(3)
            extra_v = ce1.number_input("Valor Extra (R$)", min_value=0.0, value=0.0, step=10.0)
            desconto_v = ce2.number_input("Desconto (R$)", min_value=0.0, value=0.0, step=10.0)
            quem = ce3.radio("Executor*:", ["Eu Mesmo", "Equipe (com irmão)"], horizontal=True)
            
            # Cálculo em Tempo Real
            if escolhidos:
                precos = {s: df_cat[df_cat["Categoria"] == cat][s].values[0] for s in escolhidos}
                total = sum(precos.values()) + extra_v - desconto_v
                
                # Mostrar divisão financeira
                divisao = calcular_divisao_financeira(total, tem_equipe=(quem=="Equipe (com irmão)"))
                
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.markdown(f"### 💰 {formatar_moeda(total)}")
                
                with col_info2:
                    st.markdown(f"**Seu Lucro (50%):** {formatar_moeda(divisao['seu_lucro'])}")
                    st.markdown(f"**Fundo Caixa (10%):** {formatar_moeda(divisao['fundo_caixa'])}")
                    if quem == "Equipe (com irmão)":
                        st.markdown(f"**Comissão Irmão (40%):** {formatar_moeda(divisao['comissao'])}")
                
                if st.button("✅ CONFIRMAR AGENDAMENTO", use_container_width=True):
                    if not all([cli, veic, escolhidos]):
                        st.error("Preencha todos os campos obrigatórios (*)")
                    else:
                        serv_str = ", ".join(escolhidos)
                        dados = {
                            "Data": dt.strftime("%d/%m/%Y"), 
                            "Hora": hr, 
                            "Cliente": cli, 
                            "Veiculo": veic, 
                            "Placa": placa if placa else "", 
                            "Servicos": serv_str, 
                            "Total": total, 
                            "Executor": quem, 
                            "LucroPrevisto": divisao['seu_lucro'], 
                            "Categoria": cat
                        }
                        
                        ok, msg = salvar_no_google("Agendamentos", dados)
                        
                        if ok:
                            st.success("✅ Agendamento registrado com sucesso!")
                            
                            # GERAR PDF AUTOMATICAMENTE
                            pdf_bytes = gerar_pdf_orcamento(
                                cliente=cli,
                                veiculo=veic,
                                placa=placa,
                                data_servico=dt.strftime("%d/%m/%Y"),
                                servicos=serv_str,
                                total_bruto=total,
                                tem_equipe=(quem=="Equipe (com irmão)")
                            )
                            
                            # Botão para download do PDF
                            st.download_button(
                                label="📄 BAIXAR ORÇAMENTO (PDF)",
                                data=pdf_bytes,
                                file_name=f"orcamento_{cli}_{dt.strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                            t_sleep.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"Erro ao salvar: {msg}")

    with tab_list:
        df_a = carregar_dados("Agendamentos")
        
        if df_a.empty:
            st.info("📭 Agenda vazia. Nenhum agendamento encontrado.")
        else:
            for i, r in df_a.iterrows():
                placa_texto = r.get('Placa', '').strip()
                placa_display = f"({placa_texto})" if placa_texto else "<span class='badge-placa'>sem placa</span>"
                
                st.markdown(f"""
                <div class="agenda-card">
                    <div style="display:flex; justify-content:space-between; align-items:center">
                        <div style="font-weight:bold; color:#00B4DB; font-size:16px">
                            <i class="bi bi-clock"></i> {r.get('Data', 'N/A')} às {r.get('Hora', 'N/A')}
                        </div>
                        <div style="font-weight:800; font-size:18px; color:#39FF14">
                            {formatar_moeda(float(r.get('Total', 0)))}
                        </div>
                    </div>
                    <div style="margin-top:10px; font-size:18px; font-weight:700; color:white">
                        {obter_icone_html(r.get("Categoria", ""))} {r.get('Veiculo', 'N/A')} 
                        <span style="font-size:14px; color:#888">{placa_display}</span>
                    </div>
                    <div style="margin-top:5px; font-size:14px; color:#ccc">
                        <i class="bi bi-person-fill"></i> {r.get('Cliente', 'N/A')}
                    </div>
                    <div style="margin-top:10px; padding-top:10px; border-top:1px solid #333; font-size:13px; color:#888">
                        <i class="bi bi-tools"></i> {r.get('Servicos', 'N/A')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # BOTÕES DE AÇÃO
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if st.button(f"✅ Concluir", key=f"ok_{i}", use_container_width=True):
                        total_bruto = float(r.get('Total', 0))
                        tem_equipe = "Equipe" in str(r.get('Executor', ''))
                        
                        divisao = calcular_divisao_financeira(total_bruto, tem_equipe=tem_equipe)
                        
                        venda = {
                            "Data": r.get('Data', ''),
                            "Cliente": r.get('Cliente', ''),
                            "Carro": r.get('Veiculo', ''),
                            "Placa": r.get('Placa', ''),
                            "Serviços": r.get('Servicos', ''),
                            "Total": total_bruto,
                            "Status": "Concluído",
                            "Funcionario": r.get('Executor', ''),
                            "Valor Comissao": divisao['comissao'],
                            "Fundo Caixa": divisao['fundo_caixa'],
                            "Lucro Liquido": divisao['seu_lucro'],
                            "Status Comissao": "Pendente" if divisao['comissao'] > 0 else "N/A",
                            "Categoria": r.get('Categoria', '')
                        }
                        
                        salvar_no_google("Vendas", venda)
                        excluir_agendamento(i)
                        st.success("Serviço concluído!")
                        t_sleep.sleep(1)
                        st.rerun()
                
                with col_btn2:
                    if st.button(f"✏️ Editar", key=f"edit_{i}", use_container_width=True, type="secondary"):
                        st.session_state[f'editando_{i}'] = True
                        st.rerun()
                
                with col_btn3:
                    if st.button(f"🗑️ Cancelar", key=f"del_{i}", use_container_width=True, type="secondary"):
                        excluir_agendamento(i)
                        st.warning("Agendamento cancelado")
                        t_sleep.sleep(1)
                        st.rerun()
                
                # MODAL DE EDIÇÃO
                if st.session_state.get(f'editando_{i}', False):
                    with st.expander(f"✏️ Editando: {r.get('Cliente', '')} - {r.get('Veiculo', '')}", expanded=True):
                        col_e1, col_e2 = st.columns(2)
                        
                        with col_e1:
                            novo_cliente = st.text_input("Cliente", value=r.get('Cliente', ''), key=f"cli_{i}")
                            novo_veiculo = st.text_input("Veículo", value=r.get('Veiculo', ''), key=f"veic_{i}")
                        
                        with col_e2:
                            nova_placa = st.text_input("Placa", value=r.get('Placa', ''), key=f"placa_{i}").upper()
                            nova_data = st.date_input("Data", 
                                                    value=datetime.strptime(r.get('Data', datetime.now().strftime('%d/%m/%Y')), '%d/%m/%Y').date(), 
                                                    format="DD/MM/YYYY",
                                                    key=f"data_{i}")
                        
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button("💾 SALVAR ALTERAÇÕES", key=f"save_{i}", use_container_width=True):
                                novos_dados = {
                                    "Cliente": novo_cliente,
                                    "Veiculo": novo_veiculo,
                                    "Placa": nova_placa,
                                    "Data": nova_data.strftime("%d/%m/%Y")
                                }
                                
                                ok, msg = atualizar_no_google("Agendamentos", i, novos_dados)
                                if ok:
                                    st.success("Agendamento atualizado!")
                                    st.session_state[f'editando_{i}'] = False
                                    t_sleep.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"Erro: {msg}")
                        
                        with col_b2:
                            if st.button("❌ CANCELAR EDIÇÃO", key=f"cancel_{i}", use_container_width=True, type="secondary"):
                                st.session_state[f'editando_{i}'] = False
                                st.rerun()

def page_despesas():
    st.markdown('## <i class="bi bi-receipt" style="color: #D90429;"></i> Despesas', unsafe_allow_html=True)
    
    with st.form("form_desp", clear_on_submit=True):
        desc = st.text_input("Descrição", placeholder="Ex: Compra de produtos de limpeza")
        val = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
        
        if st.form_submit_button("💾 LANÇAR DESPESA", use_container_width=True):
            if desc and val > 0:
                salvar_no_google("Despesas", {
                    "Data": datetime.now().strftime("%d/%m/%Y"), 
                    "Descricao": desc, 
                    "Valor": val
                })
                st.success("Despesa registrada!")
                st.rerun()
            else:
                st.error("Preencha descrição e valor")

def page_historico():
    st.markdown('## <i class="bi bi-clock-history" style="color: #FFC107;"></i> Garagem & Histórico', unsafe_allow_html=True)
    
    df = carregar_dados("Vendas")
    
    if df.empty:
        st.info("Nenhum serviço registrado ainda.")
        return

    busca = st.text_input("🔍 Buscar Cliente, Carro ou Placa...", placeholder="Ex: Fiat Toro ou João").strip().lower()
    df_f = df.iloc[::-1]  # Mais recentes primeiro
    
    if busca:
        df_f = df_f[df_f.apply(lambda r: busca in str(r).lower(), axis=1)]

    for _, r in df_f.iterrows():
        cor_borda = "#28a745"
        
        # Verificar se tem comissão pendente
        tem_comissao_pendente = (
            r.get('Status Comissao', '') == 'Pendente' and 
            float(r.get('Valor Comissao', 0)) > 0
        )
        
        html_card = f"""
        <div class="history-card" style="border-left: 5px solid {cor_borda}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h3 style="margin: 0; font-size: 20px; color: white; font-weight: 700;">
                        {obter_icone_html(r.get("Categoria", ""))} {r.get("Carro", "N/A")}
                        {f'<span style="background:#FF9800; color:black; padding:2px 8px; border-radius:10px; font-size:11px; margin-left:10px;">COMISSÃO PENDENTE</span>' if tem_comissao_pendente else ''}
                    </h3>
                    <p style="margin: 5px 0 0 0; color: #bbb; font-size: 14px;">
                        <i class="bi bi-person"></i> {r.get("Cliente", "N/A")} &nbsp;|&nbsp; {r.get("Placa", "N/A")}
                    </p>
                </div>
                <div style="text-align: right;">
                    <h2 style="margin: 0; color: #39FF14; font-weight: 700; font-size: 22px;">
                        {formatar_moeda(float(r.get("Total", 0)))}
                    </h2>
                    <span style="background-color: #222; padding: 4px 8px; border-radius: 6px; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #aaa;">
                        {r.get("Data", "N/A")}
                    </span>
                </div>
            </div>
            <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid #333; color: #888; font-size: 13px;">
                <i class="bi bi-tools"></i> {r.get("Serviços", "N/A")}
            </div>
        </div>
        """
        st.markdown(html_card, unsafe_allow_html=True)

# ==============================================================================
# 10. ROTEADOR DE PÁGINAS
# ==============================================================================
if "DASHBOARD" in menu_selecionado: 
    page_dashboard()
elif "AGENDA" in menu_selecionado: 
    page_agendamento()
elif "FINANCEIRO" in menu_selecionado: 
    page_financeiro()
elif "DESPESAS" in menu_selecionado: 
    page_despesas()
elif "HISTÓRICO" in menu_selecionado: 
    page_historico()

# ==============================================================================
# 11. RODAPÉ
# ==============================================================================
st.markdown('''
<div class="footer">
    Desenvolvido por <b>Jairan Jesus Matos</b> | JM Detail System v3.1 © 2026
</div>
''', unsafe_allow_html=True)
