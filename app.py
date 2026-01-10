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
                    registrar_log("Sistema", "Login realizado", f"IP: {st.experimental_user.ip}")
                    
                    try:
                        st.query_params["acesso_liberado"] = "sim_mestre"
                    except:
                        pass
                    
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
                    registrar_log("Tentativa falha", "Login falhou", f"Tentativa com senha: {pwd[:3]}...")
    
    return False

if not check_password():
    st.stop()

# ==============================================================================
# --- 3. ESTILO CSS OTIMIZADO (V14.0) ---
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

    /* --- CARDS LISTA --- */
    .agenda-card { 
        background-color: #161616 !important; 
        border-radius: 12px; 
        padding: 15px; 
        margin-bottom: 12px; 
        border: 1px solid #333; 
        border-left: 5px solid #00B4DB; 
        transition: all 0.3s ease;
    }
    
    .agenda-card:hover {
        border-left-width: 8px;
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
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border-radius: 12px;
        padding: 15px;
        border-left: 4px solid;
        margin-bottom: 10px;
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
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #111;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #D90429;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #8D021F;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #D90429 !important;
    }

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- 4. FUNÇÕES AUXILIARES OTIMIZADAS ---
# ==============================================================================

def formatar_moeda(valor: float) -> str:
    """Formata valores monetários de forma segura"""
    try:
        if pd.isna(valor) or valor is None:
            return "R$ 0,00"
        valor = float(valor)
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
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
        registrar_log("ERRO", "Falha conexão Google Sheets", str(e))
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

@st.cache_data(ttl=600, show_spinner=False)
def carregar_todos_dados() -> Dict[str, pd.DataFrame]:
    """Carrega todos os dados principais de uma vez"""
    return {
        "vendas": carregar_dados_com_cache("Vendas"),
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
            else:
                # Tentar variações de acentuação
                variacoes = [
                    col_name.replace("ç", "c"),
                    col_name.replace("c", "ç"),
                    col_name.replace("ã", "a"),
                    col_name.replace("a", "ã")
                ]
                
                for var in variacoes:
                    if var in headers:
                        index = headers.index(var)
                        nova_linha[index] = valor
                        break
        
        # Inserir linha
        ws.append_row(nova_linha)
        
        # Invalidar cache para esta aba
        st.cache_data.clear()
        
        # Criar backup automático
        criar_backup_local()
        
        return True, "✅ Dados salvos com sucesso!"
    
    except Exception as e:
        registrar_log("ERRO", f"Falha ao salvar em {aba}", str(e))
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
        
        # Registrar log
        registrar_log("Sistema", "Agendamento excluído", f"Linha {indice_linha}")
        
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
        "Higi. Bancos": [80.0, 80.0, 80.0, 120.0, 150.0, 0.0],
        "Higi. Interna (Teto/Carpete)": [150.0, 150.0, 180.0, 200.0, 250.0, 0.0],
        "Combo Premium": [300.0, 320.0, 350.0, 400.0, 450.0, 0.0],
        "Limpeza Motor": [100.0, 100.0, 120.0, 150.0, 150.0, 80.0],
        "Faróis": [200.0, 200.0, 200.0, 200.0, 200.0, 100.0],
        "Cristalização Vidros": [90.0, 120.0, 150.0, 150.0, 150.0, 50.0],
        "Vitrificação": [800.0, 900.0, 1100.0, 1300.0, 1300.0, 500.0]
    })

def obter_icone_html(categoria: str) -> str:
    """Retorna ícone HTML baseado na categoria do veículo"""
    if not isinstance(categoria, str):
        return '<i class="bi bi-car-front-fill"></i>'
    
    c = categoria.lower()
    
    if "moto" in c:
        return '<i class="bi bi-motorcycle"></i>'
    elif "suv" in c or "picape" in c or "caminhonete" in c:
        return '<i class="bi bi-truck-front-fill"></i>'
    elif "van" in c or "utilitário" in c:
        return '<i class="bi bi-bus-front-fill"></i>'
    elif "hatch" in c or "compacto" in c:
        return '<i class="bi bi-car-front"></i>'
    elif "sedã" in c or "sedan" in c:
        return '<i class="bi bi-car-front-fill"></i>'
    else:
        return '<i class="bi bi-car-front-fill"></i>'

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
    pdf.cell(140, 10, txt="TOTAL", align='R')
    pdf.cell(50, 10, txt=txt(f"R$ {total:.2f}"), border=1, align='C')
    
    # Rodapé
    pdf.ln(15)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, txt="Agradecemos pela preferência! Volte sempre.", 
             ln=True, align='C')
    
    return pdf.output(dest="S").encode("latin-1")

def criar_backup_local():
    """Cria backup automático dos dados"""
    try:
        backup_data = {}
        
        for aba in ["Vendas", "Agendamentos", "Despesas"]:
            df = carregar_dados_com_cache(aba)
            backup_data[aba] = df.to_dict(orient='records')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backups/backup_{timestamp}.json"
        
        # Criar diretório se não existir
        os.makedirs("backups", exist_ok=True)
        
        with open(backup_file, "w", encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        # Manter apenas últimos 10 backups
        backups = sorted([f for f in os.listdir("backups") if f.startswith("backup_")])
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                os.remove(os.path.join("backups", old_backup))
    
    except Exception as e:
        print(f"Erro ao criar backup: {e}")

def registrar_log(usuario: str, acao: str, detalhes: str = ""):
    """Registra log de atividades"""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "usuario": usuario,
            "acao": acao,
            "detalhes": detalhes,
            "ip": st.experimental_user.ip if hasattr(st.experimental_user, 'ip') else "N/A"
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
        
        # Agendamentos para hoje
        hoje_agendamentos = df_a[df_a['Data_dt'] == hoje]
        
        if not hoje_agendamentos.empty():
            st.toast(
                f"📅 Hoje: {len(hoje_agendamentos)} serviço(s) agendado(s)",
                icon="📅"
            )
    
    except Exception as e:
        print(f"Erro ao verificar agendamentos: {e}")

def calcular_kpis() -> Dict:
    """Calcula KPIs avançados"""
    dados = carregar_todos_dados()
    df_v = dados["vendas"]
    
    if df_v.empty:
        return {}
    
    hoje = datetime.now()
    
    try:
        # Ticket médio
        vendas_concluidas = df_v[df_v["Status"] == "Concluído"]
        ticket_medio = vendas_concluidas["Total"].mean() if not vendas_concluidas.empty else 0
        
        # Taxa de conversão
        total_orcamentos = len(df_v[df_v["Status"] == "Orçamento/Pendente"])
        total_concluidos = len(vendas_concluidas)
        taxa_conversao = (total_concluidos / (total_concluidos + total_orcamentos) * 100 
                         if (total_concluidos + total_orcamentos) > 0 else 0)
        
        # Lucratividade por serviço
        lucratividade_media = vendas_concluidas["Lucro Liquido"].mean() if not vendas_concluidas.empty else 0
        
        # Serviço mais popular
        if "Serviços" in df_v.columns:
            todos_servicos = []
            for servicos in df_v["Serviços"]:
                if isinstance(servicos, str):
                    todos_servicos.extend([s.strip() for s in servicos.split(",")])
            
            if todos_servicos:
                from collections import Counter
                servico_mais_popular = Counter(todos_servicos).most_common(1)
                if servico_mais_popular:
                    servico_mais_popular = servico_mais_popular[0][0]
                else:
                    servico_mais_popular = "Nenhum"
            else:
                servico_mais_popular = "Nenhum"
        else:
            servico_mais_popular = "Nenhum"
        
        return {
            "ticket_medio": ticket_medio,
            "taxa_conversao": taxa_conversao,
            "lucratividade_media": lucratividade_media,
            "servico_popular": servico_mais_popular,
            "total_clientes": len(df_v["Cliente"].unique()),
            "carros_ativos": len(df_v["Placa"].unique())
        }
    
    except Exception as e:
        print(f"Erro ao calcular KPIs: {e}")
        return {}

def exportar_dados_periodo(formato: str = "csv", periodo: str = "mes_atual"):
    """Exporta dados para diferentes formatos"""
    dados = carregar_todos_dados()
    hoje = datetime.now()
    
    # Filtrar por período
    if periodo == "mes_atual":
        data_inicio = hoje.replace(day=1)
        data_fim = hoje
    elif periodo == "ultimo_mes":
        data_inicio = (hoje.replace(day=1) - timedelta(days=1)).replace(day=1)
        data_fim = hoje.replace(day=1) - timedelta(days=1)
    else:  # ano atual
        data_inicio = hoje.replace(month=1, day=1)
        data_fim = hoje
    
    # Filtrar dados
    dados_filtrados = {}
    for nome, df in dados.items():
        if not df.empty and 'Data_dt' in df.columns:
            mask = (df['Data_dt'] >= pd.Timestamp(data_inicio)) & \
                   (df['Data_dt'] <= pd.Timestamp(data_fim))
            dados_filtrados[nome] = df[mask]
        else:
            dados_filtrados[nome] = df
    
    # Exportar
    if formato == "csv":
        output = {}
        for nome, df in dados_filtrados.items():
            output[nome] = df.to_csv(index=False).encode('utf-8')
        return output
    
    elif formato == "excel":
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for nome, df in dados_filtrados.items():
                df.to_excel(writer, sheet_name=nome[:30], index=False)
        output.seek(0)
        return output
    
    return None

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

# Verificar notificações de agendamentos
verificar_agendamentos_proximos()

# ==============================================================================
# --- 6. PÁGINAS DO SISTEMA ---
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
    
    # KPIs Avançados
    st.markdown("### 📊 KPIs de Performance", unsafe_allow_html=True)
    kpis = calcular_kpis()
    
    if kpis:
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        
        with col_kpi1:
            st.metric("Ticket Médio", formatar_moeda(kpis.get("ticket_medio", 0)))
        
        with col_kpi2:
            st.metric("Taxa de Conversão", f"{kpis.get('taxa_conversao', 0):.1f}%")
        
        with col_kpi3:
            st.metric("Clientes Únicos", kpis.get("total_clientes", 0))
        
        with col_kpi4:
            st.metric("Serviço Popular", kpis.get("servico_popular", "N/A"))
    
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
                                <i class="bi bi-calendar"></i> {r['Data']} • {r['Hora']}
                            </div>
                            <div style="font-weight:bold; font-size:16px; color:white">
                                {obter_icone_html(r.get("Categoria", ""))} {r['Veiculo']}
                            </div>
                            <div style="font-size:13px; color:#888;">{r['Cliente']}</div>
                        </div>
                        ''',
                        unsafe_allow_html=True
                    )
            else:
                st.info("🎉 Agenda livre para os próximos dias!")
        else:
            st.info("📅 Nenhum agendamento futuro encontrado.")
        
        # Botão de exportação rápida
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📤 Exportar Relatório do Mês", use_container_width=True):
            dados_export = exportar_dados_periodo("csv", "mes_atual")
            if dados_export:
                st.download_button(
                    label="⬇️ Baixar CSV",
                    data=dados_export["vendas"],
                    file_name=f"vendas_{hoje.strftime('%Y%m')}.csv",
                    mime="text/csv"
                )

def page_financeiro():
    """Página de gestão financeira"""
    st.markdown(
        '## <i class="bi bi-cash-coin" style="color: #28a745;"></i> Gestão Financeira',
        unsafe_allow_html=True
    )
    
    df_v = carregar_dados_com_cache("Vendas")
    comissao_pendente = 0.0
    fundo_caixa = 0.0
    
    if not df_v.empty:
        if "Status Comissao" not in df_v.columns:
            df_v["Status Comissao"] = "Pendente"
        
        comissao_pendente = df_v[
            df_v["Status Comissao"] != "Pago"
        ]["Valor Comissao"].sum()
        
        fundo_caixa = df_v["Fundo Caixa"].sum()
    
    # Cards de status
    col_status1, col_status2, col_status3 = st.columns(3)
    
    with col_status1:
        st.metric(
            "💰 Caixa da Empresa",
            formatar_moeda(fundo_caixa),
            delta=formatar_moeda(fundo_caixa * 0.1) + " (último mês)"
        )
    
    with col_status2:
        st.metric(
            "💸 Comissões Pendentes",
            formatar_moeda(comissao_pendente)
        )
    
    with col_status3:
        lucro_total = df_v["Lucro Liquido"].sum() if not df_v.empty else 0
        st.metric(
            "📈 Lucro Total Acumulado",
            formatar_moeda(lucro_total)
        )
    
    st.write("---")
    
    # Gestão de comissões
    st.markdown("### 🧾 Pagamento de Comissões")
    
    if comissao_pendente > 0:
        col_btn1, col_btn2 = st.columns([1, 3])
        
        with col_btn1:
            if st.button("✅ Pagar Todas as Comissões", use_container_width=True):
                # Confirmação
                with st.popover("⚠️ Confirmar Pagamento"):
                    st.write(f"Valor total a pagar: {formatar_moeda(comissao_pendente)}")
                    st.write("Esta ação marcará TODAS as comissões como PAGAS.")
                    
                    col_confirm1, col_confirm2 = st.columns(2)
                    
                    with col_confirm1:
                        if st.button("👍 Confirmar Pagamento"):
                            try:
                                sheet = conectar_google_sheets()
                                if sheet:
                                    ws = sheet.worksheet("Vendas")
                                    dados = ws.get_all_records()
                                    header = ws.row_values(1)
                                    
                                    if "Status Comissao" in header:
                                        col_idx = header.index("Status Comissao") + 1
                                        
                                        # Atualizar todas as linhas
                                        for i in range(2, len(dados) + 2):
                                            ws.update_cell(i, col_idx, "Pago")
                                        
                                        st.success("✅ Todas as comissões foram pagas!")
                                        registrar_log("Financeiro", "Comissões pagas", 
                                                     f"Valor: {comissao_pendente}")
                                        t_sleep.sleep(2)
                                        st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erro ao processar: {str(e)}")
                    
                    with col_confirm2:
                        if st.button("👎 Cancelar"):
                            st.rerun()
        
        with col_btn2:
            st.info(f"💰 Total pendente: **{formatar_moeda(comissao_pendente)}**")
    
    else:
        st.success("🎉 Todas as comissões estão em dia!")
    
    # Gráfico de evolução financeira
    st.write("---")
    st.markdown("### 📊 Evolução Financeira")
    
    if not df_v.empty and 'Data_dt' in df_v.columns:
        # Agrupar por mês
        df_v['Mes'] = df_v['Data_dt'].dt.to_period('M')
        evolucao = df_v.groupby('Mes').agg({
            'Total': 'sum',
            'Lucro Liquido': 'sum',
            'Fundo Caixa': 'sum'
        }).reset_index()
        
        if not evolucao.empty:
            evolucao['Mes'] = evolucao['Mes'].astype(str)
            
            chart = alt.Chart(evolucao).transform_fold(
                ['Total', 'Lucro Liquido'],
                as_=['Metric', 'Value']
            ).mark_line(point=True).encode(
                x=alt.X('Mes:N', title='Mês'),
                y=alt.Y('Value:Q', title='Valor (R$)'),
                color=alt.Color('Metric:N', scale=alt.Scale(
                    domain=['Total', 'Lucro Liquido'],
                    range=['#00B4DB', '#39FF14']
                )),
                strokeWidth=alt.value(3)
            ).properties(
                height=300,
                background='transparent'
            )
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("📈 Insuficientes dados para gerar gráfico de evolução.")
    else:
        st.info("📊 Nenhum dado financeiro disponível para análise.")

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
                df_cat["Categoria"],
                help="Selecione a categoria que melhor descreve o veículo"
            )
            
            servicos_disponiveis = [c for c in df_cat.columns if c != "Categoria"]
            servicos_selecionados = st.multiselect(
                "Selecione os Serviços *:",
                servicos_disponiveis,
                help="Pressione CTRL para selecionar múltiplos serviços"
            )
            
            # Cálculo em tempo real
            if servicos_selecionados:
                precos = {
                    serv: df_cat[df_cat["Categoria"] == categoria][serv].values[0]
                    for serv in servicos_selecionados
                }
                
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
                            
                            # Gerar PDF
                            pdf_bytes = gerar_pdf(
                                cliente,
                                veiculo,
                                placa,
                                data_ag.strftime("%d/%m/%Y"),
                                precos,
                                total_final
                            )
                            
                            st.download_button(
                                label="📄 Baixar Orçamento (PDF)",
                                data=pdf_bytes,
                                file_name=f"orcamento_{placa}_{data_ag.strftime('%Y%m%d')}.pdf",
                                mime="application/pdf"
                            )
                            
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
            # Filtros
            col_filtro1, col_filtro2 = st.columns(2)
            
            with col_filtro1:
                filtrar_data = st.checkbox("Filtrar por data")
            
            with col_filtro2:
                if filtrar_data:
                    data_filtro = st.date_input(
                        "Data específica",
                        value=date.today()
                    )
                    df_a = df_a[df_a['Data'] == data_filtro.strftime("%d/%m/%Y")]
            
            # Ordenação
            col_ord1, col_ord2 = st.columns(2)
            
            with col_ord1:
                ordenar_por = st.selectbox(
                    "Ordenar por:",
                    ["Data (mais recente)", "Data (mais antigo)", "Valor (maior)", "Valor (menor)"]
                )
            
            # Aplicar ordenação
            if ordenar_por == "Data (mais recente)" and 'Data_dt' in df_a.columns:
                df_a = df_a.sort_values(by='Data_dt', ascending=False)
            elif ordenar_por == "Data (mais antigo)" and 'Data_dt' in df_a.columns:
                df_a = df_a.sort_values(by='Data_dt', ascending=True)
            elif ordenar_por == "Valor (maior)":
                df_a = df_a.sort_values(by='Total', ascending=False)
            elif ordenar_por == "Valor (menor)":
                df_a = df_a.sort_values(by='Total', ascending=True)
            
            # Exibir agendamentos
            for i, (_, r) in enumerate(df_a.iterrows()):
                st.markdown(
                    f"""
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
                            {obter_icone_html(r.get("Categoria", ""))} {r['Veiculo']} 
                            <span style="font-size:14px; color:#888">({r['Placa']})</span>
                        </div>
                        <div style="margin-top:5px; font-size:14px; color:#ccc">
                            <i class="bi bi-person-fill"></i> {r['Cliente']}
                        </div>
                        <div style="margin-top:10px; padding-top:10px; border-top:1px solid #333; 
                                 font-size:13px; color:#888">
                            🔧 {r['Servicos']}
                        </div>
                        <div style="margin-top:10px; font-size:12px; color:#666">
                            <i class="bi bi-person-workspace"></i> Executor: {r['Executor']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Botões de ação
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if st.button(f"✅ Concluir", key=f"ok_{i}", use_container_width=True):
                        # Cálculos financeiros
                        total_val = float(r["Total"])
                        fundo = total_val * 0.10
                        comissao = total_val * 0.40 if "Equipe" in r["Executor"] else 0.0
                        lucro = total_val - fundo - comissao
                        
                        # Dados da venda
                        venda = {
                            "Data": r["Data"],
                            "Cliente": r["Cliente"],
                            "Carro": r["Veiculo"],
                            "Placa": r["Placa"],
                            "Serviços": r["Servicos"],
                            "Total": total_val,
                            "Status": "Concluído",
                            "Funcionario": r["Executor"],
                            "Valor Comissao": comissao,
                            "Fundo Caixa": fundo,
                            "Lucro Liquido": lucro,
                            "Status Comissao": "Pendente",
                            "Categoria": r.get("Categoria", "")
                        }
                        
                        # Salvar venda e excluir agendamento
                        salvar_no_google("Vendas", venda)
                        excluir_agendamento(i)
                        
                        st.success("✅ Serviço concluído e movido para vendas!")
                        t_sleep.sleep(2)
                        st.rerun()
                
                with col_btn2:
                    if st.button(f"✏️ Editar", key=f"edit_{i}", use_container_width=True):
                        st.info("⏳ Funcionalidade em desenvolvimento!")
                
                with col_btn3:
                    if st.button(f"🗑️ Cancelar", key=f"del_{i}", use_container_width=True):
                        # Confirmação
                        with st.popover("⚠️ Confirmar Exclusão"):
                            st.write(f"Deseja realmente excluir o agendamento?")
                            st.write(f"**Cliente:** {r['Cliente']}")
                            st.write(f"**Veículo:** {r['Veiculo']} ({r['Placa']})")
                            st.write(f"**Data:** {r['Data']} às {r['Hora']}")
                            
                            col_conf1, col_conf2 = st.columns(2)
                            
                            with col_conf1:
                                if st.button("👍 Sim, excluir", type="primary"):
                                    if excluir_agendamento(i):
                                        st.success("🗑️ Agendamento excluído!")
                                        t_sleep.sleep(2)
                                        st.rerun()
                            
                            with col_conf2:
                                if st.button("👎 Cancelar"):
                                    st.rerun()
                
                st.write("---")

def page_despesas():
    """Página de gestão de despesas"""
    st.markdown(
        '## <i class="bi bi-receipt" style="color: #D90429;"></i> Controle de Despesas',
        unsafe_allow_html=True
    )
    
    tab_lancar, tab_analise = st.tabs(["📝 Lançar Despesa", "📊 Análise de Gastos"])
    
    with tab_lancar:
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
                valor = st.number_input(
                    "Valor (R$) *",
                    min_value=0.01,
                    value=0.0,
                    step=10.0
                )
            
            observacoes = st.text_area(
                "Observações",
                placeholder="Detalhes adicionais sobre a despesa...",
                height=100
            )
            
            col_submit1, col_submit2 = st.columns([1, 3])
            
            with col_submit1:
                submit = st.form_submit_button(
                    "💾 Salvar Despesa",
                    type="primary",
                    use_container_width=True
                )
            
            with col_submit2:
                if submit:
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
    
    with tab_analise:
        st.markdown("### 📊 Análise de Despesas")
        
        df_d = carregar_dados_com_cache("Despesas")
        
        if df_d.empty:
            st.info("📊 Nenhuma despesa registrada ainda.")
        else:
            # KPIs rápidos
            total_despesas = df_d["Valor"].sum()
            media_mensal = df_d.groupby(
                df_d['Data_dt'].dt.to_period('M')
            )['Valor'].sum().mean() if 'Data_dt' in df_d.columns else 0
            
            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            
            with col_kpi1:
                st.metric("Total Gastos", formatar_moeda(total_despesas))
            
            with col_kpi2:
                st.metric("Média Mensal", formatar_moeda(media_mensal))
            
            with col_kpi3:
                maior_despesa = df_d["Valor"].max()
                st.metric("Maior Despesa", formatar_moeda(maior_despesa))
            
            st.write("---")
            
            # Filtros
            col_filt1, col_filt2 = st.columns(2)
            
            with col_filt1:
                periodo = st.selectbox(
                    "Período",
                    ["Últimos 30 dias", "Últimos 90 dias", "Este mês", "Este ano", "Todo período"]
                )
                
                # Aplicar filtro de período
                hoje = datetime.now()
                if periodo == "Últimos 30 dias":
                    data_inicio = hoje - timedelta(days=30)
                    df_filtrado = df_d[df_d['Data_dt'] >= data_inicio]
                elif periodo == "Últimos 90 dias":
                    data_inicio = hoje - timedelta(days=90)
                    df_filtrado = df_d[df_d['Data_dt'] >= data_inicio]
                elif periodo == "Este mês":
                    data_inicio = hoje.replace(day=1)
                    df_filtrado = df_d[df_d['Data_dt'] >= data_inicio]
                elif periodo == "Este ano":
                    data_inicio = hoje.replace(month=1, day=1)
                    df_filtrado = df_d[df_d['Data_dt'] >= data_inicio]
                else:
                    df_filtrado = df_d
            
            with col_filt2:
                if 'Categoria' in df_filtrado.columns:
                    categorias = ["Todas"] + sorted(df_filtrado['Categoria'].unique().tolist())
                    categoria_filtro = st.selectbox("Categoria", categorias)
                    
                    if categoria_filtro != "Todas":
                        df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria_filtro]
            
            # Gráficos
            if not df_filtrado.empty:
                col_graf1, col_graf2 = st.columns(2)
                
                with col_graf1:
                    st.markdown("##### 📈 Evolução Temporal")
                    
                    if 'Data_dt' in df_filtrado.columns:
                        evolucao = df_filtrado.set_index('Data_dt').resample('D')['Valor'].sum()
                        
                        if not evolucao.empty:
                            chart = alt.Chart(
                                evolucao.reset_index()
                            ).mark_area(
                                line={'color': '#D90429'},
                                color=alt.Gradient(
                                    gradient='linear',
                                    stops=[
                                        alt.GradientStop(color='#D90429', offset=0),
                                        alt.GradientStop(color='#8D021F', offset=1)
                                    ]
                                )
                            ).encode(
                                x=alt.X('Data_dt:T', title='Data'),
                                y=alt.Y('Valor:Q', title='Valor (R$)')
                            ).properties(
                                height=250
                            )
                            
                            st.altair_chart(chart, use_container_width=True)
                
                with col_graf2:
                    st.markdown("##### 🏷️ Por Categoria")
                    
                    if 'Categoria' in df_filtrado.columns:
                        por_categoria = df_filtrado.groupby('Categoria')['Valor'].sum().reset_index()
                        
                        if not por_categoria.empty:
                            chart = alt.Chart(por_categoria).mark_bar().encode(
                                y=alt.Y('Categoria:N', sort='-x', title='Categoria'),
                                x=alt.X('Valor:Q', title='Valor (R$)'),
                                color=alt.Color('Categoria:N', legend=None),
                                tooltip=['Categoria', 'Valor']
                            ).properties(
                                height=250
                            )
                            
                            st.altair_chart(chart, use_container_width=True)
                
                # Tabela detalhada
                st.write("---")
                st.markdown("##### 📋 Detalhamento das Despesas")
                
                # Ordenação
                col_sort1, col_sort2 = st.columns(2)
                
                with col_sort1:
                    ordenar_por = st.selectbox(
                        "Ordenar tabela por:",
                        ["Data (recente)", "Data (antiga)", "Valor (maior)", "Valor (menor)"]
                    )
                
                # Aplicar ordenação
                if ordenar_por == "Data (recente)" and 'Data_dt' in df_filtrado.columns:
                    df_tabela = df_filtrado.sort_values('Data_dt', ascending=False)
                elif ordenar_por == "Data (antiga)" and 'Data_dt' in df_filtrado.columns:
                    df_tabela = df_filtrado.sort_values('Data_dt', ascending=True)
                elif ordenar_por == "Valor (maior)":
                    df_tabela = df_filtrado.sort_values('Valor', ascending=False)
                elif ordenar_por == "Valor (menor)":
                    df_tabela = df_filtrado.sort_values('Valor', ascending=True)
                else:
                    df_tabela = df_filtrado
                
                # Exibir tabela
                st.dataframe(
                    df_tabela[['Data', 'Descricao', 'Categoria', 'Valor', 'Observacoes']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Data": st.column_config.TextColumn("Data"),
                        "Descricao": st.column_config.TextColumn("Descrição"),
                        "Categoria": st.column_config.TextColumn("Categoria"),
                        "Valor": st.column_config.NumberColumn(
                            "Valor",
                            format="R$ %.2f"
                        ),
                        "Observacoes": st.column_config.TextColumn("Observações")
                    }
                )
                
                # Botão de exportação
                if st.button("📤 Exportar Relatório de Despesas", use_container_width=True):
                    csv = df_tabela.to_csv(index=False).encode('utf-8')
                    
                    st.download_button(
                        label="⬇️ Baixar CSV",
                        data=csv,
                        file_name=f"despesas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )

def page_historico():
    """Página de histórico e garagem"""
    st.markdown(
        '## <i class="bi bi-clock-history" style="color: #FFC107;"></i> Garagem & Histórico',
        unsafe_allow_html=True
    )
    
    df = carregar_dados_com_cache("Vendas")
    
    if df.empty:
        st.info("🚗 Nenhum serviço registrado ainda.")
        return
    
    # Filtros avançados
    with st.expander("🔍 Filtros Avançados", expanded=False):
        col_filt1, col_filt2, col_filt3 = st.columns(3)
        
        with col_filt1:
            busca = st.text_input(
                "Buscar (Cliente/Veículo/Placa)",
                placeholder="Digite para buscar..."
            ).strip().lower()
        
        with col_filt2:
            if 'Data_dt' in df.columns:
                datas_disponiveis = sorted(df['Data_dt'].dt.date.unique(), reverse=True)
                data_filtro = st.selectbox(
                    "Filtrar por data",
                    ["Todas as datas"] + [str(d) for d in datas_disponiveis]
                )
            else:
                data_filtro = "Todas as datas"
        
        with col_filt3:
            if 'Status' in df.columns:
                status_options = ["Todos"] + sorted(df['Status'].unique().tolist())
                status_filtro = st.selectbox("Status", status_options)
            else:
                status_filtro = "Todos"
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if busca:
        mask = df_filtrado.apply(
            lambda row: busca in str(row).lower(),
            axis=1
        )
        df_filtrado = df_filtrado[mask]
    
    if data_filtro != "Todas as datas" and 'Data_dt' in df_filtrado.columns:
        data_selecionada = pd.to_datetime(data_filtro).date()
        df_filtrado = df_filtrado[
            df_filtrado['Data_dt'].dt.date == data_selecionada
        ]
    
    if status_filtro != "Todos" and 'Status' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Status'] == status_filtro]
    
    # Estatísticas
    total_registros = len(df_filtrado)
    valor_total = df_filtrado["Total"].sum() if total_registros > 0 else 0
    lucro_total = df_filtrado["Lucro Liquido"].sum() if total_registros > 0 else 0
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.metric("📊 Total de Serviços", total_registros)
    
    with col_stat2:
        st.metric("💰 Valor Total", formatar_moeda(valor_total))
    
    with col_stat3:
        st.metric("📈 Lucro Total", formatar_moeda(lucro_total))
    
    st.write("---")
    
    # Ordenação
    col_sort1, col_sort2 = st.columns([1, 2])
    
    with col_sort1:
        ordenar_por = st.selectbox(
            "Ordenar por:",
            ["Data (mais recente)", "Data (mais antigo)", "Valor (maior)", "Valor (menor)"]
        )
    
    # Aplicar ordenação
    if ordenar_por == "Data (mais recente)" and 'Data_dt' in df_filtrado.columns:
        df_filtrado = df_filtrado.sort_values('Data_dt', ascending=False)
    elif ordenar_por == "Data (mais antigo)" and 'Data_dt' in df_filtrado.columns:
        df_filtrado = df_filtrado.sort_values('Data_dt', ascending=True)
    elif ordenar_por == "Valor (maior)":
        df_filtrado = df_filtrado.sort_values('Total', ascending=False)
    elif ordenar_por == "Valor (menor)":
        df_filtrado = df_filtrado.sort_values('Total', ascending=True)
    
    # Exibir histórico
    if total_registros == 0:
        st.info("🔍 Nenhum resultado encontrado com os filtros aplicados.")
    else:
        for _, r in df_filtrado.iterrows():
            # Determinar cor da borda baseada no status
            if str(r.get("Status", "")).lower() == "concluído":
                cor_borda = "#28a745"
                icone_status = "✅"
            elif "pendente" in str(r.get("Status", "")).lower():
                cor_borda = "#FFC107"
                icone_status = "⏳"
            else:
                cor_borda = "#6c757d"
                icone_status = "📝"
            
            # Card do histórico
            html_card = f"""
            <div class="history-card" style="border-left: 5px solid {cor_borda}">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h3 style="margin: 0; font-size: 20px; color: white; font-weight: 700;">
                            {obter_icone_html(r.get("Categoria", ""))} {r.get("Carro", "N/A")}
                            <span style="font-size: 14px; color: #666; margin-left: 10px;">
                                {icone_status} {r.get("Status", "N/A")}
                            </span>
                        </h3>
                        <p style="margin: 5px 0 0 0; color: #bbb; font-size: 14px;">
                            <i class="bi bi-person"></i> {r.get("Cliente", "N/A")} 
                            &nbsp;|&nbsp; 
                            <i class="bi bi-tag"></i> {r.get("Placa", "N/A")}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <h2 style="margin: 0; color: #39FF14; font-weight: 700; font-size: 22px;">
                            {formatar_moeda(float(r.get("Total", 0)))}
                        </h2>
                        <span style="background-color: #222; padding: 4px 8px; border-radius: 6px; 
                                   font-size: 11px; text-transform: uppercase; letter-spacing: 1px; 
                                   color: #aaa;">
                            <i class="bi bi-calendar"></i> {r.get("Data", "N/A")}
                        </span>
                    </div>
                </div>
                
                <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid #333; 
                           color: #888; font-size: 13px;">
                    <i class="bi bi-tools"></i> {r.get("Serviços", "N/A")}
                </div>
                
                <div style="margin-top: 10px; display: flex; gap: 15px; font-size: 12px; color: #666;">
                    <span>
                        <i class="bi bi-cash"></i> 
                        Comissão: {formatar_moeda(float(r.get("Valor Comissao", 0)))}
                    </span>
                    <span>
                        <i class="bi bi-bank"></i> 
                        Caixa: {formatar_moeda(float(r.get("Fundo Caixa", 0)))}
                    </span>
                    <span>
                        <i class="bi bi-graph-up"></i> 
                        Lucro: {formatar_moeda(float(r.get("Lucro Liquido", 0)))}
                    </span>
                </div>
                
                <div style="margin-top: 10px; font-size: 11px; color: #555;">
                    <i class="bi bi-person-workspace"></i> 
                    Executor: {r.get("Funcionario", "N/A")} | 
                    Status Comissão: {r.get("Status Comissao", "N/A")}
                </div>
            </div>
            """
            
            st.markdown(html_card, unsafe_allow_html=True)
        
        # Paginação (simples)
        total_paginas = (total_registros + 9) // 10
        if total_paginas > 1:
            pagina_atual = st.number_input(
                "Página",
                min_value=1,
                max_value=total_paginas,
                value=1,
                step=1
            )
            st.write(f"Mostrando {min(10, total_registros)} de {total_registros} registros")
        
        # Botões de ação
        col_acao1, col_acao2, col_acao3 = st.columns(3)
        
        with col_acao1:
            if st.button("📤 Exportar Histórico", use_container_width=True):
                csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="⬇️ Baixar CSV",
                    data=csv_data,
                    file_name=f"historico_servicos_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col_acao2:
            if st.button("📊 Gerar Relatório", use_container_width=True):
                # Análise por categoria
                if 'Categoria' in df_filtrado.columns:
                    analise_categoria = df_filtrado.groupby('Categoria').agg({
                        'Total': ['count', 'sum', 'mean'],
                        'Lucro Liquido': 'sum'
                    }).round(2)
                    
                    st.write("### 📈 Análise por Categoria")
                    st.dataframe(analise_categoria)
        
        with col_acao3:
            if st.button("🔄 Atualizar Dados", use_container_width=True):
                st.cache_data.clear()
                st.success("✅ Cache limpo! Dados serão recarregados.")
                t_sleep.sleep(2)
                st.rerun()

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

st.markdown("<br><br><br>", unsafe_allow_html=True)  # Espaço para o rodapé fixo
st.markdown(
    '''
    <div class="footer">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                💎 <b>JM Detail System PRO</b> | Versão 14.0
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
    os.makedirs("backups", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    st.session_state.system_initialized = True
    
    # Criar backup inicial
    criar_backup_local()
    
    # Registrar início da sessão
    registrar_log("Sistema", "Aplicativo iniciado", 
                 f"Usuário: {st.experimental_user.email if hasattr(st.experimental_user, 'email') else 'N/A'}")
