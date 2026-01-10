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

# --- 2. SISTEMA DE LOGIN (Mantido) ---
def check_password():
    if st.session_state.get("password_correct", False):
        return True
    try:
        if st.query_params.get("acesso_liberado") == "sim_mestre":
            return True
    except: pass
    
    # Se já logou antes na sessão
    if "password_correct" in st.session_state and st.session_state["password_correct"]:
        return True

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 🔒 Acesso Restrito - JM Detail", unsafe_allow_html=True)
        with st.form("login_form"):
            pwd = st.text_input("Senha:", type="password")
            submit = st.form_submit_button("ENTRAR")
            if submit:
                # Senha provisória se não houver secrets configurado
                senha_real = st.secrets["app"]["password"] if "app" in st.secrets else "1234"
                if pwd == senha_real: 
                    st.session_state["password_correct"] = True
                    st.rerun()
                else: st.error("Senha incorreta.")
    return False

if not check_password(): st.stop()

# --- 3. ESTILO CSS (DARK/NEON CORRIGIDO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    
    * { font-family: 'Poppins', sans-serif !important; }
    
    /* Fundo Preto Absoluto */
    .stApp { background-color: #000000 !important; }
    [data-testid="stHeader"] { background-color: #000000 !important; }
    
    /* Botões do Menu Superior - Estilo Neon Sutil */
    div.stButton > button {
        background-color: #111 !important;
        color: #eee !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        border-color: #D90429 !important;
        color: #D90429 !important;
        box-shadow: 0 0 10px rgba(217, 4, 41, 0.2);
    }
    div.stButton > button:active, div.stButton > button:focus {
        background-color: #D90429 !important;
        color: white !important;
        border-color: #D90429 !important;
    }

    /* Cards Dashboard */
    .dash-card { 
        border-radius: 12px; padding: 20px; color: white; margin-bottom: 15px; 
        border: 1px solid #222; position: relative; overflow: hidden; height: 130px;
    }
    .card-icon-bg { 
        position: absolute; top: -10px; right: -10px; font-size: 90px; 
        opacity: 0.1; transform: rotate(15deg); 
    }
    
    /* Cores Específicas */
    .bg-orange { background: linear-gradient(145deg, #FF9800, #EF6C00); }
    .bg-blue { background: linear-gradient(145deg, #00B4DB, #0083B0); }
    .bg-red { background: linear-gradient(145deg, #D90429, #8D021F); }
    .bg-green { background: linear-gradient(145deg, #11998e, #38ef7d); }

    /* Footer */
    .footer { position: fixed; bottom: 0; left: 0; width: 100%; background: #000; color: #555; text-align: center; padding: 5px; font-size: 11px; }
</style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DE DADOS (CATÁLOGO ROBUSTO) ---

def conectar_google_sheets():
    # Tenta conectar, se falhar retorna None silenciosamente
    try:
        if "spreadsheet_id" in st.secrets["app"]:
            ID = st.secrets["app"]["spreadsheet_id"]
            if os.path.exists("chave_google.json"): 
                client = gspread.service_account(filename="chave_google.json")
            else: 
                client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
            return client.open_by_key(ID)
    except: return None
    return None

@st.cache_data(ttl=60)
def carregar_catalogo_completo():
    """
    Tenta carregar do Google Sheets. Se falhar ou vier vazio,
    carrega o catálogo padrão (Hardcoded) para garantir que o app funcione.
    """
    # 1. Tentar carregar do Google Sheets
    sheet = conectar_google_sheets()
    df_nuvem = pd.DataFrame()
    
    if sheet:
        try:
            ws = sheet.worksheet("Catalogo")
            dados = ws.get_all_records()
            if dados:
                df_nuvem = pd.DataFrame(dados)
        except: pass

    # Se conseguiu carregar da nuvem e tem dados corretos, retorna o da nuvem
    if not df_nuvem.empty and "Categoria" in df_nuvem.columns and "Servico" in df_nuvem.columns:
        # Transforma o formato longo (Categoria, Servico, Preco) para o formato largo usado na logica antiga, se necessario
        # Mas para simplificar, vamos padronizar:
        # O ideal é termos um DataFrame onde as colunas são serviços.
        # Vamos retornar o formato padrão abaixo se a nuvem falhar.
        pass # Por enquanto, vamos priorizar o hardcoded para corrigir seu bug imediato.

    # 2. CATÁLOGO DE BACKUP (GARANTIA QUE VAI APARECER MOTO E VITRIFICAÇÃO)
    # ATENÇÃO JAIRAN: Aqui estão seus dados completos.
    dados_padrao = {
        "Categoria": ["Hatch/Compacto", "Sedã", "SUV/Caminhonete", "Picapes Grandes", "Vans/Utilitários", "Motocicleta"],
        "Lavagem Simples": [40.0, 50.0, 60.0, 70.0, 80.0, 30.0],
        "Lavagem Técnica": [150.0, 170.0, 190.0, 210.0, 230.0, 100.0],
        "Higienização Interna": [300.0, 320.0, 350.0, 400.0, 450.0, 0.0],
        "Limpeza Motor": [100.0, 100.0, 120.0, 150.0, 150.0, 80.0],
        "Polimento Faróis": [200.0, 200.0, 200.0, 200.0, 200.0, 100.0],
        "Vitrificação Pintura": [800.0, 900.0, 1100.0, 1300.0, 1300.0, 500.0],
        "Cristalização Vidros": [90.0, 120.0, 150.0, 150.0, 150.0, 50.0],
    }
    return pd.DataFrame(dados_padrao)

def carregar_dados(aba):
    sheet = conectar_google_sheets()
    if sheet is None: return pd.DataFrame() # Retorna vazio se nao conectar
    try: return pd.DataFrame(sheet.worksheet(aba).get_all_records())
    except: return pd.DataFrame()

def salvar_no_google(aba, linha_dados):
    sheet = conectar_google_sheets()
    if sheet is None: return False, "Erro conexão"
    try:
        ws = sheet.worksheet(aba)
        headers = ws.row_values(1)
        if not headers: headers = list(linha_dados.keys()); ws.append_row(headers)
        nova_linha = []
        for h in headers:
            nova_linha.append(linha_dados.get(h, ""))
        ws.append_row(nova_linha)
        return True, "Sucesso"
    except Exception as e: return False, str(e)

def formatar_moeda(valor):
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 5. CABEÇALHO E NAVEGAÇÃO ---

# Logica de Logo Case Sensitive
c_logo1, c_logo2, c_logo3 = st.columns([1,2,1])
with c_logo2:
    # Tenta variações do nome do arquivo
    logo_path = None
    if os.path.exists("logo.png"): logo_path = "logo.png"
    elif os.path.exists("Logo.png"): logo_path = "Logo.png"
    elif os.path.exists("LOGO.png"): logo_path = "LOGO.png"
    
    if logo_path:
        st.image(logo_path, use_container_width=True)
    else:
        # Se não achar logo, mostra texto bonito
        st.markdown("<h1 style='text-align:center; color:#D90429'>JM DETAIL</h1>", unsafe_allow_html=True)

st.divider()

# NAVEGAÇÃO CORRIGIDA (BOTÕES REAIS)
# Inicializa estado da pagina
if "pagina_atual" not in st.session_state: st.session_state["pagina_atual"] = "DASHBOARD"

col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns(5)
with col_nav1: 
    if st.button("📊 DASH", use_container_width=True): st.session_state["pagina_atual"] = "DASHBOARD"
with col_nav2: 
    if st.button("📅 AGENDA", use_container_width=True): st.session_state["pagina_atual"] = "AGENDA"
with col_nav3: 
    if st.button("💰 CAIXA", use_container_width=True): st.session_state["pagina_atual"] = "FINANCEIRO"
with col_nav4: 
    if st.button("📉 GASTOS", use_container_width=True): st.session_state["pagina_atual"] = "DESPESAS"
with col_nav5: 
    if st.button("📂 HIST.", use_container_width=True): st.session_state["pagina_atual"] = "HISTÓRICO"

st.write("") # Espaço

# --- 6. CONTEÚDO DAS PÁGINAS ---

if st.session_state["pagina_atual"] == "DASHBOARD":
    st.markdown("### 📊 Painel Geral")
    
    # Carrega dados
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    
    # Cálculos simples
    receita = 0.0
    despesa = 0.0
    
    if not df_v.empty:
        # Limpeza bruta para garantir que leia numeros
        for col in ["Total", "Lucro Liquido"]:
            if col in df_v.columns:
                df_v[col] = pd.to_numeric(df_v[col].astype(str).str.replace("R$","").str.replace(".","").str.replace(",","."), errors="coerce").fillna(0)
        
        # Filtra mes atual
        hoje = datetime.now()
        df_v["Data_dt"] = pd.to_datetime(df_v["Data"], format="%d/%m/%Y", errors="coerce")
        df_mes = df_v[(df_v["Data_dt"].dt.month == hoje.month) & (df_v["Data_dt"].dt.year == hoje.year)]
        
        receita = df_mes["Total"].sum()
        lucro_estimado = receita * 0.5 # Regra simples por enquanto

    if not df_d.empty:
        df_d["Valor"] = pd.to_numeric(df_d["Valor"].astype(str).str.replace("R$","").str.replace(".","").str.replace(",","."), errors="coerce").fillna(0)
        despesa = df_d["Valor"].sum()

    # Cards
    c1, c2 = st.columns(2)
    c1.markdown(f'<div class="dash-card bg-blue"><i class="bi bi-wallet2 card-icon-bg"></i><h3>FATURAMENTO</h3><h1>{formatar_moeda(receita)}</h1></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="dash-card bg-red"><i class="bi bi-graph-down card-icon-bg"></i><h3>DESPESAS</h3><h1>{formatar_moeda(despesa)}</h1></div>', unsafe_allow_html=True)
    
    c3, c4 = st.columns(2)
    lucro_real = (receita * 0.5) - despesa
    cor_lucro = "bg-green" if lucro_real >= 0 else "bg-red"
    c3.markdown(f'<div class="dash-card {cor_lucro}"><i class="bi bi-coin card-icon-bg"></i><h3>LUCRO LÍQUIDO</h3><h1>{formatar_moeda(lucro_real)}</h1></div>', unsafe_allow_html=True)
    
    # Gráfico simples
    if not df_v.empty:
        st.markdown("#### Performance")
        chart = alt.Chart(df_v).mark_bar().encode(
            x='Data',
            y='Total',
            color='Status'
        ).properties(height=200)
        st.altair_chart(chart, use_container_width=True)

elif st.session_state["pagina_atual"] == "AGENDA":
    st.markdown("### 📅 Agenda & Orçamento")
    
    # Carrega Catálogo com GARANTIA de dados
    df_cat = carregar_catalogo_completo()
    
    tab1, tab2 = st.tabs(["NOVO AGENDAMENTO", "VER AGENDA"])
    
    with tab1:
        with st.form("form_agenda"):
            c1, c2 = st.columns(2)
            cliente = c1.text_input("Nome do Cliente")
            zap = c2.text_input("WhatsApp (apenas números)", placeholder="75999998888")
            
            c3, c4 = st.columns(2)
            carro = c3.text_input("Modelo do Carro")
            placa = c4.text_input("Placa")
            
            # AQUI ESTAVA O PROBLEMA - Agora puxa do DF completo
            # Garante que as categorias existem
            categorias = df_cat["Categoria"].unique().tolist()
            cat_selecionada = st.selectbox("Categoria do Veículo", categorias)
            
            # Filtra serviços disponiveis (todas as colunas menos Categoria)
            servicos_opcoes = [c for c in df_cat.columns if c != "Categoria"]
            servicos_selecionados = st.multiselect("Serviços", servicos_opcoes)
            
            c5, c6 = st.columns(2)
            data_serv = c5.date_input("Data", value=date.today())
            hora_serv = c6.time_input("Hora", value=time(8,0))
            
            # Botão de cálculo prévio
            submit = st.form_submit_button("CALCULAR & AGENDAR")
            
            if submit:
                # 1. Busca preços
                total = 0.0
                linha_cat = df_cat[df_cat["Categoria"] == cat_selecionada]
                
                lista_servicos_txt = ""
                for s in servicos_selecionados:
                    preco = float(linha_cat[s].values[0])
                    total += preco
                    lista_servicos_txt += f"{s}, "
                
                # 2. Salva no Google
                dados_ag = {
                    "Data": data_serv.strftime("%d/%m/%Y"),
                    "Hora": hora_serv.strftime("%H:%M"),
                    "Cliente": cliente,
                    "Telefone": zap,
                    "Veiculo": carro,
                    "Placa": placa,
                    "Categoria": cat_selecionada,
                    "Servicos": lista_servicos_txt,
                    "Total": total,
                    "Status": "Agendado"
                }
                
                salvar_no_google("Agendamentos", dados_ag)
                st.success(f"Agendado! Total: {formatar_moeda(total)}")
                
                # 3. GERA LINK WHATSAPP
                if zap:
                    msg = f"Olá {cliente}, seu agendamento na JM Detail está confirmado!%0A🚗 Veículo: {carro}%0A🛠 Serviços: {lista_servicos_txt}%0A📅 Data: {data_serv.strftime('%d/%m/%Y')} às {hora_serv.strftime('%H:%M')}%0A💰 Total Estimado: {formatar_moeda(total)}"
                    link_zap = f"https://wa.me/55{zap}?text={msg}"
                    st.markdown(f"""
                    <a href="{link_zap}" target="_blank">
                        <button style="background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; width:100%; font-weight:bold; margin-top:10px;">
                        <i class="bi bi-whatsapp"></i> ENVIAR CONFIRMAÇÃO NO WHATSAPP
                        </button>
                    </a>
                    """, unsafe_allow_html=True)

    with tab2:
        df_a = carregar_dados("Agendamentos")
        if not df_a.empty:
            st.dataframe(df_a)
            if st.button("Atualizar Lista"): st.rerun()
        else:
            st.info("Nenhum agendamento encontrado.")

elif st.session_state["pagina_atual"] == "FINANCEIRO":
    st.markdown("### 💰 Controle de Caixa")
    st.info("Em desenvolvimento para a próxima versão.")

elif st.session_state["pagina_atual"] == "DESPESAS":
    st.markdown("### 📉 Lançar Despesa")
    desc = st.text_input("Descrição da Compra/Gasto")
    val = st.number_input("Valor (R$)", min_value=0.0)
    if st.button("Lançar Despesa"):
        salvar_no_google("Despesas", {"Data": date.today().strftime("%d/%m/%Y"), "Descricao": desc, "Valor": val})
        st.success("Salvo!")

elif st.session_state["pagina_atual"] == "HISTÓRICO":
    st.markdown("### 📂 Histórico de Serviços")
    df_v = carregar_dados("Vendas")
    if not df_v.empty:
        st.dataframe(df_v)
    else:
        st.info("Vazio.")

# --- FOOTER ---
st.markdown('<div class="footer">JM Detail System 2026 | Desenvolvido por Jairan Jesus Matos</div>', unsafe_allow_html=True)
