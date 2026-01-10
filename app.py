import streamlit as st
import pandas as pd
import altair as alt
# plotly removido conforme solicitado
from datetime import datetime, date, time, timedelta
from fpdf import FPDF
import gspread
import os
import time as t_sleep
import hashlib
import re
import logging
from functools import lru_cache
import json

# ==============================================================================
# --- CONFIGURAÇÃO DE LOGS (NOVO) ---
# ==============================================================================
logging.basicConfig(
    filename='app_financeiro.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_acao(acao, detalhes=""):
    """Registra ações importantes no sistema"""
    usuario = st.session_state.get('usuario_logado', 'Sistema')
    logging.info(f"{usuario} - {acao} - {detalhes}")
    # Também salva no Google Sheets para auditoria
    try:
        salvar_no_google_silencioso("Logs", {
            'Data': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'Usuario': usuario,
            'Acao': acao,
            'Detalhes': str(detalhes)[:500]  # Limita tamanho
        })
    except:
        pass  # Não quebra o app se falhar

# ==============================================================================
# --- 1. CONFIGURAÇÃO DA PÁGINA ---
# ==============================================================================
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# --- 2. SISTEMA DE LOGIN SEGURO (MELHORADO) ---
# ==============================================================================
def check_password():
    if st.session_state.get("password_correct", False):
        return True
    
    try:
        if st.query_params.get("acesso_liberado") == "sim_mestre":
            st.session_state["password_correct"] = True
            st.session_state["usuario_logado"] = "Admin"
            return True
    except: 
        pass
    
    # Função de hash segura
    def verificar_senha(input_pwd):
        try:
            # Hash armazenado no secrets
            senha_hash_correto = st.secrets["app"]["password_hash"]
            input_hash = hashlib.sha256(input_pwd.encode()).hexdigest()
            return input_hash == senha_hash_correto
        except:
            # Fallback temporário (remover depois de configurar o hash)
            return input_pwd == "1234"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### <i class='bi bi-shield-lock-fill' style='color:#D90429'></i> Acesso Restrito - JM Detail", unsafe_allow_html=True)
        with st.form("login_form"):
            pwd = st.text_input("Digite a senha de acesso:", type="password")
            submit = st.form_submit_button("ACESSAR SISTEMA")
            if submit:
                if verificar_senha(pwd): 
                    st.session_state["password_correct"] = True
                    st.session_state["usuario_logado"] = "Administrador"
                    try: 
                        st.query_params["acesso_liberado"] = "sim_mestre"
                    except: 
                        pass
                    log_acao("Login", "Acesso concedido")
                    st.rerun()
                else: 
                    st.error("Senha incorreta.")
                    log_acao("Tentativa de Login", "Senha incorreta")
    
    return False

if not check_password(): 
    st.stop()

# ==============================================================================
# --- 3. ESTILO CSS (V13.0 - BLINDADO) - MANTIDO IGUAL ---
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

    /* --- NOVO: BARRA DE PROGRESSO PERSONALIZADA --- */
    .stProgress > div > div > div > div {
        background-color: #D90429;
    }
    
    /* --- NOTIFICAÇÕES --- */
    .notification-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        background: #D90429;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
    }
    
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- FUNÇÕES AUXILIARES (MELHORADAS) ---
# ==============================================================================

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ==============================================================================
# --- VALIDAÇÕES (NOVO) ---
# ==============================================================================

def validar_placa(placa):
    """Valida placas brasileiras (antigo e mercosul)"""
    if not placa or pd.isna(placa):
        return False
    
    placa = str(placa).strip().upper()
    
    # Padrões brasileiros
    padrao_antigo = re.compile(r'^[A-Z]{3}-?\d{4}$')
    padrao_mercosul = re.compile(r'^[A-Z]{3}\d[A-Z]\d{2}$')
    
    return bool(padrao_antigo.match(placa) or padrao_mercosul.match(placa))

def validar_data_futura(data):
    """Valida se data não é no passado"""
    return data >= datetime.now().date()

def validar_email(email):
    """Validação básica de email"""
    if not email:
        return True  # Email opcional
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

# ==============================================================================
# --- CONEXÃO GOOGLE SHEETS COM CACHE E RETRY (MELHORADO) ---
# ==============================================================================

@st.cache_data(ttl=300)  # Cache de 5 minutos
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
        log_acao("Erro Conexão Google Sheets", str(e))
        return None

@st.cache_data(ttl=60)  # Cache de 1 minuto para dados
def carregar_dados_cache(aba):
    """Carrega dados com cache inteligente"""
    sheet = conectar_google_sheets()
    if sheet is None: 
        return pd.DataFrame()
    
    try: 
        dados = pd.DataFrame(sheet.worksheet(aba).get_all_records())
        
        # Validação básica de colunas
        if not dados.empty:
            if 'Data' in dados.columns:
                dados['Data'] = pd.to_datetime(dados['Data'], format='%d/%m/%Y', errors='coerce')
        
        return dados
    except Exception as e: 
        log_acao(f"Erro carregar {aba}", str(e))
        return pd.DataFrame()

def carregar_dados(aba):
    """Wrapper para compatibilidade"""
    return carregar_dados_cache(aba)

def salvar_no_google_silencioso(aba, linha_dados):
    """Versão silenciosa para logs"""
    try:
        return salvar_no_google(aba, linha_dados, silencioso=True)
    except:
        return False, "Erro"

def salvar_no_google(aba, linha_dados, silencioso=False):
    """Salva dados com validação e retry"""
    sheet = conectar_google_sheets()
    if sheet is None: 
        if not silencioso:
            st.error("Falha na conexão com Google Sheets.")
        return False, "Falha na conexão."
    
    # Tentar 3 vezes com retry
    for tentativa in range(3):
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
                else:
                    # Tentar variações (remover acentos, etc.)
                    alt = (col_name.replace("ç", "c").replace("ã", "a")
                          .replace("õ", "o").replace("á", "a")
                          .replace("é", "e").replace("í", "i")
                          .replace("ó", "o").replace("ú", "u"))
                    
                    if alt in headers:
                        index = headers.index(alt)
                        nova_linha[index] = valor
            
            # Adicionar timestamp de auditoria
            if '_timestamp' not in headers:
                ws.append_row([''] * len(headers))  # Linha temporária
                ws.update_cell(1, len(headers) + 1, '_timestamp')
                headers = ws.row_values(1)
                nova_linha = nova_linha + [datetime.now().isoformat()]
            else:
                index = headers.index('_timestamp')
                nova_linha[index] = datetime.now().isoformat()
            
            ws.append_row(nova_linha)
            
            if not silencioso:
                log_acao(f"Salvar em {aba}", f"Dados: {linha_dados}")
            
            return True, "Sucesso"
            
        except Exception as e:
            if tentativa == 2:  # Última tentativa
                if not silencioso:
                    st.error(f"Erro ao salvar: {str(e)}")
                    log_acao(f"Erro salvar {aba}", str(e))
                return False, str(e)
            t_sleep.sleep(0.5)  # Aguarda meio segundo
    
    return False, "Falha após tentativas"

def excluir_agendamento(indice_linha):
    sheet = conectar_google_sheets()
    if sheet is None: 
        return False
    
    try: 
        ws = sheet.worksheet("Agendamentos")
        ws.delete_rows(indice_linha + 2)
        log_acao("Excluir agendamento", f"Linha {indice_linha}")
        return True
    except Exception as e: 
        log_acao("Erro excluir agendamento", str(e))
        return False

# ==============================================================================
# --- SISTEMA DE NOTIFICAÇÕES (NOVO) ---
# ==============================================================================

def enviar_notificacao(tipo, mensagem):
    """Sistema de notificações interno"""
    if 'notificacoes' not in st.session_state:
        st.session_state.notificacoes = []
    
    icones = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    
    st.session_state.notificacoes.append({
        'tipo': tipo,
        'icone': icones.get(tipo, '📌'),
        'mensagem': mensagem,
        'data': datetime.now().strftime("%H:%M"),
        'lida': False
    })
    
    # Limitar a 15 notificações
    if len(st.session_state.notificacoes) > 15:
        st.session_state.notificacoes = st.session_state.notificacoes[-15:]

def mostrar_notificacoes():
    """Mostra as notificações não lidas"""
    if 'notificacoes' not in st.session_state:
        return
    
    nao_lidas = [n for n in st.session_state.notificacoes if not n['lida']]
    
    if nao_lidas:
        # Ícone de notificação no header
        st.markdown(f"""
        <div style="position: fixed; top: 20px; right: 20px; z-index: 10000;">
            <div class="notification-badge">{len(nao_lidas)}</div>
            <button onclick="document.getElementById('notif-popup').style.display='block'" 
                    style="background: none; border: none; color: #fff; font-size: 24px; cursor: pointer;">
                <i class="bi bi-bell-fill"></i>
            </button>
        </div>
        
        <div id="notif-popup" style="display: none; position: fixed; top: 60px; right: 20px; 
             background: #222; border: 1px solid #444; border-radius: 10px; padding: 15px; 
             width: 300px; z-index: 10001; max-height: 400px; overflow-y: auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; color: white;">Notificações</h4>
                <button onclick="document.getElementById('notif-popup').style.display='none'"
                        style="background: none; border: none; color: #fff; cursor: pointer;">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>
            {''.join([f"""
            <div style="background: #333; padding: 10px; margin-bottom: 8px; border-radius: 6px; border-left: 4px solid {'#00B4DB' if n['tipo']=='info' else '#28a745' if n['tipo']=='success' else '#ffc107' if n['tipo']=='warning' else '#dc3545'};">
                <div style="font-size: 12px; color: #aaa;">{n['icone']} {n['data']}</div>
                <div style="color: white; font-size: 14px;">{n['mensagem']}</div>
            </div>
            """ for n in reversed(nao_lidas[:5])])}
            <button onclick="limparNotificacoes()" 
                    style="width: 100%; background: #444; color: white; border: none; padding: 8px; border-radius: 5px; margin-top: 10px;">
                Limpar Todas
            </button>
        </div>
        
        <script>
        function limparNotificacoes() {{
            fetch('/clear_notifications', {{method: 'POST'}})
            .then(() => location.reload());
        }}
        </script>
        """, unsafe_allow_html=True)
        
        # Marcar como lidas após mostrar
        for n in st.session_state.notificacoes:
            n['lida'] = True

# ==============================================================================
# --- FUNÇÕES DE CATÁLOGO E PDF (MANTIDAS) ---
# ==============================================================================

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

def obter_icone_html(cat):
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

def gerar_pdf(cliente, carro, placa, data_servico, servicos_com_precos, total):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"): 
        pdf.image("logo.png", x=55, y=10, w=100)
        pdf.ln(35)
    else: 
        pdf.ln(20)
    
    def txt(t): 
        return t.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt=txt("JM DETAIL - Estética Automotiva Premium"), ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt=txt("Tucano - BA | Rua São João, 54 | (75) 99830-3753"), ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt=txt(f"CLIENTE: {cliente}"), ln=True)
    pdf.cell(0, 10, txt=txt(f"VEÍCULO: {carro} | PLACA: {placa}"), ln=True)
    pdf.cell(0, 10, txt=txt(f"DATA: {data_servico}"), ln=True)
    pdf.ln(5)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(140, 10, txt("Pacote de Serviços"), border=1, fill=True)
    pdf.cell(50, 10, txt("Valor"), border=1, ln=True, fill=True, align='C')
    pdf.set_font("Arial", size=12)
    
    for s, v in servicos_com_precos.items():
        t_s = (s[:60] + '...') if len(s) > 60 else s
        pdf.cell(140, 10, txt=txt(t_s), border=1)
        pdf.cell(50, 10, txt=txt(f"R$ {v:.2f}"), border=1, ln=True, align='C')
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(140, 10, txt="TOTAL", align='R')
    pdf.cell(50, 10, txt=txt(f"R$ {total:.2f}"), border=1, align='C')
    
    return pdf.output(dest="S").encode("latin-1")

# ==============================================================================
# --- FUNÇÕES DE RELATÓRIOS (NOVO) ---
# ==============================================================================

def calcular_metricas_avancadas():
    """Calcula métricas avançadas para o dashboard"""
    df_v = carregar_dados("Vendas")
    df_vendas = df_v[df_v['Status'] == 'Concluído']
    
    if df_vendas.empty:
        return {}
    
    # Limpeza de dados
    df_vendas['Total'] = pd.to_numeric(df_vendas['Total'], errors='coerce').fillna(0)
    
    metricas = {
        'Ticket Médio': df_vendas['Total'].mean(),
        'Vendas por Dia': len(df_vendas) / df_vendas['Data'].nunique() if df_vendas['Data'].nunique() > 0 else 0,
        'Serviço Mais Popular': '',
        'Melhor Cliente': '',
        'Dia da Semana Mais Movimentado': ''
    }
    
    try:
        # Serviço mais popular
        if 'Serviços' in df_vendas.columns:
            todos_servicos = df_vendas['Serviços'].str.split(', ').explode()
            metricas['Serviço Mais Popular'] = todos_servicos.mode()[0] if not todos_servicos.empty else 'N/A'
        
        # Melhor cliente
        if 'Cliente' in df_vendas.columns:
            cliente_valor = df_vendas.groupby('Cliente')['Total'].sum()
            if not cliente_valor.empty:
                metricas['Melhor Cliente'] = cliente_valor.idxmax()
        
        # Dia mais movimentado
        if 'Data' in df_vendas.columns:
            df_vendas['Dia_Semana'] = df_vendas['Data'].dt.day_name()
            dia_count = df_vendas.groupby('Dia_Semana').size()
            if not dia_count.empty:
                metricas['Dia da Semana Mais Movimentado'] = dia_count.idxmax()
    
    except Exception as e:
        log_acao("Erro cálculo métricas", str(e))
    
    return metricas

def verificar_metas():
    """Verifica metas diárias e semanais"""
    hoje = datetime.now()
    df_v = carregar_dados("Vendas")
    df_vendas = df_v[df_v['Status'] == 'Concluído']
    
    if df_vendas.empty:
        return {'diaria': {'meta': 800, 'atingido': 0, 'percentual': 0},
                'semanal': {'meta': 4000, 'atingido': 0, 'percentual': 0}}
    
    # Meta configurável (pode vir do secrets)
    META_DIARIA = 800.00
    META_SEMANAL = 4000.00
    
    # Vendas de hoje
    vendas_hoje = df_vendas[
        df_vendas['Data'].dt.date == hoje.date()
    ]['Total'].sum()
    
    # Vendas da semana (segunda a hoje)
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    vendas_semana = df_vendas[
        df_vendas['Data'] >= inicio_semana
    ]['Total'].sum()
    
    return {
        'diaria': {
            'meta': META_DIARIA,
            'atingido': vendas_hoje,
            'percentual': min((vendas_hoje / META_DIARIA) * 100, 100)
        },
        'semanal': {
            'meta': META_SEMANAL,
            'atingido': vendas_semana,
            'percentual': min((vendas_semana / META_SEMANAL) * 100, 100)
        }
    }

# ==============================================================================
# --- FUNÇÃO DE BACKUP (NOVO) ---
# ==============================================================================

def criar_backup():
    """Cria backup dos dados atuais"""
    try:
        data_backup = datetime.now().strftime("%Y%m%d_%H%M")
        backup_dir = "backups"
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        dados_backup = {}
        
        for aba in ["Vendas", "Agendamentos", "Despesas"]:
            df = carregar_dados(aba)
            if not df.empty:
                caminho = f"{backup_dir}/{data_backup}_{aba}.csv"
                df.to_csv(caminho, index=False, encoding='utf-8-sig')
                dados_backup[aba] = caminho
        
        # Salvar metadados do backup
        with open(f"{backup_dir}/{data_backup}_info.json", 'w') as f:
            json.dump({
                'data': data_backup,
                'quantidade_arquivos': len(dados_backup),
                'tamanho_total': sum(os.path.getsize(p) for p in dados_backup.values()),
                'abas': list(dados_backup.keys())
            }, f, indent=2)
        
        enviar_notificacao('success', f'Backup criado: {data_backup}')
        log_acao("Backup", f"Criado backup {data_backup}")
        
        return True, f"Backup criado: {data_backup}"
    
    except Exception as e:
        log_acao("Erro backup", str(e))
        return False, f"Erro: {str(e)}"

# ==============================================================================
# --- HEADER COM NOTIFICAÇÕES ---
# ==============================================================================

# Mostrar notificações
mostrar_notificacoes()

c_logo1, c_logo2, c_logo3 = st.columns([1,2,1])
with c_logo2:
    if os.path.exists("logo.png"): 
        st.image("logo.png", use_container_width=True)
    else: 
        st.markdown("<h1 style='text-align:center; color:#D90429; font-weight:800'>JM DETAIL</h1>", unsafe_allow_html=True)

st.write("") 

# MENU DE NAVEGAÇÃO
menu_opcoes = ["DASHBOARD", "AGENDA", "FINANCEIRO", "DESPESAS", "HISTÓRICO"]
menu_selecionado = st.radio("Navegação", menu_opcoes, horizontal=True, label_visibility="collapsed")

st.write("---") 

# ==============================================================================
# --- PÁGINA DASHBOARD (MELHORADA) ---
# ==============================================================================

def page_dashboard():
    hoje = datetime.now()
    mes_atual, ano_atual = hoje.month, hoje.year
    nome_meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    # Título com Ícone Original
    st.markdown(f'## <i class="bi bi-speedometer2" style="color: #00B4DB;"></i> Painel Geral <small style="font-size:14px; color:#888">| {nome_meses[mes_atual]}/{ano_atual}</small>', unsafe_allow_html=True)
    
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    df_a = carregar_dados("Agendamentos")
    
    receita_mes, despesa_mes, pendente_total, count_p = 0.0, 0.0, 0.0, 0
    lucro_operacional = 0.0
    
    if not df_v.empty:
        # Limpeza robusta da coluna Total
        if "Total" in df_v.columns:
            df_v['Total'] = pd.to_numeric(df_v['Total'].astype(str)
                                         .str.replace('R\$', '', regex=False)
                                         .str.replace('.', '')
                                         .str.replace(',', '.'), errors='coerce').fillna(0)
        
        if 'Data' in df_v.columns:
            df_v['Data_dt'] = pd.to_datetime(df_v['Data'], format='%d/%m/%Y', errors='coerce')
            df_mes = df_v[(df_v['Data_dt'].dt.month == mes_atual) & (df_v['Data_dt'].dt.year == ano_atual)]
            
            # Receita Bruta (Soma dos Totais Concluídos)
            if "Status" in df_mes.columns:
                receita_mes = df_mes[df_mes["Status"]=="Concluído"]["Total"].sum()
            
            # Lucro Operacional (50% do Bruto)
            lucro_operacional = receita_mes * 0.50
            
            # Pendentes
            if "Status" in df_v.columns:
                pendente_total = df_v[df_v["Status"]=="Orçamento/Pendente"]["Total"].sum()
                count_p = len(df_v[df_v["Status"]=="Orçamento/Pendente"])

    if not df_d.empty:
        if 'Data' in df_d.columns:
            df_d['Data_dt'] = pd.to_datetime(df_d['Data'], format='%d/%m/%Y', errors='coerce')
            df_d_mes = df_d[(df_d['Data_dt'].dt.month == mes_atual) & (df_d['Data_dt'].dt.year == ano_atual)]
            
            # Limpeza robusta da coluna Valor
            if "Valor" in df_d_mes.columns:
                despesa_mes = pd.to_numeric(df_d_mes["Valor"].astype(str)
                                          .str.replace('R\$', '', regex=False)
                                          .str.replace('.', '')
                                          .str.replace(',', '.'), errors='coerce').fillna(0).sum()
    
    # CÁLCULO FINAL DE LUCRO REAL (Tempo Real)
    lucro_final = lucro_operacional - despesa_mes
    
    # CARDS PRINCIPAIS
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
            <small>Gastos externos</small>
        </div>
        ''', unsafe_allow_html=True)
    
    cor_lucro = "bg-green" if lucro_final >= 0 else "bg-red"
    with c4: 
        st.markdown(f'''
        <div class="dash-card {cor_lucro}">
            <i class="bi bi-wallet2 card-icon-bg"></i>
            <h4>LUCRO LÍQUIDO (MÊS)</h4>
            <div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_final)}</div>
            <small>50% Bruto - Despesas</small>
        </div>
        ''', unsafe_allow_html=True)
    
    st.write("---")
    
    # --- NOVO: METAS DIÁRIAS E SEMANAIS ---
    st.markdown('### <i class="bi bi-bullseye" style="color: #FF9800;"></i> Metas de Performance', unsafe_allow_html=True)
    
    metas = verificar_metas()
    
    col_meta1, col_meta2 = st.columns(2)
    
    with col_meta1:
        st.markdown(f"**Meta Diária:** {formatar_moeda(metas['diaria']['atingido'])} / {formatar_moeda(metas['diaria']['meta'])}")
        st.progress(metas['diaria']['percentual'] / 100)
        st.caption(f"{metas['diaria']['percentual']:.1f}% da meta diária")
    
    with col_meta2:
        st.markdown(f"**Meta Semanal:** {formatar_moeda(metas['semanal']['atingido'])} / {formatar_moeda(metas['semanal']['meta'])}")
        st.progress(metas['semanal']['percentual'] / 100)
        st.caption(f"{metas['semanal']['percentual']:.1f}% da meta semanal")
    
    st.write("---")
    
    # --- NOVO: MÉTRICAS AVANÇADAS ---
    st.markdown('### <i class="bi bi-bar-chart-line" style="color: #39FF14;"></i> Métricas Avançadas', unsafe_allow_html=True)
    
    metricas = calcular_metricas_avancadas()
    
    if metricas:
        col_met1, col_met2, col_met3 = st.columns(3)
        
        with col_met1:
            st.metric("Ticket Médio", formatar_moeda(metricas.get('Ticket Médio', 0)))
            st.metric("Vendas/Dia", f"{metricas.get('Vendas por Dia', 0):.1f}")
        
        with col_met2:
            st.metric("Serviço Mais Popular", metricas.get('Serviço Mais Popular', 'N/A'))
            st.metric("Melhor Cliente", metricas.get('Melhor Cliente', 'N/A')[:15] + '...' if len(metricas.get('Melhor Cliente', '')) > 15 else metricas.get('Melhor Cliente', 'N/A'))
        
        with col_met3:
            st.metric("Dia Mais Movimentado", metricas.get('Dia da Semana Mais Movimentado', 'N/A'))
            # Botão de backup
            if st.button("Criar Backup", use_container_width=True, type="secondary"):
                ok, msg = criar_backup()
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
    
    st.write("---")
    
    # GRÁFICO E AGENDA (MANTIDO)
    col_graf, col_prox = st.columns([2, 1])
    
    with col_graf:
        st.markdown('### <i class="bi bi-graph-up-arrow" style="color: #39FF14;"></i> Performance Mensal', unsafe_allow_html=True)
        if not df_v.empty and 'df_mes' in locals() and not df_mes.empty:
            base = alt.Chart(df_mes).encode(
                x=alt.X('Data', title=None, axis=alt.Axis(labelColor='white', grid=False))
            )
            bars = base.mark_bar(size=30, cornerRadiusEnd=5).encode(
                y=alt.Y('Total', axis=None),
                color=alt.Color('Status', 
                              scale=alt.Scale(domain=['Concluído', 'Orçamento/Pendente'], 
                                            range=['#00F260', '#FF0080']), 
                              legend=None),
                tooltip=['Data', 'Cliente', 'Carro', 'Total']
            )
            st.altair_chart(bars.properties(height=300, background='transparent'), 
                          use_container_width=True)
        else:
            st.info("Sem dados de vendas neste mês.")
    
    with col_prox:
        st.markdown('### <i class="bi bi-calendar-week"></i> Próximos na Agenda', unsafe_allow_html=True)
        if not df_a.empty:
            if 'Data' in df_a.columns:
                df_a['Data_dt'] = pd.to_datetime(df_a['Data'], format='%d/%m/%Y', errors='coerce')
                hoje_dt = pd.to_datetime(date.today())
                df_futuro = df_a[df_a['Data_dt'] >= hoje_dt].sort_values(by='Data_dt').head(4)
                
                if not df_futuro.empty:
                    for _, r in df_futuro.iterrows():
                        st.markdown(f'''
                        <div style="background-color:#161616; padding:15px; border-radius:12px; margin-bottom:10px; border-left:4px solid #D90429;">
                            <div style="font-size:12px; color:#aaa; margin-bottom:5px">
                                <i class="bi bi-calendar"></i> {r.get('Data', 'N/A')} • {r.get('Hora', 'N/A')}
                            </div>
                            <div style="font-weight:bold; font-size:16px; color:white">
                                {obter_icone_html(r.get("Categoria", ""))} {r.get('Veiculo', 'N/A')}
                            </div>
                            <div style="font-size:13px; color:#888;">{r.get('Cliente', 'N/A')}</div>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("Agenda livre.")
        else:
            st.info("Agenda vazia.")

# ==============================================================================
# --- PÁGINA FINANCEIRO (MELHORADA) ---
# ==============================================================================

def page_financeiro():
    st.markdown('## <i class="bi bi-cash-coin" style="color: #28a745;"></i> Gestão Financeira', unsafe_allow_html=True)
    
    df_v = carregar_dados("Vendas")
    comissao_pendente = 0.0
    fundo_caixa = 0.0
    
    if not df_v.empty:
        # Garantir coluna de status de comissão
        if "Status Comissao" not in df_v.columns:
            df_v["Status Comissao"] = "Pendente"
        
        # Limpeza robusta
        for col in ["Total", "Valor Comissao", "Fundo Caixa"]:
            if col in df_v.columns:
                df_v[col] = pd.to_numeric(df_v[col].astype(str)
                                         .str.replace('R\$', '', regex=False)
                                         .str.replace('.', '')
                                         .str.replace(',', '.'), errors='coerce').fillna(0)
        
        # Filtrar apenas pendentes
        df_pendente = df_v[df_v["Status Comissao"] != "Pago"]
        
        # Cálculo SEGURO de comissões
        comissao_pendente = 0.0
        for _, row in df_pendente.iterrows():
            # Verifica se é serviço de equipe
            is_equipe = False
            if "Valor Comissao" in row and row["Valor Comissao"] > 0:
                is_equipe = True
            elif "Funcionario" in row and "Equipe" in str(row["Funcionario"]):
                is_equipe = True
            
            if is_equipe and "Total" in row:
                comissao_pendente += (row["Total"] * 0.40)
        
        fundo_caixa = df_v["Fundo Caixa"].sum() if "Fundo Caixa" in df_v.columns else 0
    
    # Card de fundo de caixa
    st.markdown(f'''
    <div class="dash-card bg-purple">
        <i class="bi bi-bank card-icon-bg"></i>
        <h4>FUNDO DE CAIXA (ACUMULADO)</h4>
        <div style="font-size:24px;font-weight:bold">{formatar_moeda(fundo_caixa)}</div>
        <small>10% de cada serviço concluído</small>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2,1,1])
    
    with col1: 
        st.metric("Comissões Pendentes", formatar_moeda(comissao_pendente), 
                 help="40% do valor bruto dos serviços da equipe")
    
    with col2:
        if comissao_pendente > 0:
            if st.button("💰 Pagar Todas", use_container_width=True):
                sheet = conectar_google_sheets()
                if sheet:
                    try:
                        ws = sheet.worksheet("Vendas")
                        dados = ws.get_all_records()
                        header = ws.row_values(1)
                        
                        if "Status Comissao" in header:
                            col_idx = header.index("Status Comissao") + 1
                            for i, linha in enumerate(dados):
                                v = pd.to_numeric(str(linha.get("Valor Comissao", "0"))
                                                .replace('R$', '')
                                                .replace(',', '.'), errors='coerce')
                                if v > 0 and str(linha.get("Status Comissao", "")) != "Pago":
                                    ws.update_cell(i + 2, col_idx, "Pago")
                        
                        st.success("Comissões pagas com sucesso!")
                        log_acao("Pagamento Comissões", f"Valor total: {comissao_pendente}")
                        enviar_notificacao('success', 'Comissões pagas!')
                        t_sleep.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {str(e)}")
                        log_acao("Erro pagar comissões", str(e))
    
    with col3:
        if st.button("📊 Relatório Detalhado", use_container_width=True, type="secondary"):
            # Expandir para mostrar relatório
            st.session_state['mostrar_relatorio'] = not st.session_state.get('mostrar_relatorio', False)
    
    # Relatório detalhado (se solicitado)
    if st.session_state.get('mostrar_relatorio', False) and not df_v.empty:
        st.markdown("---")
        st.markdown("#### 📈 Relatório de Comissões por Funcionário")
        
        # Filtrar apenas serviços com comissão
        df_comissoes = df_v[df_v["Valor Comissao"] > 0]
        
        if not df_comissoes.empty:
            # Agrupar por funcionário
            resumo = df_comissoes.groupby("Funcionario").agg({
                'Valor Comissao': 'sum',
                'Total': 'sum',
                'Carro': 'count'
            }).rename(columns={'Carro': 'Qtd Serviços', 'Total': 'Faturamento Gerado'})
            
            resumo['% Comissão'] = (resumo['Valor Comissao'] / resumo['Faturamento Gerado'] * 100).round(1)
            
            # Formatar moeda
            for col in ['Valor Comissao', 'Faturamento Gerado']:
                resumo[col] = resumo[col].apply(lambda x: formatar_moeda(x))
            
            st.dataframe(resumo, use_container_width=True)
            
            # Exportar opção
            csv = resumo.to_csv(index=True).encode('utf-8')
            st.download_button(
                label="📥 Exportar CSV",
                data=csv,
                file_name=f"comissoes_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("Nenhuma comissão registrada.")

# ==============================================================================
# --- PÁGINA AGENDAMENTO (COM VALIDAÇÕES) ---
# ==============================================================================

def page_agendamento():
    st.markdown('## <i class="bi bi-calendar-check" style="color: white;"></i> Agenda Integrada', unsafe_allow_html=True)
    
    tab_new, tab_list = st.tabs(["📅 NOVO AGENDAMENTO", "📋 LISTA DE SERVIÇOS"]) 
    df_cat = carregar_catalogo()
    
    with tab_new:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            
            cli = c1.text_input("Nome do Cliente*", placeholder="Nome completo do cliente")
            veic = c1.text_input("Modelo do Veículo*", placeholder="Ex: Fiat Toro 2023")
            placa = c2.text_input("Placa*", placeholder="AAA-0A00 ou AAA0A00").upper()
            dt = c2.date_input("Data*", value=date.today(), format="DD/MM/YYYY", 
                             min_value=date.today())
            hr = c2.time_input("Horário*", value=time(8, 0)).strftime("%H:%M")
            
            # Validação em tempo real
            erros = []
            
            if placa and not validar_placa(placa):
                erros.append("❌ Placa inválida. Use formato: AAA-0A00 ou AAA0A00")
            
            if dt and not validar_data_futura(dt):
                erros.append("⚠️ Data não pode ser no passado")
            
            if erros:
                for erro in erros:
                    st.warning(erro)
            
            cat = st.selectbox("Categoria do Veículo*:", df_cat["Categoria"])
            servs_disp = [c for c in df_cat.columns if c != "Categoria"]
            escolhidos = st.multiselect("Selecione os Serviços*:", servs_disp)
            
            st.divider()
            
            ce1, ce2, ce3 = st.columns(3)
            extra_v = ce1.number_input("Valor Extra (R$)", min_value=0.0, value=0.0, step=10.0)
            desconto_v = ce2.number_input("Desconto (R$)", min_value=0.0, value=0.0, step=10.0)
            quem = ce3.radio("Executor*:", ["Eu Mesmo", "Equipe"], horizontal=True)
            
            # Cálculo em Tempo Real
            if escolhidos and cat:
                try:
                    precos = {s: df_cat[df_cat["Categoria"] == cat][s].values[0] for s in escolhidos}
                    total = sum(precos.values()) + extra_v - desconto_v
                    
                    # Exibir cálculo detalhado
                    with st.expander("💰 Detalhamento do Orçamento"):
                        for serv, valor in precos.items():
                            st.write(f"• {serv}: {formatar_moeda(valor)}")
                        
                        if extra_v > 0:
                            st.write(f"• Extra: +{formatar_moeda(extra_v)}")
                        
                        if desconto_v > 0:
                            st.write(f"• Desconto: -{formatar_moeda(desconto_v)}")
                        
                        st.write(f"**Total: {formatar_moeda(total)}**")
                    
                    st.markdown(f"<h3 style='text-align:right; color:#39FF14'>Total: {formatar_moeda(total)}</h3>", unsafe_allow_html=True)
                    
                    # Previsão de divisão
                    comissao_prev = total * 0.40 if "Equipe" in quem else 0.0
                    fundo_prev = total * 0.10
                    lucro_prev = total - comissao_prev - fundo_prev
                    
                    st.caption(f"Previsão: Caixa: {formatar_moeda(fundo_prev)} | Comissão: {formatar_moeda(comissao_prev)} | Lucro: {formatar_moeda(lucro_prev)}")
                    
                    # Botão de confirmação
                    if st.button("✅ CONFIRMAR AGENDAMENTO", use_container_width=True, 
                               disabled=not all([cli, veic, placa, escolhidos])):
                        
                        # Validação final
                        if not validar_placa(placa):
                            st.error("Placa inválida. Corrija antes de confirmar.")
                            return
                        
                        serv_str = ", ".join(escolhidos)
                        
                        dados = {
                            "Data": dt.strftime("%d/%m/%Y"),
                            "Hora": hr,
                            "Cliente": cli,
                            "Veiculo": veic,
                            "Placa": placa,
                            "Servicos": serv_str,
                            "Total": total,
                            "Executor": quem,
                            "LucroPrevisto": lucro_prev,
                            "Categoria": cat,
                            "Status": "Agendado",
                            "DataCadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
                        }
                        
                        ok, msg = salvar_no_google("Agendamentos", dados)
                        
                        if ok:
                            st.success("✅ Agendamento registrado com sucesso!")
                            log_acao("Novo Agendamento", f"Cliente: {cli} | Valor: {total}")
                            enviar_notificacao('success', f'Novo agendamento: {cli} - {formatar_moeda(total)}')
                            
                            # Opção de gerar PDF
                            with st.spinner("Gerando orçamento em PDF..."):
                                pdf_bytes = gerar_pdf(cli, veic, placa, dt.strftime("%d/%m/%Y"), 
                                                    precos, total)
                                st.download_button(
                                    label="📄 Baixar Orçamento (PDF)",
                                    data=pdf_bytes,
                                    file_name=f"orcamento_{cli}_{dt.strftime('%Y%m%d')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            
                            t_sleep.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"Erro ao salvar: {msg}")
                            log_acao("Erro Agendamento", msg)
                
                except Exception as e:
                    st.error(f"Erro no cálculo: {str(e)}")
                    log_acao("Erro cálculo agendamento", str(e))
            else:
                st.info("Selecione os serviços para calcular o total.")
    
    with tab_list:
        df_a = carregar_dados("Agendamentos")
        
        if df_a.empty:
            st.info("📭 Agenda vazia. Nenhum agendamento encontrado.")
        else:
            # Filtros
            col_filtro1, col_filtro2 = st.columns(2)
            with col_filtro1:
                filtro_data = st.date_input("Filtrar por data", value=None)
            with col_filtro2:
                filtro_cliente = st.text_input("Filtrar por cliente")
            
            # Aplicar filtros
            df_filtrado = df_a.copy()
            
            if filtro_data:
                df_filtrado = df_filtrado[df_filtrado['Data'] == filtro_data.strftime("%d/%m/%Y")]
            
            if filtro_cliente:
                df_filtrado = df_filtrado[df_filtrado['Cliente'].str.contains(filtro_cliente, case=False, na=False)]
            
            if df_filtrado.empty:
                st.info("Nenhum agendamento encontrado com os filtros aplicados.")
            else:
                for i, r in df_filtrado.iterrows():
                    st.markdown(f'''
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
                            <span style="font-size:14px; color:#888">({r.get('Placa', 'N/A')})</span>
                        </div>
                        <div style="margin-top:5px; font-size:14px; color:#ccc">
                            <i class="bi bi-person-fill"></i> {r.get('Cliente', 'N/A')}
                        </div>
                        <div style="margin-top:10px; padding-top:10px; border-top:1px solid #333; font-size:13px; color:#888">
                            🔧 {r.get('Servicos', 'N/A')}
                        </div>
                        <div style="margin-top:8px; font-size:12px; color:#666">
                            <i class="bi bi-person-badge"></i> {r.get('Executor', 'N/A')}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button(f"✅ Concluir Serviço", key=f"ok_{i}", use_container_width=True):
                            # 1. Total (Bruto)
                            total_bruto = float(r.get("Total", 0))
                            
                            # 2. Fundo de Caixa (10% do BRUTO)
                            fundo = total_bruto * 0.10
                            
                            # 3. Comissão (40% do BRUTO se for Equipe)
                            comis = total_bruto * 0.40 if "Equipe" in r.get("Executor", "") else 0.0
                            
                            # 4. Lucro Líquido (O que sobra)
                            lucro = total_bruto - fundo - comis
                            
                            venda = {
                                "Data": r.get("Data", ""),
                                "Cliente": r.get("Cliente", ""),
                                "Carro": r.get("Veiculo", ""),
                                "Placa": r.get("Placa", ""),
                                "Serviços": r.get("Servicos", ""),
                                "Total": total_bruto,
                                "Status": "Concluído",
                                "Funcionario": r.get("Executor", ""),
                                "Valor Comissao": comis,
                                "Fundo Caixa": fundo,
                                "Lucro Liquido": lucro,
                                "Status Comissao": "Pendente" if comis > 0 else "N/A",
                                "Categoria": r.get("Categoria", ""),
                                "DataConclusao": datetime.now().strftime("%d/%m/%Y %H:%M")
                            }
                            
                            salvar_no_google("Vendas", venda)
                            excluir_agendamento(i)
                            
                            log_acao("Concluir Serviço", f"Cliente: {r.get('Cliente', '')} | Valor: {total_bruto}")
                            enviar_notificacao('success', f'Serviço concluído: {r.get("Cliente", "")} - {formatar_moeda(total_bruto)}')
                            
                            st.success("Serviço concluído e movido para vendas!")
                            t_sleep.sleep(1)
                            st.rerun()
                    
                    with c_btn2:
                        if st.button(f"🗑️ Cancelar", key=f"del_{i}", use_container_width=True, type="secondary"):
                            excluir_agendamento(i)
                            st.warning("Agendamento excluído.")
                            log_acao("Cancelar Agendamento", f"Cliente: {r.get('Cliente', '')}")
                            enviar_notificacao('warning', f'Agendamento cancelado: {r.get("Cliente", "")}')
                            t_sleep.sleep(1)
                            st.rerun()
                
                # Estatísticas rápidas
                st.markdown("---")
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Total Agendamentos", len(df_filtrado))
                with col_stat2:
                    valor_total = df_filtrado['Total'].astype(float).sum()
                    st.metric("Valor Total", formatar_moeda(valor_total))
                with col_stat3:
                    equipe_count = len(df_filtrado[df_filtrado['Executor'].str.contains('Equipe', na=False)])
                    st.metric("Com Equipe", equipe_count)

# ==============================================================================
# --- PÁGINA DESPESAS (MELHORADA) ---
# ==============================================================================

def page_despesas():
    st.markdown('## <i class="bi bi-receipt" style="color: #D90429;"></i> Controle de Despesas', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Nova Despesa", "📋 Histórico"])
    
    with tab1:
        with st.form("form_desp", clear_on_submit=True):
            desc = st.text_input("Descrição*", placeholder="Ex: Compra de produtos de limpeza")
            val = st.number_input("Valor (R$)*", min_value=0.0, step=10.0)
            categoria = st.selectbox("Categoria*", 
                                   ["Produtos", "Manutenção", "Salários", "Contas", "Outros"])
            data_desp = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
            obs = st.text_area("Observações (opcional)")
            
            submit = st.form_submit_button("💾 Lançar Despesa", use_container_width=True)
            
            if submit:
                if not desc or val <= 0:
                    st.error("Preencha descrição e valor corretamente.")
                else:
                    dados = {
                        "Data": data_desp.strftime("%d/%m/%Y"),
                        "Descricao": desc,
                        "Valor": val,
                        "Categoria": categoria,
                        "Observacoes": obs,
                        "DataLancamento": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    
                    ok, msg = salvar_no_google("Despesas", dados)
                    
                    if ok:
                        st.success(f"✅ Despesa de {formatar_moeda(val)} registrada!")
                        log_acao("Nova Despesa", f"{desc} - {formatar_moeda(val)}")
                        enviar_notificacao('info', f'Nova despesa: {desc} - {formatar_moeda(val)}')
                        t_sleep.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Erro: {msg}")
    
    with tab2:
        df_d = carregar_dados("Despesas")
        
        if df_d.empty:
            st.info("Nenhuma despesa registrada ainda.")
        else:
            # Filtros
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                mes_filtro = st.selectbox("Mês", ["Todos"] + list(range(1, 13)))
            with col_f2:
                cat_filtro = st.selectbox("Categoria", ["Todas"] + list(df_d['Categoria'].unique() if 'Categoria' in df_d.columns else []))
            with col_f3:
                valor_min = st.number_input("Valor mínimo", min_value=0.0, value=0.0)
            
            # Aplicar filtros
            df_filtrado = df_d.copy()
            
            if mes_filtro != "Todos":
                df_filtrado['Data_dt'] = pd.to_datetime(df_filtrado['Data'], format='%d/%m/%Y', errors='coerce')
                df_filtrado = df_filtrado[df_filtrado['Data_dt'].dt.month == mes_filtro]
            
            if cat_filtro != "Todas" and 'Categoria' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['Categoria'] == cat_filtro]
            
            if 'Valor' in df_filtrado.columns:
                df_filtrado['Valor'] = pd.to_numeric(df_filtrado['Valor'], errors='coerce')
                df_filtrado = df_filtrado[df_filtrado['Valor'] >= valor_min]
            
            if df_filtrado.empty:
                st.info("Nenhuma despesa encontrada com os filtros aplicados.")
            else:
                # Estatísticas
                total_despesas = df_filtrado['Valor'].sum() if 'Valor' in df_filtrado.columns else 0
                media_despesas = df_filtrado['Valor'].mean() if 'Valor' in df_filtrado.columns else 0
                
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.metric("Total Filtrado", formatar_moeda(total_despesas))
                with col_stat2:
                    st.metric("Média por Despesa", formatar_moeda(media_despesas))
                
                # Lista de despesas
                st.markdown("---")
                for _, r in df_filtrado.iterrows():
                    cor_categoria = {
                        'Produtos': '#00B4DB',
                        'Manutenção': '#FF9800',
                        'Salários': '#D90429',
                        'Contas': '#28a745',
                        'Outros': '#8E2DE2'
                    }.get(r.get('Categoria', 'Outros'), '#666')
                    
                    st.markdown(f'''
                    <div style="background-color:#161616; border-radius:12px; padding:15px; margin-bottom:10px; border-left:5px solid {cor_categoria};">
                        <div style="display:flex; justify-content:space-between; align-items:center">
                            <div>
                                <h4 style="margin:0; color:white;">{r.get('Descricao', '')}</h4>
                                <div style="font-size:12px; color:#aaa; margin-top:5px">
                                    <i class="bi bi-calendar"></i> {r.get('Data', '')} • 
                                    <span style="background:{cor_categoria}20; color:{cor_categoria}; padding:2px 8px; border-radius:10px; font-size:11px">
                                        {r.get('Categoria', '')}
                                    </span>
                                </div>
                            </div>
                            <div style="font-size:20px; font-weight:700; color:#D90429">
                                {formatar_moeda(float(r.get('Valor', 0)))}
                            </div>
                        </div>
                        {f'<div style="margin-top:10px; font-size:13px; color:#888;"><i class="bi bi-chat-left-text"></i> {r.get("Observacoes", "")}</div>' if r.get('Observacoes') else ''}
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Exportar
                csv = df_filtrado.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar Despesas (CSV)",
                    data=csv,
                    file_name=f"despesas_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

# ==============================================================================
# --- PÁGINA HISTÓRICO (MELHORADA) ---
# ==============================================================================

def page_historico():
    st.markdown('## <i class="bi bi-clock-history" style="color: #FFC107;"></i> Garagem & Histórico Completo', unsafe_allow_html=True)
    
    df = carregar_dados("Vendas")
    
    if df.empty:
        st.info("📭 Nenhum serviço registrado ainda.")
        return
    
    # Filtros avançados
    with st.expander("🔍 Filtros Avançados", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            data_inicio = st.date_input("Data inicial", value=date.today().replace(day=1))
            data_fim = st.date_input("Data final", value=date.today())
        
        with col2:
            valor_min = st.number_input("Valor mínimo (R$)", min_value=0.0, value=0.0)
            valor_max = st.number_input("Valor máximo (R$)", min_value=0.0, value=10000.0)
        
        with col3:
            categorias = st.multiselect("Categorias", options=df['Categoria'].unique() if 'Categoria' in df.columns else [])
            status_opcoes = st.multiselect("Status", options=df['Status'].unique() if 'Status' in df.columns else [])
    
    # Campo de busca
    busca = st.text_input("🔍 Buscar (cliente, carro, placa ou serviço)...", 
                         placeholder="Ex: João, Fiat Toro, ABC-1234")
    
    # Aplicar filtros
    df_f = df.copy()
    
    # Converter datas
    if 'Data' in df_f.columns:
        df_f['Data_dt'] = pd.to_datetime(df_f['Data'], format='%d/%m/%Y', errors='coerce')
        
        if data_inicio:
            df_f = df_f[df_f['Data_dt'] >= pd.to_datetime(data_inicio)]
        
        if data_fim:
            df_f = df_f[df_f['Data_dt'] <= pd.to_datetime(data_fim)]
    
    # Filtro de valor
    if 'Total' in df_f.columns:
        df_f['Total'] = pd.to_numeric(df_f['Total'], errors='coerce')
        df_f = df_f[(df_f['Total'] >= valor_min) & (df_f['Total'] <= valor_max)]
    
    # Filtro de categorias
    if categorias and 'Categoria' in df_f.columns:
        df_f = df_f[df_f['Categoria'].isin(categorias)]
    
    # Filtro de status
    if status_opcoes and 'Status' in df_f.columns:
        df_f = df_f[df_f['Status'].isin(status_opcoes)]
    
    # Filtro de busca
    if busca:
        busca_lower = busca.lower()
        df_f = df_f[df_f.apply(lambda row: 
                              busca_lower in str(row.get('Cliente', '')).lower() or
                              busca_lower in str(row.get('Carro', '')).lower() or
                              busca_lower in str(row.get('Placa', '')).lower() or
                              busca_lower in str(row.get('Serviços', '')).lower(), 
                              axis=1)]
    
    # Ordenar do mais recente
    if 'Data_dt' in df_f.columns:
        df_f = df_f.sort_values('Data_dt', ascending=False)
    
    # Estatísticas
    total_servicos = len(df_f)
    valor_total = df_f['Total'].sum() if 'Total' in df_f.columns else 0
    ticket_medio = valor_total / total_servicos if total_servicos > 0 else 0
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Serviços Encontrados", total_servicos)
    with col_stat2:
        st.metric("Valor Total", formatar_moeda(valor_total))
    with col_stat3:
        st.metric("Ticket Médio", formatar_moeda(ticket_medio))
    
    st.write("---")
    
    # Exibir serviços
    if df_f.empty:
        st.info("Nenhum serviço encontrado com os filtros aplicados.")
    else:
        for _, r in df_f.iterrows():
            # Cor baseada no status
            cor_status = {
                'Concluído': '#28a745',
                'Orçamento/Pendente': '#ffc107',
                'Cancelado': '#dc3545'
            }.get(r.get('Status', 'Concluído'), '#666')
            
            # Verificar se tem comissão pendente
            tem_comissao_pendente = (
                'Status Comissao' in r and 
                r['Status Comissao'] == 'Pendente' and
                float(r.get('Valor Comissao', 0)) > 0
            )
            
            html_card = f'''
            <div class="history-card" style="border-left: 5px solid {cor_status}">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h3 style="margin: 0; font-size: 20px; color: white; font-weight: 700;">
                            {obter_icone_html(r.get("Categoria", ""))} {r.get("Carro", "N/A")}
                            {f'<span style="background:#D90429; color:white; padding:2px 8px; border-radius:10px; font-size:11px; margin-left:10px;">COMISSÃO PENDENTE</span>' if tem_comissao_pendente else ''}
                        </h3>
                        <p style="margin: 5px 0 0 0; color: #bbb; font-size: 14px;">
                            <i class="bi bi-person"></i> {r.get("Cliente", "N/A")} &nbsp;|&nbsp; {r.get("Placa", "N/A")}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <h2 style="margin: 0; color: #39FF14; font-weight: 700; font-size: 22px;">
                            {formatar_moeda(float(r.get("Total", 0)))}
                        </h2>
                        <span style="background-color: #222; padding: 4px 8px; border-radius: 6px; 
                                  font-size: 11px; text-transform: uppercase; letter-spacing: 1px; 
                                  color: #aaa; margin-top: 5px; display: inline-block;">
                            {r.get("Data", "N/A")}
                        </span>
                    </div>
                </div>
                <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid #333; color: #888; font-size: 13px;">
                    <i class="bi bi-tools"></i> {r.get("Serviços", "N/A")}
                </div>
                <div style="margin-top: 10px; display: flex; gap: 10px; font-size: 12px;">
                    <span style="background: {cor_status}20; color: {cor_status}; padding: 3px 8px; border-radius: 4px;">
                        {r.get("Status", "N/A")}
                    </span>
                    <span style="background: #00B4DB20; color: #00B4DB; padding: 3px 8px; border-radius: 4px;">
                        {r.get("Categoria", "N/A")}
                    </span>
                    <span style="background: #8E2DE220; color: #8E2DE2; padding: 3px 8px; border-radius: 4px;">
                        {r.get("Funcionario", "N/A")}
                    </span>
                </div>
                {f'<div style="margin-top: 10px; font-size: 12px; color: #ffc107;"><i class="bi bi-cash-coin"></i> Comissão Pendente: {formatar_moeda(float(r.get("Valor Comissao", 0)))}</div>' if tem_comissao_pendente else ''}
            </div>
            '''
            st.markdown(html_card, unsafe_allow_html=True)
        
        # Botão de exportação
        st.write("---")
        csv = df_f.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar Histórico (CSV)",
            data=csv,
            file_name=f"historico_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ==============================================================================
# --- ROTEADOR DE PÁGINAS ---
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
# --- RODAPÉ ---
# ==============================================================================
st.markdown('''
<div class="footer">
    Desenvolvido por <b>Jairan Jesus Matos</b> | JM Detail System © 2026 | 
    <span style="color: #D90429;">v3.0 • Segurança • Performance</span>
</div>
''', unsafe_allow_html=True)

# ==============================================================================
# --- SCRIPT JS PARA NOTIFICAÇÕES ---
# ==============================================================================
st.markdown('''
<script>
// Função para limpar notificações (simulada)
function limparNotificacoes() {
    // Em um sistema real, aqui seria uma chamada AJAX
    alert("Notificações limpas (em produção salvaria no servidor)");
    document.getElementById('notif-popup').style.display = 'none';
}

// Fechar popup ao clicar fora
document.addEventListener('click', function(event) {
    var popup = document.getElementById('notif-popup');
    var badge = document.querySelector('.notification-badge');
    var button = document.querySelector('button[onclick*="notif-popup"]');
    
    if (popup && !popup.contains(event.target) && 
        !badge.contains(event.target) && 
        button && !button.contains(event.target)) {
        popup.style.display = 'none';
    }
});

// Atalhos de teclado
document.addEventListener('keydown', function(e) {
    // Ctrl + 1 = Dashboard
    if (e.ctrlKey && e.key === '1') {
        window.location.search = '?nav=DASHBOARD';
    }
    // Ctrl + 2 = Agenda
    if (e.ctrlKey && e.key === '2') {
        window.location.search = '?nav=AGENDA';
    }
    // Ctrl + 3 = Financeiro
    if (e.ctrlKey && e.key === '3') {
        window.location.search = '?nav=FINANCEIRO';
    }
});
</script>
''', unsafe_allow_html=True)
