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
from typing import Dict, List, Optional

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
    """Sistema de login com múltiplas camadas de segurança"""
    if st.session_state.get("password_correct", False):
        return True
    
    # Verificar parâmetro de URL (para acesso rápido)
    try:
        if st.query_params.get("acesso_liberado") == "sim_mestre":
            st.session_state["password_correct"] = True
            return True
    except:
        pass
    
    # Interface de login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            "### <i class='bi bi-shield-lock-fill' style='color:#D90429'></i> Acesso Restrito - JM Detail",
            unsafe_allow_html=True
        )
        
        with st.form("login_form"):
            pwd = st.text_input("Digite a senha de acesso:", type="password")
            submit = st.form_submit_button("ACESSAR SISTEMA")
            
            if submit:
                try:
                    # Tentar carregar senha dos secrets
                    senha_correta = st.secrets["app"]["password"]
                except:
                    # Senha padrão para desenvolvimento
                    senha_correta = "JM@2024"
                
                if pwd == senha_correta:
                    st.session_state["password_correct"] = True
                    st.session_state["login_time"] = datetime.now().isoformat()
                    
                    # Registrar log de login
                    registrar_log("Sistema", "Login realizado")
                    
                    try:
                        st.query_params["acesso_liberado"] = "sim_mestre"
                    except:
                        pass
                    
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
    
    return False

if not check_password():
    st.stop()

# ==============================================================================
# --- 3. ESTILO CSS OTIMIZADO (V14.1) ---
# ==============================================================================
st.markdown("""
<style>
    /* 1. FONTE POPPINS */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    
    * { 
        font-family: 'Poppins', sans-serif !important; 
        box-sizing: border-box;
    }
    
    /* --- FUNDO PRETO --- */
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"], 
    [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
    }
    
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 6rem; 
    }

    /* --- OCULTAR BARRA LATERAL --- */
    [data-testid="stSidebarCollapsedControl"] { 
        display: none !important; 
    }
    
    [data-testid="stSidebar"] { 
        display: none !important; 
    }

    /* --- NAVEGAÇÃO SUPERIOR COM ÍCONES --- */
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
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
    
    div[role="radiogroup"]::-webkit-scrollbar {
        display: none;
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
        cursor: pointer;
        min-width: 140px;
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
        transform: translateY(-2px);
    }

    /* Botão Selecionado */
    div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(90deg, #D90429 0%, #8D021F 100%) !important;
        color: white !important;
        border-color: #D90429 !important;
        box-shadow: 0 0 12px rgba(217, 4, 41, 0.5) !important;
    }
    
    div[role="radiogroup"] div[data-testid="stMarkdownContainer"] p { 
        margin: 0; 
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
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .dash-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
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
    
    /* CORES DOS CARDS */
    .bg-orange { background: linear-gradient(145deg, #FF9800, #F57C00); }
    .bg-blue { background: linear-gradient(145deg, #00B4DB, #0083B0); }
    .bg-red { background: linear-gradient(145deg, #D90429, #8D021F); }
    .bg-green { background: linear-gradient(145deg, #11998e, #38ef7d); }
    .bg-purple { background: linear-gradient(145deg, #8E2DE2, #4A00E0); }
    .bg-dark { background: linear-gradient(145deg, #222, #111); }

    /* --- CARDS HISTÓRICO CORRIGIDOS --- */
    .history-card { 
        background-color: #161616 !important; 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 20px; 
        border: 1px solid #333; 
        border-left: 5px solid #28a745;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .history-card h3 {
        color: white !important;
        margin: 0 0 10px 0 !important;
        font-size: 20px !important;
        font-weight: 700 !important;
    }
    
    .history-card p {
        color: #bbb !important;
        margin: 5px 0 !important;
        font-size: 14px !important;
    }
    
    .history-card .valor-total {
        color: #39FF14 !important;
        font-size: 22px !important;
        font-weight: 700 !important;
    }
    
    .history-card .servicos {
        color: #888 !important;
        font-size: 13px !important;
        margin-top: 12px !important;
        padding-top: 10px !important;
        border-top: 1px solid #333 !important;
    }
    
    .history-card .detalhes-financeiros {
        color: #666 !important;
        font-size: 12px !important;
        margin-top: 10px !important;
        display: flex !important;
        gap: 15px !important;
    }
    
    .history-card .info-adicional {
        color: #555 !important;
        font-size: 11px !important;
        margin-top: 10px !important;
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
        transition: all 0.3s ease !important;
    }
    
    div.stButton > button:hover {
        background-color: #8D021F !important;
        transform: scale(1.05);
    }
    
    /* Toast personalizado */
    .stToast {
        background-color: #1a1a1a !important;
        border: 1px solid #D90429 !important;
    }
    
    /* Responsividade Mobile */
    @media (max-width: 768px) {
        div[role="radiogroup"] {
            flex-direction: column !important;
            gap: 5px !important;
        }
        
        div[role="radiogroup"] label {
            min-width: 100% !important;
            margin: 2px 0 !important;
        }
        
        .dash-card {
            height: auto !important;
            min-height: 120px;
            margin-bottom: 10px;
        }
        
        .footer {
            position: relative;
            margin-top: 30px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- 4. FUNÇÕES AUXILIARES CORRIGIDAS ---
# ==============================================================================

def formatar_moeda(valor: float) -> str:
    """Formata valores monetários de forma segura"""
    try:
        if pd.isna(valor) or valor is None:
            return "R$ 0,00"
        valor = float(valor)
        # Formato brasileiro seguro
        valor_str = f"{valor:,.2f}"
        # Substituir . por , e , por .
        partes = valor_str.split('.')
        if len(partes) == 2:
            inteiro = partes[0].replace(',', '.')
            decimal = partes[1]
            return f"R$ {inteiro},{decimal}"
        else:
            return f"R$ {valor_str.replace(',', '.')},00"
    except (ValueError, TypeError):
        return "R$ 0,00"

def conectar_google_sheets():
    """Conexão otimizada com Google Sheets usando cache"""
    if 'sheet' in st.session_state:
        return st.session_state.sheet
    
    try:
        # Tentar carregar ID da planilha
        try:
            ID = st.secrets["app"]["spreadsheet_id"]
        except:
            ID = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg"
        
        # Conectar usando credenciais
        if os.path.exists("chave_google.json"):
            client = gspread.service_account(filename="chave_google.json")
        else:
            client = gspread.service_account_from_dict(
                dict(st.secrets["gcp_service_account"])
            )
        
        sheet = client.open_by_key(ID)
        st.session_state.sheet = sheet
        return sheet
    except Exception as e:
        st.error(f"❌ Erro na conexão com Google Sheets: {str(e)}")
        return None

@st.cache_data(ttl=300, show_spinner=False)
def carregar_dados_com_cache(aba: str) -> pd.DataFrame:
    """Carrega dados do Google Sheets com cache de 5 minutos"""
    try:
        sheet = conectar_google_sheets()
        if sheet is None:
            return pd.DataFrame()
        
        worksheet = sheet.worksheet(aba)
        dados = worksheet.get_all_records()
        
        if not dados:
            return pd.DataFrame()
        
        df = pd.DataFrame(dados)
        
        # Converter colunas de data
        if 'Data' in df.columns:
            df['Data_dt'] = pd.to_datetime(
                df['Data'], 
                format='%d/%m/%Y', 
                errors='coerce'
            )
        
        # Converter colunas numéricas
        colunas_numericas = ['Total', 'Lucro Liquido', 'Valor Comissao', 
                            'Fundo Caixa', 'Valor', 'LucroPrevisto']
        for col in colunas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace('R\$', '', regex=False)
                    .str.replace(',', '.'),
                    errors='coerce'
                ).fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados da aba {aba}: {str(e)}")
        return pd.DataFrame()

def carregar_vendas_corrigida():
    """Carrega dados de vendas com compatibilidade para nomes antigos e novos"""
    df = carregar_dados_com_cache("Vendas")
    
    if df.empty:
        return df
    
    # Mapear nomes antigos para novos
    mapeamento_colunas = {
        'Clients': 'Cliente',
        'Velody': 'Carro',
        'Place': 'Placa',
        'Services': 'Serviços',
        'Devolver': 'Status',
        'Local/Private': 'Funcionario',
        'Categories': 'Categoria'
    }
    
    # Renomear colunas se existirem
    for antigo, novo in mapeamento_colunas.items():
        if antigo in df.columns and novo not in df.columns:
            df = df.rename(columns={antigo: novo})
    
    # Garantir que colunas numéricas existem
    colunas_numericas = ['Total', 'Valor Comissao', 'Fundo Caixa', 'Lucro Liquido']
    for col in colunas_numericas:
        if col not in df.columns:
            df[col] = 0.0
    
    # Converter colunas numéricas
    for col in colunas_numericas:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Garantir coluna de status
    if 'Status' not in df.columns:
        df['Status'] = 'Concluído'
    
    if 'Status Comissao' not in df.columns:
        df['Status Comissao'] = 'Pendente'
    
    # Converter data
    if 'Data' in df.columns:
        df['Data_dt'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
    
    return df

@st.cache_data(ttl=600, show_spinner=False)
def carregar_todos_dados() -> Dict[str, pd.DataFrame]:
    """Carrega todos os dados principais de uma vez"""
    return {
        "vendas": carregar_vendas_corrigida(),
        "agendamentos": carregar_dados_com_cache("Agendamentos"),
        "despesas": carregar_dados_com_cache("Despesas")
    }

def validar_agendamento(cliente: str, veiculo: str, placa: str) -> List[str]:
    """Valida os dados de um agendamento"""
    erros = []
    
    if not cliente or not cliente.strip():
        erros.append("❌ Nome do cliente é obrigatório")
    elif len(cliente.strip()) < 3:
        erros.append("❌ Nome do cliente muito curto")
    
    if not veiculo or not veiculo.strip():
        erros.append("❌ Modelo do veículo é obrigatório")
    
    if not placa or not placa.strip():
        erros.append("❌ Placa é obrigatória")
    else:
        placa_upper = placa.strip().upper()
        # Validação de placa padrão brasileiro (antigo e Mercosul)
        padrao_antigo = r'^[A-Z]{3}\d{4}$'
        padrao_mercosul = r'^[A-Z]{3}\d{1}[A-Z]{1}\d{2}$'
        
        if not (re.match(padrao_antigo, placa_upper) or 
                re.match(padrao_mercosul, placa_upper)):
            erros.append("❌ Formato de placa inválido. Use: AAA1A11 ou AAA1111")
    
    return erros

def salvar_no_google(aba: str, linha_dados: Dict) -> tuple:
    """Salva dados no Google Sheets de forma otimizada"""
    try:
        sheet = conectar_google_sheets()
        if sheet is None:
            return False, "Falha na conexão"
        
        ws = sheet.worksheet(aba)
        headers = ws.row_values(1)
        
        if not headers:
            headers = list(linha_dados.keys())
            ws.append_row(headers)
        
        # Preparar linha para inserção
        nova_linha = [''] * len(headers)
        
        for col_name, valor in linha_dados.items():
            if col_name in headers:
                index = headers.index(col_name)
                nova_linha[index] = valor
        
        # Inserir linha
        ws.append_row(nova_linha)
        
        # Invalidar cache para esta aba
        st.cache_data.clear()
        
        return True, "✅ Dados salvos com sucesso!"
    
    except Exception as e:
        return False, f"❌ Erro ao salvar: {str(e)}"

def excluir_agendamento(indice_linha: int) -> bool:
    """Exclui um agendamento com confirmação"""
    try:
        sheet = conectar_google_sheets()
        if sheet is None:
            return False
        
        ws = sheet.worksheet("Agendamentos")
        ws.delete_rows(indice_linha + 2)  # +2 para linha 1 cabeçalho
        
        # Invalidar cache
        st.cache_data.clear()
        
        return True
    except Exception as e:
        st.error(f"Erro ao excluir: {str(e)}")
        return False

@st.cache_data
def carregar_catalogo() -> pd.DataFrame:
    """Catálogo de preços com cache"""
    return pd.DataFrame({
        "Categoria": ["Hatch/Compacto", "Sedã", "SUV/Caminhonete", 
                     "Picapes Grandes", "Vans/Utilitários", "Motocicleta"],
        "Lavagem Simples": [40.0, 50.0, 60.0, 70.0, 80.0, 30.0],
        "Lavagem Técnica": [150.0, 170.0, 190.0, 210.0, 230.0, 100.0],
        "Higienização Bancos": [80.0, 80.0, 80.0, 120.0, 150.0, 0.0],
        "Higienização Interna (Teto/Carpete)": [150.0, 150.0, 180.0, 200.0, 250.0, 0.0],
        "Combo Premium": [300.0, 320.0, 350.0, 400.0, 450.0, 0.0],
        "Limpeza Motor": [100.0, 100.0, 120.0, 150.0, 150.0, 80.0],
        "Faróis": [200.0, 200.0, 200.0, 200.0, 200.0, 100.0],
        "Cristalização Vidros": [90.0, 120.0, 150.0, 150.0, 150.0, 50.0],
        "Vitrificação": [800.0, 900.0, 1100.0, 1300.0, 1300.0, 500.0]
    })

def obter_icone_html(categoria: str) -> str:
    """Retorna ícone HTML baseado na categoria do veículo"""
    if not isinstance(categoria, str):
        return '🚗'
    
    c = categoria.lower()
    
    if "moto" in c:
        return '🏍️'
    elif "suv" in c or "picape" in c or "caminhonete" in c:
        return '🚙'
    elif "van" in c or "utilitário" in c:
        return '🚐'
    elif "hatch" in c or "compacto" in c:
        return '🚗'
    elif "sedã" in c or "sedan" in c:
        return '🚘'
    else:
        return '🚗'

def gerar_pdf(cliente: str, carro: str, placa: str, data_servico: str,
             servicos_com_precos: Dict, total: float) -> bytes:
    """Gera PDF do orçamento"""
    pdf = FPDF()
    pdf.add_page()
    
    # Adicionar logo se existir
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=55, y=10, w=100)
        pdf.ln(35)
    else:
        pdf.ln(20)
    
    def txt(t: str) -> str:
        """Helper para encoding"""
        return t.encode('latin-1', 'replace').decode('latin-1')
    
    # Cabeçalho
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt=txt("JM DETAIL - Estética Automotiva Premium"), 
             ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt=txt("Tucano - BA | Rua São João, 54 | (75) 99830-3753"), 
             ln=True, align='C')
    
    pdf.ln(10)
    
    # Informações do cliente
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt=txt(f"CLIENTE: {cliente}"), ln=True)
    pdf.cell(0, 10, txt=txt(f"VEÍCULO: {carro} | PLACA: {placa}"), ln=True)
    pdf.cell(0, 10, txt=txt(f"DATA: {data_servico}"), ln=True)
    pdf.ln(5)
    
    # Tabela de serviços
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(140, 10, txt("Pacote de Serviços"), border=1, fill=True)
    pdf.cell(50, 10, txt("Valor"), border=1, ln=True, fill=True, align='C')
    
    pdf.set_font("Arial", size=12)
    for servico, valor in servicos_com_precos.items():
        t_servico = (servico[:60] + '...') if len(servico) > 60 else servico
        pdf.cell(140, 10, txt=txt(t_servico), border=1)
        pdf.cell(50, 10, txt=txt(f"R$ {valor:.2f}"), border=1, ln=True, align='C')
    
    # Total
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(140, 10, txt("TOTAL", align='R'))
    pdf.cell(50, 10, txt=txt(f"R$ {total:.2f}"), border=1, align='C')
    
    # Rodapé
    pdf.ln(15)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, txt="Agradecemos pela preferência! Volte sempre.", 
             ln=True, align='C')
    
    return pdf.output(dest="S").encode("latin-1")

def registrar_log(usuario: str, acao: str, detalhes: str = ""):
    """Registra log de atividades"""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "usuario": usuario,
            "acao": acao,
            "detalhes": detalhes
        }
        
        # Salvar em arquivo de log
        log_file = "logs/atividades.json"
        os.makedirs("logs", exist_ok=True)
        
        logs = []
        if os.path.exists(log_file):
            with open(log_file, "r", encoding='utf-8') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(log_file, "w", encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    except Exception as e:
        print(f"Erro ao registrar log: {e}")

def verificar_agendamentos_proximos():
    """Verifica e notifica sobre agendamentos próximos"""
    try:
        df_a = carregar_dados_com_cache("Agendamentos")
        
        if df_a.empty or 'Data_dt' not in df_a.columns:
            return
        
        hoje = pd.to_datetime(date.today())
        amanha = hoje + timedelta(days=1)
        
        # Agendamentos para amanhã
        proximos = df_a[df_a['Data_dt'] == amanha]
        
        if not proximos.empty:
            st.toast(
                f"⚠️ Você tem {len(proximos)} agendamento(s) para amanhã!",
                icon="⚠️"
            )
    
    except Exception as e:
        print(f"Erro ao verificar agendamentos: {e}")

def calcular_kpis() -> Dict:
    """Calcula KPIs avançados"""
    dados = carregar_todos_dados()
    df_v = dados["vendas"]
    
    if df_v.empty:
        return {}
    
    try:
        # Ticket médio
        vendas_concluidas = df_v[df_v["Status"] == "Concluído"]
        ticket_medio = vendas_concluidas["Total"].mean() if not vendas_concluidas.empty else 0
        
        # Taxa de conversão
        total_orcamentos = len(df_v[df_v["Status"] == "Orçamento/Pendente"])
        total_concluidos = len(vendas_concluidas)
        taxa_conversao = (total_concluidos / (total_concluidos + total_orcamentos) * 100 
                         if (total_concluidos + total_orcamentos) > 0 else 0)
        
        return {
            "ticket_medio": ticket_medio,
            "taxa_conversao": taxa_conversao,
            "total_clientes": len(df_v["Cliente"].unique()),
        }
    
    except Exception as e:
        print(f"Erro ao calcular KPIs: {e}")
        return {}

def limpar_dados_antigos():
    """Remove todos os dados antigos da planilha, mantendo apenas serviços recentes"""
    st.warning("⚠️ **ATENÇÃO: Esta função vai DELETAR todos os dados antigos!**")
    st.error("🚨 **FAÇA BACKUP ANTES! Isso não pode ser desfeito!**")
    
    with st.expander("📋 Ver dados atuais antes de limpar"):
        df_v = carregar_vendas_corrigida()
        if not df_v.empty:
            st.dataframe(df_v, use_container_width=True)
            st.write(f"**Total de registros:** {len(df_v)}")
    
    if st.button("🧹 LIMPAR TODOS OS DADOS ANTIGOS", type="primary", use_container_width=True):
        # Confirmação EXTRA
        st.error("TEM CERTEZA? Isso vai apagar TUDO e deixar APENAS os 2 serviços atuais!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ SIM, LIMPAR TUDO", type="primary"):
                try:
                    sheet = conectar_google_sheets()
                    if sheet:
                        ws = sheet.worksheet("Vendas")
                        
                        # MANTER APENAS ESTES 2 SERVIÇOS (ajuste as datas conforme necessário)
                        novos_dados = [
                            # Cabeçalho
                            ['Data', 'Cliente', 'Carro', 'Placa', 'Serviços', 'Total', 'Status', 'Funcionario', 'Valor Comissao', 'Fundo Caixa', 'Lucro Liquido', 'Status Comissao', 'Categoria'],
                            # Serviço 1: R$ 208,00
                            ['01/02/2025', 'Cliente 1', 'Veículo 1', 'ABC1234', 'Lavagem Simples', 208.00, 'Concluído', 'Equipe', 83.20, 20.80, 104.00, 'Pendente', 'SUV/Caminhonete'],
                            # Serviço 2: R$ 140,00
                            ['01/02/2025', 'Cliente 2', 'Veículo 2', 'DEF5678', 'Lavagem Simples', 140.00, 'Concluído', 'Eu Mesmo', 0.00, 14.00, 126.00, 'Pago', 'Sedã']
                        ]
                        
                        # Limpar toda a planilha
                        ws.clear()
                        
                        # Adicionar novos dados
                        ws.update('A1', novos_dados)
                        
                        st.success("✅ Planilha limpa e resetada com os 2 serviços!")
                        st.balloons()
                        st.cache_data.clear()
                        t_sleep.sleep(3)
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        
        with col2:
            if st.button("❌ NÃO, CANCELAR"):
                st.rerun()

# ==============================================================================
# --- 5. CABEÇALHO E NAVEGAÇÃO ---
# ==============================================================================

# Logo e título
c_logo1, c_logo2, c_logo3 = st.columns([1, 2, 1])
with c_logo2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown(
            "<h1 style='text-align:center; color:#D90429; font-weight:800'>JM DETAIL PRO</h1>",
            unsafe_allow_html=True
        )

st.write("")

# Menu de navegação
menu_opcoes = ["DASHBOARD", "AGENDA", "FINANCEIRO", "DESPESAS", "HISTÓRICO"]
menu_selecionado = st.radio(
    "Navegação",
    menu_opcoes,
    horizontal=True,
    label_visibility="collapsed"
)

st.write("---")

# ==============================================================================
# --- 6. PÁGINAS DO SISTEMA CORRIGIDAS ---
# ==============================================================================

def page_dashboard():
    """Página principal do dashboard"""
    st.markdown(
        '## <i class="bi bi-speedometer2" style="color: #00B4DB;"></i> Painel Geral',
        unsafe_allow_html=True
    )
    
    # Carregar dados
    dados = carregar_todos_dados()
    df_v = dados["vendas"]
    df_d = dados["despesas"]
    df_a = dados["agendamentos"]
    
    hoje = datetime.now()
    mes_atual, ano_atual = hoje.month, hoje.year
    nome_meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    # Cálculos principais
    receita_mes, despesa_mes, pendente_total, count_p = 0.0, 0.0, 0.0, 0
    
    if not df_v.empty:
        # Filtrar mês atual
        if 'Data_dt' in df_v.columns:
            df_mes = df_v[
                (df_v['Data_dt'].dt.month == mes_atual) & 
                (df_v['Data_dt'].dt.year == ano_atual)
            ]
            receita_mes = df_mes[df_mes["Status"] == "Concluído"]["Total"].sum()
            pendente_total = df_v[df_v["Status"] == "Orçamento/Pendente"]["Total"].sum()
            count_p = len(df_v[df_v["Status"] == "Orçamento/Pendente"])
    
    if not df_d.empty and 'Data_dt' in df_d.columns:
        df_d_mes = df_d[
            (df_d['Data_dt'].dt.month == mes_atual) & 
            (df_d['Data_dt'].dt.year == ano_atual)
        ]
        despesa_mes = df_d_mes["Valor"].sum()
    
    lucro_final = receita_mes - despesa_mes
    
    # Cards principais
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'''
            <div class="dash-card bg-orange">
                <i class="bi bi-hourglass-split card-icon-bg"></i>
                <h4>PENDENTES (GERAL)</h4>
                <div style="font-size:24px;font-weight:bold">{formatar_moeda(pendente_total)}</div>
                <small>{count_p} carros na fila</small>
            </div>
            ''',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f'''
            <div class="dash-card bg-blue">
                <i class="bi bi-currency-dollar card-icon-bg"></i>
                <h4>FATURAMENTO (MÊS)</h4>
                <div style="font-size:24px;font-weight:bold">{formatar_moeda(receita_mes)}</div>
                <small>Ref: {nome_meses[mes_atual]}</small>
            </div>
            ''',
            unsafe_allow_html=True
        )
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(
            f'''
            <div class="dash-card bg-red">
                <i class="bi bi-graph-down-arrow card-icon-bg"></i>
                <h4>DESPESAS (MÊS)</h4>
                <div style="font-size:24px;font-weight:bold">{formatar_moeda(despesa_mes)}</div>
                <small>Gastos externos</small>
            </div>
            ''',
            unsafe_allow_html=True
        )
    
    cor_lucro = "bg-green" if lucro_final >= 0 else "bg-red"
    with col4:
        st.markdown(
            f'''
            <div class="dash-card {cor_lucro}">
                <i class="bi bi-wallet2 card-icon-bg"></i>
                <h4>LUCRO LÍQUIDO (MÊS)</h4>
                <div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_final)}</div>
                <small>Após comissões/insumos</small>
            </div>
            ''',
            unsafe_allow_html=True
        )
    
    st.write("---")
    
    # Gráficos e próxima agenda
    col_graf, col_prox = st.columns([2, 1])
    
    with col_graf:
        st.markdown(
            '### <i class="bi bi-graph-up-arrow" style="color: #39FF14;"></i> Performance Mensal',
            unsafe_allow_html=True
        )
        
        if not df_v.empty and 'df_mes' in locals() and not df_mes.empty:
            base = alt.Chart(df_mes).encode(
                x=alt.X('Data', title=None, axis=alt.Axis(labelColor='white'))
            )
            
            bars = base.mark_bar(size=30, cornerRadiusEnd=5).encode(
                y=alt.Y('Total', axis=None),
                color=alt.Color(
                    'Status',
                    scale=alt.Scale(
                        domain=['Concluído', 'Orçamento/Pendente'],
                        range=['#00F260', '#FF0080']
                    ),
                    legend=None
                ),
                tooltip=['Data', 'Cliente', 'Carro', 'Total', 'Lucro Liquido']
            )
            
            line = base.mark_line(color='#0575E6', strokeWidth=3).encode(
                y=alt.Y('Lucro Liquido', axis=None)
            )
            
            chart = alt.layer(bars, line).properties(
                height=300,
                background='transparent'
            ).configure_view(strokeWidth=0).configure_axis(
                grid=False,
                domain=False,
                ticks=False
            )
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("📊 Sem dados de vendas neste mês.")
        
        # Meta mensal
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '##### <i class="bi bi-bullseye" style="color:#D90429"></i> Meta Mensal',
            unsafe_allow_html=True
        )
        
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
        st.markdown(
            '### <i class="bi bi-calendar-week"></i> Próximos na Agenda',
            unsafe_allow_html=True
        )
        
        if not df_a.empty and 'Data_dt' in df_a.columns:
            hoje_dt = pd.to_datetime(date.today())
            df_futuro = df_a[df_a['Data_dt'] >= hoje_dt].sort_values(
                by='Data_dt'
            ).head(4)
            
            if not df_futuro.empty:
                for _, r in df_futuro.iterrows():
                    st.markdown(
                        f'''
                        <div style="background-color:#161616; padding:15px; border-radius:12px; 
                                 margin-bottom:10px; border-left:4px solid #D90429;">
                            <div style="font-size:12px; color:#aaa; margin-bottom:5px">
                                <i class="bi bi-calendar"></i> {r.get('Data', 'N/A')} • {r.get('Hora', 'N/A')}
                            </div>
                            <div style="font-weight:bold; font-size:16px; color:white">
                                {obter_icone_html(r.get("Categoria", ""))} {r.get('Veiculo', 'N/A')}
                            </div>
                            <div style="font-size:13px; color:#888;">{r.get('Cliente', 'N/A')}</div>
                        </div>
                        ''',
                        unsafe_allow_html=True
                    )
            else:
                st.info("🎉 Agenda livre para os próximos dias!")
        else:
            st.info("📅 Nenhum agendamento futuro encontrado.")

def page_financeiro():
    """Página de gestão financeira - CÁLCULOS CORRETOS"""
    st.markdown(
        '## <i class="bi bi-cash-coin" style="color: #28a745;"></i> Gestão Financeira',
        unsafe_allow_html=True
    )
    
    # Adicionar botão de limpeza
    with st.expander("🧹 Ferramentas de Limpeza (USE COM CUIDADO!)", expanded=False):
        limpar_dados_antigos()
    
    # Carregar dados
    df_v = carregar_vendas_corrigida()
    
    if df_v.empty:
        st.info("📊 Nenhuma venda registrada.")
        
        # Adicionar serviços manuais para teste
        if st.button("➕ Adicionar Serviços de Exemplo (R$ 208 + R$ 140)"):
            try:
                sheet = conectar_google_sheets()
                if sheet:
                    ws = sheet.worksheet("Vendas")
                    
                    # Cabeçalho se não existir
                    header = ws.row_values(1)
                    if not header:
                        ws.update('A1', [['Data', 'Cliente', 'Carro', 'Placa', 'Serviços', 'Total', 'Status', 'Funcionario', 'Valor Comissao', 'Fundo Caixa', 'Lucro Liquido', 'Status Comissao', 'Categoria']])
                    
                    # Adicionar os 2 serviços
                    novos_dados = [
                        ['01/02/2025', 'Cliente Exemplo 1', 'Fiat Toro', 'ABC1D23', 'Lavagem Completa', 208.00, 'Concluído', 'Equipe', 83.20, 20.80, 104.00, 'Pendente', 'SUV/Caminhonete'],
                        ['02/02/2025', 'Cliente Exemplo 2', 'Chevrolet Onix', 'DEF4G56', 'Lavagem Simples', 140.00, 'Concluído', 'Eu Mesmo', 0.00, 14.00, 126.00, 'Pago', 'Hatch/Compacto']
                    ]
                    
                    for dados in novos_dados:
                        ws.append_row(dados)
                    
                    st.success("✅ Serviços de exemplo adicionados!")
                    st.cache_data.clear()
                    t_sleep.sleep(2)
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
        
        return
    
    # Mostrar dados brutos para debug
    with st.expander("👁️ Ver todos os dados da planilha", expanded=True):
        st.dataframe(df_v, use_container_width=True)
        st.write(f"**Total de registros na planilha:** {len(df_v)}")
    
    # CÁLCULOS CORRETOS - Baseado na sua explicação
    st.write("---")
    st.markdown("### 🧮 Cálculos Financeiros")
    
    # 1. Somar todos os valores totais
    faturamento_bruto = df_v['Total'].sum()
    
    # 2. Calcular caixa (10% do total)
    caixa_empresa = faturamento_bruto * 0.10
    
    # 3. Calcular comissões (40% apenas dos serviços com equipe)
    if 'Funcionario' in df_v.columns:
        # Serviços feitos pela equipe
        servicos_equipe = df_v[df_v['Funcionario'].str.contains('Equipe|equipe', na=False)]
        comissoes_pendentes = servicos_equipe['Valor Comissao'].sum()
    else:
        comissoes_pendentes = 0
    
    # 4. Calcular lucro líquido
    lucro_liquido = faturamento_bruto - caixa_empresa - comissoes_pendentes
    
    # 5. Contar serviços
    total_servicos = len(df_v)
    servicos_com_equipe = len(df_v[df_v['Funcionario'].str.contains('Equipe|equipe', na=False)]) if 'Funcionario' in df_v.columns else 0
    servicos_sem_equipe = total_servicos - servicos_com_equipe
    
    # Exibir resultados
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Métricas Principais")
        
        metricas = [
            ("💰 Faturamento Bruto", faturamento_bruto),
            ("🏦 Caixa da Empresa (10%)", caixa_empresa),
            ("👥 Comissões da Equipe (40%)", comissoes_pendentes),
            ("📊 Lucro Líquido", lucro_liquido)
        ]
        
        for nome, valor in metricas:
            st.metric(nome, formatar_moeda(valor))
    
    with col2:
        st.markdown("#### 📊 Estatísticas")
        
        estatisticas = [
            ("📋 Total de Serviços", total_servicos),
            ("👨‍🔧 Com Equipe", servicos_com_equipe),
            ("👤 Sem Equipe", servicos_sem_equipe),
            ("📅 Mês Atual", datetime.now().strftime("%B/%Y"))
        ]
        
        for nome, valor in estatisticas:
            if isinstance(valor, (int, float)):
                st.metric(nome, valor)
            else:
                st.markdown(f"**{nome}:** {valor}")
    
    st.write("---")
    
    # TABELA DETALHADA
    st.markdown("### 📋 Detalhamento por Serviço")
    
    # Criar tabela formatada
    df_detalhes = df_v.copy()
    
    # Ordenar por data
    if 'Data_dt' in df_detalhes.columns:
        df_detalhes = df_detalhes.sort_values('Data_dt', ascending=False)
    
    # Mostrar tabela
    st.dataframe(
        df_detalhes[['Data', 'Cliente', 'Carro', 'Total', 'Funcionario', 'Valor Comissao', 'Fundo Caixa', 'Lucro Liquido', 'Status Comissao']],
        use_container_width=True,
        column_config={
            "Data": "📅 Data",
            "Cliente": "👤 Cliente", 
            "Carro": "🚗 Veículo",
            "Total": st.column_config.NumberColumn("💰 Total", format="R$ %.2f"),
            "Funcionario": "👷 Executor",
            "Valor Comissao": st.column_config.NumberColumn("💸 Comissão", format="R$ %.2f"),
            "Fundo Caixa": st.column_config.NumberColumn("🏦 Caixa", format="R$ %.2f"),
            "Lucro Liquido": st.column_config.NumberColumn("📈 Lucro", format="R$ %.2f"),
            "Status Comissao": "📌 Status"
        }
    )
    
    st.write("---")
    
    # VERIFICAÇÃO DOS CÁLCULOS
    st.markdown("### 🔍 Verificação dos Cálculos")
    
    # Fórmula explicada
    st.markdown("""
    #### 📝 Como são calculados os valores:
    
    **Para cada serviço:**
    ```
    1. Faturamento Bruto = Valor Total do Serviço
    2. Caixa da Empresa = 10% do Valor Total
    3. Comissão da Equipe = 40% do Valor Total (apenas se "Funcionario" = "Equipe")
    4. Lucro Líquido = Total - Caixa - Comissão
    ```
    
    **Exemplo com R$ 208,00 (com equipe):**
    ```
    Total: R$ 208,00
    Caixa (10%): R$ 20,80
    Comissão (40%): R$ 83,20
    Lucro: R$ 104,00
    ```
    
    **Exemplo com R$ 140,00 (sem equipe):**
    ```
    Total: R$ 140,00
    Caixa (10%): R$ 14,00
    Comissão (40%): R$ 0,00
    Lucro: R$ 126,00
    ```
    """)
    
    # Botão para corrigir valores automaticamente
    if st.button("🔄 Corrigir Valores Automaticamente", type="secondary", use_container_width=True):
        try:
            sheet = conectar_google_sheets()
            if sheet:
                ws = sheet.worksheet("Vendas")
                dados = ws.get_all_records()
                
                for i, linha in enumerate(dados, start=2):  # Começa na linha 2
                    total = float(linha.get('Total', 0))
                    
                    # Calcular valores corretos
                    fundo_caixa = total * 0.10
                    
                    # Verificar se é serviço com equipe
                    funcionario = str(linha.get('Funcionario', '')).lower()
                    if 'equipe' in funcionario:
                        valor_comissao = total * 0.40
                    else:
                        valor_comissao = 0
                    
                    lucro_liquido = total - fundo_caixa - valor_comissao
                    
                    # Atualizar células
                    ws.update_cell(i, 9, valor_comissao)   # Coluna I = Valor Comissao
                    ws.update_cell(i, 10, fundo_caixa)     # Coluna J = Fundo Caixa
                    ws.update_cell(i, 11, lucro_liquido)   # Coluna K = Lucro Liquido
                
                st.success("✅ Valores recalculados com sucesso!")
                st.cache_data.clear()
                t_sleep.sleep(2)
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")

def page_agendamento():
    """Página de agendamentos"""
    st.markdown(
        '## <i class="bi bi-calendar-check" style="color: white;"></i> Agenda Integrada',
        unsafe_allow_html=True
    )
    
    tab_new, tab_list = st.tabs(["📅 NOVO AGENDAMENTO", "📋 LISTA DE SERVIÇOS"])
    df_cat = carregar_catalogo()
    
    with tab_new:
        with st.container(border=True):
            st.markdown("### 📝 Informações do Cliente")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cliente = st.text_input("Nome do Cliente *", placeholder="João Silva")
                veiculo = st.text_input("Modelo do Veículo *", placeholder="Fiat Toro")
                placa = st.text_input("Placa *", placeholder="ABC1D23").upper()
            
            with col2:
                data_ag = st.date_input(
                    "Data do Serviço *",
                    value=date.today(),
                    format="DD/MM/YYYY",
                    min_value=date.today()
                )
                hora_ag = st.time_input(
                    "Horário *",
                    value=time(8, 0)
                ).strftime("%H:%M")
            
            st.divider()
            st.markdown("### 🚗 Categoria e Serviços")
            
            categoria = st.selectbox(
                "Categoria do Veículo *:",
                df_cat["Categoria"]
            )
            
            servicos_disponiveis = [c for c in df_cat.columns if c != "Categoria"]
            servicos_selecionados = st.multiselect(
                "Selecione os Serviços *:",
                servicos_disponiveis
            )
            
            # Cálculo em tempo real
            if servicos_selecionados:
                precos = {}
                for serv in servicos_selecionados:
                    valor = df_cat[df_cat["Categoria"] == categoria][serv].values
                    if len(valor) > 0:
                        precos[serv] = valor[0]
                
                st.markdown("### 💰 Resumo Financeiro")
                
                col_preco1, col_preco2, col_preco3 = st.columns(3)
                
                with col_preco1:
                    extra_valor = st.number_input(
                        "Valor Extra (R$)",
                        min_value=0.0,
                        value=0.0,
                        step=10.0
                    )
                
                with col_preco2:
                    desconto_valor = st.number_input(
                        "Desconto (R$)",
                        min_value=0.0,
                        value=0.0,
                        step=10.0
                    )
                
                with col_preco3:
                    executor = st.radio(
                        "Executor do Serviço:",
                        ["Eu Mesmo", "Equipe"],
                        horizontal=True
                    )
                
                # Cálculos
                subtotal = sum(precos.values())
                total_final = subtotal + extra_valor - desconto_valor
                
                # Exibir resumo
                st.markdown("---")
                col_res1, col_res2 = st.columns([2, 1])
                
                with col_res1:
                    with st.expander("📋 Detalhamento dos Valores"):
                        for serv, valor in precos.items():
                            st.write(f"• {serv}: {formatar_moeda(valor)}")
                        
                        if extra_valor > 0:
                            st.write(f"• Extra: +{formatar_moeda(extra_valor)}")
                        
                        if desconto_valor > 0:
                            st.write(f"• Desconto: -{formatar_moeda(desconto_valor)}")
                        
                        st.write(f"**Subtotal:** {formatar_moeda(subtotal)}")
                
                with col_res2:
                    st.markdown(
                        f"""
                        <div style="background: linear-gradient(135deg, #1a1a1a, #2d2d2d); 
                                 padding: 20px; border-radius: 10px; border: 2px solid #39FF14;">
                            <h3 style="color: #39FF14; margin: 0; text-align: center;">
                                TOTAL
                            </h3>
                            <h1 style="color: white; text-align: center; margin: 10px 0;">
                                {formatar_moeda(total_final)}
                            </h1>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Botão de confirmação
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("✅ CONFIRMAR AGENDAMENTO", use_container_width=True, type="primary"):
                    # Validação
                    erros = validar_agendamento(cliente, veiculo, placa)
                    
                    if erros:
                        for erro in erros:
                            st.error(erro)
                    elif not servicos_selecionados:
                        st.error("❌ Selecione pelo menos um serviço!")
                    else:
                        # Cálculo do lucro previsto
                        comissao = total_final * 0.40 if executor == "Equipe" else 0.0
                        fundo = total_final * 0.10
                        lucro_previsto = total_final - fundo - comissao
                        
                        # Preparar dados
                        dados_agendamento = {
                            "Data": data_ag.strftime("%d/%m/%Y"),
                            "Hora": hora_ag,
                            "Cliente": cliente.strip(),
                            "Veiculo": veiculo.strip(),
                            "Placa": placa.strip().upper(),
                            "Servicos": ", ".join(servicos_selecionados),
                            "Total": total_final,
                            "Executor": executor,
                            "LucroPrevisto": lucro_previsto,
                            "Categoria": categoria,
                            "Status": "Agendado"
                        }
                        
                        # Salvar
                        sucesso, mensagem = salvar_no_google("Agendamentos", dados_agendamento)
                        
                        if sucesso:
                            st.success("🎉 Agendamento confirmado com sucesso!")
                            st.balloons()
                            t_sleep.sleep(3)
                            st.rerun()
                        else:
                            st.error(f"❌ {mensagem}")
            else:
                st.info("👆 Selecione os serviços para calcular o orçamento.")
    
    with tab_list:
        st.markdown("### 📋 Serviços Agendados")
        
        df_a = carregar_dados_com_cache("Agendamentos")
        
        if df_a.empty:
            st.info("📅 Nenhum agendamento registrado.")
        else:
            for i, (_, r) in enumerate(df_a.iterrows()):
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{r.get('Veiculo', 'N/A')}** - {r.get('Cliente', 'N/A')}")
                        st.markdown(f"📅 {r.get('Data', 'N/A')} às {r.get('Hora', 'N/A')}")
                        st.markdown(f"🔧 {r.get('Servicos', 'N/A')}")
                    
                    with col2:
                        st.markdown(f"**{formatar_moeda(float(r.get('Total', 0)))}**")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if st.button("✅", key=f"concluir_{i}", help="Concluir serviço"):
                                total_val = float(r.get("Total", 0))
                                fundo = total_val * 0.10
                                comissao = total_val * 0.40 if "Equipe" in str(r.get("Executor", "")) else 0.0
                                lucro = total_val - fundo - comissao
                                
                                venda = {
                                    "Data": r.get("Data", ""),
                                    "Cliente": r.get("Cliente", ""),
                                    "Carro": r.get("Veiculo", ""),
                                    "Placa": r.get("Placa", ""),
                                    "Serviços": r.get("Servicos", ""),
                                    "Total": total_val,
                                    "Status": "Concluído",
                                    "Funcionario": r.get("Executor", ""),
                                    "Valor Comissao": comissao,
                                    "Fundo Caixa": fundo,
                                    "Lucro Liquido": lucro,
                                    "Status Comissao": "Pendente",
                                    "Categoria": r.get("Categoria", "")
                                }
                                
                                salvar_no_google("Vendas", venda)
                                excluir_agendamento(i)
                                st.success("✅ Serviço concluído!")
                                t_sleep.sleep(2)
                                st.rerun()
                        
                        with col_btn2:
                            if st.button("🗑️", key=f"excluir_{i}", help="Excluir agendamento"):
                                if excluir_agendamento(i):
                                    st.success("🗑️ Agendamento excluído!")
                                    t_sleep.sleep(2)
                                    st.rerun()

def page_despesas():
    """Página de gestão de despesas - CORRIGIDA"""
    st.markdown(
        '## <i class="bi bi-receipt" style="color: #D90429;"></i> Controle de Despesas',
        unsafe_allow_html=True
    )
    
    with st.form("form_despesa", clear_on_submit=True):
        st.markdown("### 📄 Nova Despesa")
        
        col1, col2 = st.columns(2)
        
        with col1:
            data_desp = st.date_input(
                "Data da Despesa *",
                value=date.today(),
                format="DD/MM/YYYY"
            )
            descricao = st.text_input(
                "Descrição *",
                placeholder="Ex: Compra de produtos de limpeza"
            )
        
        with col2:
            categoria = st.selectbox(
                "Categoria *",
                ["Insumos", "Manutenção", "Marketing", "Salários", 
                 "Aluguel", "Energia/Água", "Outros"]
            )
            # CORREÇÃO CRÍTICA: value deve ser >= min_value
            valor = st.number_input(
                "Valor (R$) *",
                min_value=0.01,
                value=0.01,  # CORRIGIDO: valor inicial 0.01
                step=10.0
            )
        
        observacoes = st.text_area(
            "Observações",
            placeholder="Detalhes adicionais sobre a despesa...",
            height=100
        )
        
        # CORREÇÃO: Botão de submit dentro do form
        submitted = st.form_submit_button(
            "💾 Salvar Despesa",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not descricao.strip():
                st.error("❌ Descrição é obrigatória!")
            elif valor <= 0:
                st.error("❌ Valor deve ser maior que zero!")
            else:
                dados_despesa = {
                    "Data": data_desp.strftime("%d/%m/%Y"),
                    "Descricao": descricao.strip(),
                    "Categoria": categoria,
                    "Valor": valor,
                    "Observacoes": observacoes.strip(),
                    "Status": "Pago"
                }
                
                sucesso, mensagem = salvar_no_google("Despesas", dados_despesa)
                
                if sucesso:
                    st.success("✅ Despesa registrada com sucesso!")
                    st.balloons()
                    t_sleep.sleep(2)
                    st.rerun()
                else:
                    st.error(f"❌ {mensagem}")
    
    st.write("---")
    
    # Lista de despesas recentes
    st.markdown("### 📋 Despesas Recentes")
    
    df_d = carregar_dados_com_cache("Despesas")
    
    if df_d.empty:
        st.info("📊 Nenhuma despesa registrada ainda.")
    else:
        # Mostrar últimas 10 despesas
        df_recentes = df_d.sort_values('Data_dt', ascending=False).head(10)
        
        for _, r in df_recentes.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{r.get('Descricao', 'N/A')}**")
                    st.markdown(f"📅 {r.get('Data', 'N/A')} | 🏷️ {r.get('Categoria', 'N/A')}")
                    if r.get('Observacoes'):
                        st.markdown(f"📝 {r.get('Observacoes')}")
                
                with col2:
                    st.markdown(f"**{formatar_moeda(float(r.get('Valor', 0)))}**")

def page_historico():
    """Página de histórico e garagem - COMPLETAMENTE CORRIGIDA"""
    st.markdown(
        '## <i class="bi bi-clock-history" style="color: #FFC107;"></i> Garagem & Histórico',
        unsafe_allow_html=True
    )
    
    df = carregar_vendas_corrigida()
    
    if df.empty:
        st.info("🚗 Nenhum serviço registrado ainda.")
        return
    
    # Filtro de busca
    busca = st.text_input(
        "🔍 Buscar (Cliente/Veículo/Placa)",
        placeholder="Digite para buscar..."
    ).strip().lower()
    
    # Aplicar filtro
    if busca:
        df_filtrado = df[
            df.apply(
                lambda row: busca in str(row).lower(),
                axis=1
            )
        ]
    else:
        df_filtrado = df
    
    # Ordenar por data mais recente
    if 'Data_dt' in df_filtrado.columns:
        df_filtrado = df_filtrado.sort_values('Data_dt', ascending=False)
    
    # Estatísticas
    total_registros = len(df_filtrado)
    valor_total = df_filtrado["Total"].sum() if total_registros > 0 else 0
    
    col_stat1, col_stat2 = st.columns(2)
    
    with col_stat1:
        st.metric("📊 Total de Serviços", total_registros)
    
    with col_stat2:
        st.metric("💰 Valor Total", formatar_moeda(valor_total))
    
    st.write("---")
    
    # Exibir histórico - FORMA CORRIGIDA SEM HTML MAL FORMADO
    if total_registros == 0:
        st.info("🔍 Nenhum resultado encontrado.")
    else:
        for _, r in df_filtrado.iterrows():
            # Usar containers do Streamlit em vez de HTML
            with st.container(border=True):
                # Cabeçalho
                col_head1, col_head2 = st.columns([3, 1])
                
                with col_head1:
                    st.markdown(f"### {r.get('Carro', 'N/A')}")
                    st.markdown(f"**Cliente:** {r.get('Cliente', 'N/A')} | **Placa:** {r.get('Placa', 'N/A')}")
                    st.markdown(f"**Data:** {r.get('Data', 'N/A')} | **Status:** {r.get('Status', 'N/A')}")
                
                with col_head2:
                    st.markdown(f"# {formatar_moeda(float(r.get('Total', 0)))}")
                
                # Serviços
                st.markdown(f"**Serviços:** {r.get('Serviços', 'N/A')}")
                
                # Detalhes financeiros
                col_fin1, col_fin2, col_fin3 = st.columns(3)
                
                with col_fin1:
                    st.metric(
                        "Comissão",
                        formatar_moeda(float(r.get("Valor Comissao", 0)))
                    )
                
                with col_fin2:
                    st.metric(
                        "Caixa",
                        formatar_moeda(float(r.get("Fundo Caixa", 0)))
                    )
                
                with col_fin3:
                    st.metric(
                        "Lucro",
                        formatar_moeda(float(r.get("Lucro Liquido", 0)))
                    )
                
                # Informações adicionais
                st.caption(f"Executor: {r.get('Funcionario', 'N/A')} | Status Comissão: {r.get('Status Comissao', 'N/A')}")

# ==============================================================================
# --- 7. ROTEADOR DE PÁGINAS ---
# ==============================================================================

if menu_selecionado == "DASHBOARD":
    page_dashboard()
elif menu_selecionado == "AGENDA":
    page_agendamento()
elif menu_selecionado == "FINANCEIRO":
    page_financeiro()
elif menu_selecionado == "DESPESAS":
    page_despesas()
elif menu_selecionado == "HISTÓRICO":
    page_historico()

# ==============================================================================
# --- 8. RODAPÉ ---
# ==============================================================================

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown(
    '''
    <div class="footer">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                💎 <b>JM Detail System PRO</b> | Versão 14.1
            </div>
            <div>
                🚗 Sistema de Gestão Automotiva
            </div>
            <div>
                📞 (75) 99830-3753 | 📍 Tucano - BA
            </div>
        </div>
        <div style="margin-top: 5px; font-size: 10px; color: #444;">
            Desenvolvido por <b>Jairan Jesus Matos</b> © 2026 | 
            Última atualização: {}
        </div>
    </div>
    '''.format(datetime.now().strftime("%d/%m/%Y %H:%M")),
    unsafe_allow_html=True
)

# ==============================================================================
# --- 9. INICIALIZAÇÃO DO SISTEMA ---
# ==============================================================================

# Criar diretórios necessários na primeira execução
if 'system_initialized' not in st.session_state:
    os.makedirs("logs", exist_ok=True)
    st.session_state.system_initialized = True
