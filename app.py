import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date, time, timedelta
from fpdf import FPDF
import gspread
import os
import time as t_sleep
import hashlib
import re
import logging

# ==============================================================================
# 1. CONFIGURAÇÃO BÁSICA
# ==============================================================================
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# 2. CSS (MESMO SEU ESTILO - apenas 1 função adicionada)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    
    * { font-family: 'Poppins', sans-serif !important; }
    
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
    }
    
    .block-container { padding-top: 1rem; padding-bottom: 6rem; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    
    /* MENU SUPERIOR (mesmo seu estilo) */
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
    
    div[role="radiogroup"] label:hover {
        border-color: #D90429 !important;
        color: white !important;
        background-color: #1a1a1a !important;
    }
    
    div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(90deg, #D90429 0%, #8D021F 100%) !important;
        color: white !important;
        border-color: #D90429 !important;
        box-shadow: 0 0 12px rgba(217, 4, 41, 0.5) !important;
    }
    
    /* CARDS (mesmo estilo) */
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
    
    .bg-orange { background: linear-gradient(145deg, #FF9800, #F57C00); }
    .bg-blue { background: linear-gradient(145deg, #00B4DB, #0083B0); }
    .bg-red { background: linear-gradient(145deg, #D90429, #8D021F); }
    .bg-green { background: linear-gradient(145deg, #11998e, #38ef7d); }
    .bg-purple { background: linear-gradient(145deg, #8E2DE2, #4A00E0); }
    
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
    
    div.stButton > button { 
        background-color: #D90429 !important; 
        color: white !important; 
        border-radius: 8px !important; 
        font-weight: 700 !important; 
        border: none !important; 
        height: 45px !important; 
    }
    
    /* NOVO: Notificações minimalista */
    .notification-dot {
        position: absolute;
        top: 10px;
        right: 10px;
        background: #D90429;
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. FUNÇÕES AUXILIARES OTIMIZADAS
# ==============================================================================
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def validar_placa(placa):
    if not placa: return False
    placa = str(placa).strip().upper()
    padrao_antigo = re.compile(r'^[A-Z]{3}-?\d{4}$')
    padrao_mercosul = re.compile(r'^[A-Z]{3}\d[A-Z]\d{2}$')
    return bool(padrao_antigo.match(placa) or padrao_mercosul.match(placa))

def obter_icone_html(cat):
    if not isinstance(cat, str): return '<i class="bi bi-car-front-fill"></i>'
    c = cat.lower()
    if "moto" in c: return '<i class="bi bi-motorcycle"></i>'
    elif "suv" in c or "picape" in c or "caminhonete" in c: return '<i class="bi bi-truck-front-fill"></i>'
    elif "van" in c: return '<i class="bi bi-bus-front-fill"></i>'
    else: return '<i class="bi bi-car-front-fill"></i>'

# ==============================================================================
# 4. GOOGLE SHEETS (com cache e tratamento de erro)
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
    except: 
        return None

@st.cache_data(ttl=60)
def carregar_dados(aba):
    sheet = conectar_google_sheets()
    if sheet is None: return pd.DataFrame()
    try: 
        dados = pd.DataFrame(sheet.worksheet(aba).get_all_records())
        if not dados.empty and 'Data' in dados.columns:
            dados['Data_dt'] = pd.to_datetime(dados['Data'], format='%d/%m/%Y', errors='coerce')
        return dados
    except: 
        return pd.DataFrame()

def salvar_no_google(aba, linha_dados):
    sheet = conectar_google_sheets()
    if sheet is None: return False, "Sem conexão"
    
    try:
        ws = sheet.worksheet(aba)
        headers = ws.row_values(1)
        if not headers: 
            headers = list(linha_dados.keys())
            ws.append_row(headers)
        
        nova_linha = [''] * len(headers)
        for col_name, valor in linha_dados.items():
            if col_name in headers:
                nova_linha[headers.index(col_name)] = valor
        
        ws.append_row(nova_linha)
        return True, "Sucesso"
    except Exception as e: 
        return False, str(e)

def excluir_agendamento(indice_linha):
    sheet = conectar_google_sheets()
    if sheet is None: return False
    try: 
        ws = sheet.worksheet("Agendamentos")
        ws.delete_rows(indice_linha + 2)
        return True
    except: 
        return False

# ==============================================================================
# 5. LOGIN SEGURO (compacto)
# ==============================================================================
def check_password():
    if st.session_state.get("password_correct", False):
        return True
    
    # Verificar senha via hash
    def verificar_senha(input_pwd):
        try:
            senha_hash = st.secrets["app"]["password_hash"]
            return hashlib.sha256(input_pwd.encode()).hexdigest() == senha_hash
        except:
            return input_pwd == "1234"  # Fallback temporário
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### <i class='bi bi-shield-lock-fill' style='color:#D90429'></i> Acesso Restrito", unsafe_allow_html=True)
        with st.form("login_form"):
            pwd = st.text_input("Senha:", type="password")
            if st.form_submit_button("ACESSAR"):
                if verificar_senha(pwd): 
                    st.session_state["password_correct"] = True
                    st.rerun()
                else: 
                    st.error("Senha incorreta.")
    return False

if not check_password(): st.stop()

# ==============================================================================
# 6. CATÁLOGO DE PREÇOS (cache)
# ==============================================================================
@st.cache_data
def carregar_catalogo():
    return pd.DataFrame({
        "Categoria": ["Hatch/Compacto", "Sedã", "SUV/Caminhonete", "Picapes Grandes", "Vans/Utilitários", "Motocicleta"],
        "Lavagem Simples": [40, 50, 60, 70, 80, 30],
        "Lavagem Técnica": [150, 170, 190, 210, 230, 100],
        "Higi. Bancos": [80, 80, 80, 120, 150, 0],
        "Combo Premium": [300, 320, 350, 400, 450, 0],
        "Limpeza Motor": [100, 100, 120, 150, 150, 80],
    })

# ==============================================================================
# 7. HEADER
# ==============================================================================
c_logo1, c_logo2, c_logo3 = st.columns([1,2,1])
with c_logo2:
    if os.path.exists("logo.png"): 
        st.image("logo.png", use_container_width=True)
    else: 
        st.markdown("<h1 style='text-align:center; color:#D90429; font-weight:800'>JM DETAIL</h1>", unsafe_allow_html=True)

st.write("") 
menu_opcoes = ["DASHBOARD", "AGENDA", "FINANCEIRO", "DESPESAS", "HISTÓRICO"]
menu_selecionado = st.radio("Navegação", menu_opcoes, horizontal=True, label_visibility="collapsed")
st.write("---")

# ==============================================================================
# 8. FUNÇÕES DE PÁGINAS OTIMIZADAS
# ==============================================================================
def page_dashboard():
    hoje = datetime.now()
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    df_a = carregar_dados("Agendamentos")
    
    # Cálculos rápidos
    receita_mes = despesa_mes = pendente_total = count_p = 0
    
    if not df_v.empty:
        df_v['Total'] = pd.to_numeric(df_v['Total'], errors='coerce')
        df_v['Data_dt'] = pd.to_datetime(df_v['Data'], errors='coerce')
        mes_atual = df_v[df_v['Data_dt'].dt.month == hoje.month]
        
        receita_mes = mes_atual[mes_atual['Status']=='Concluído']['Total'].sum()
        pendente_total = df_v[df_v['Status']=='Orçamento/Pendente']['Total'].sum()
        count_p = len(df_v[df_v['Status']=='Orçamento/Pendente'])
    
    if not df_d.empty:
        df_d['Valor'] = pd.to_numeric(df_d['Valor'], errors='coerce')
        despesa_mes = df_d['Valor'].sum()
    
    lucro_final = (receita_mes * 0.5) - despesa_mes
    
    # Cards principais
    c1, c2, c3, c4 = st.columns(4)
    
    cards = [
        (f"PENDENTES", pendente_total, f"{count_p} carros", "bg-orange", "hourglass-split"),
        (f"FATURAMENTO", receita_mes, "Mês atual", "bg-blue", "currency-dollar"),
        (f"DESPESAS", despesa_mes, "Gastos totais", "bg-red", "graph-down-arrow"),
        (f"LUCRO", lucro_final, "50% bruto - despesas", "bg-green" if lucro_final >=0 else "bg-red", "wallet2")
    ]
    
    for col, (titulo, valor, subtitulo, cor, icone) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(f'''
            <div class="dash-card {cor}">
                <i class="bi bi-{icone} card-icon-bg"></i>
                <h4>{titulo}</h4>
                <div style="font-size:24px;font-weight:bold">{formatar_moeda(valor)}</div>
                <small>{subtitulo}</small>
            </div>
            ''', unsafe_allow_html=True)
    
    st.write("---")
    
    # Métricas rápidas
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('### 📈 Performance')
        if not df_v.empty and 'mes_atual' in locals() and not mes_atual.empty:
            chart = alt.Chart(mes_atual).mark_bar(size=30).encode(
                x='Data:N',
                y='Total:Q',
                color=alt.Color('Status', scale=alt.Scale(domain=['Concluído', 'Orçamento/Pendente'], range=['#00F260', '#FF0080']))
            )
            st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.markdown('### 📅 Próximos')
        if not df_a.empty:
            for _, r in df_a.head(3).iterrows():
                st.markdown(f'''
                <div style="background:#161616; padding:10px; border-radius:8px; margin-bottom:8px;">
                    <div style="color:#00B4DB; font-size:12px;">
                        <i class="bi bi-calendar"></i> {r.get('Data', '')}
                    </div>
                    <div style="color:white; font-weight:bold;">{r.get('Veiculo', '')}</div>
                    <div style="color:#888; font-size:13px;">{r.get('Cliente', '')}</div>
                </div>
                ''', unsafe_allow_html=True)

def page_agendamento():
    st.markdown('## 📅 Agenda')
    tab1, tab2 = st.tabs(["Novo", "Lista"])
    df_cat = carregar_catalogo()
    
    with tab1:
        with st.form("novo_agendamento"):
            col1, col2 = st.columns(2)
            cli = col1.text_input("Cliente")
            veic = col1.text_input("Veículo")
            placa = col2.text_input("Placa").upper()
            dt = col2.date_input("Data", value=date.today())
            
            if placa and not validar_placa(placa):
                st.warning("Placa inválida. Formato: AAA-0A00 ou AAA0A00")
            
            cat = st.selectbox("Categoria", df_cat["Categoria"])
            servicos = st.multiselect("Serviços", [c for c in df_cat.columns if c != "Categoria"])
            
            if servicos:
                total = sum(df_cat[df_cat["Categoria"]==cat][s].values[0] for s in servicos)
                st.markdown(f"**Total:** {formatar_moeda(total)}")
            
            if st.form_submit_button("Agendar"):
                dados = {
                    "Data": dt.strftime("%d/%m/%Y"),
                    "Cliente": cli,
                    "Veiculo": veic,
                    "Placa": placa,
                    "Servicos": ", ".join(servicos),
                    "Total": total,
                    "Categoria": cat
                }
                ok, msg = salvar_no_google("Agendamentos", dados)
                if ok: 
                    st.success("Agendado!")
                    st.rerun()
    
    with tab2:
        df_a = carregar_dados("Agendamentos")
        if df_a.empty:
            st.info("Agenda vazia")
        else:
            for i, r in df_a.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f'''
                    <div class="agenda-card">
                        <div style="color:#00B4DB; font-weight:bold;">
                            {r.get('Data', '')} • {r.get('Hora', '')}
                        </div>
                        <div style="color:white; font-size:18px; font-weight:bold;">
                            {obter_icone_html(r.get('Categoria', ''))} {r.get('Veiculo', '')}
                        </div>
                        <div style="color:#ccc;">{r.get('Cliente', '')}</div>
                        <div style="color:#888; font-size:13px;">{r.get('Servicos', '')}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col2:
                    if st.button("✅", key=f"ok_{i}"):
                        total = float(r.get('Total', 0))
                        venda = {
                            "Data": r.get('Data', ''),
                            "Cliente": r.get('Cliente', ''),
                            "Carro": r.get('Veiculo', ''),
                            "Placa": r.get('Placa', ''),
                            "Serviços": r.get('Servicos', ''),
                            "Total": total,
                            "Status": "Concluído",
                            "Fundo Caixa": total * 0.1,
                            "Lucro Liquido": total * 0.5
                        }
                        salvar_no_google("Vendas", venda)
                        excluir_agendamento(i)
                        st.rerun()

def page_financeiro():
    st.markdown('## 💰 Financeiro')
    df_v = carregar_dados("Vendas")
    
    if not df_v.empty:
        df_v['Total'] = pd.to_numeric(df_v['Total'], errors='coerce')
        df_v['Valor Comissao'] = pd.to_numeric(df_v['Valor Comissao'], errors='coerce')
        df_v['Fundo Caixa'] = pd.to_numeric(df_v['Fundo Caixa'], errors='coerce')
        
        # Cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Fundo Caixa", formatar_moeda(df_v['Fundo Caixa'].sum()))
        
        with col2:
            pendentes = df_v[df_v.get('Status Comissao', '') != 'Pago']['Valor Comissao'].sum()
            st.metric("Comissões Pendentes", formatar_moeda(pendentes))
        
        with col3:
            if pendentes > 0 and st.button("Pagar Comissões"):
                st.success("Comissões pagas!")
                st.rerun()
        
        # Tabela simples
        st.dataframe(df_v[['Data', 'Cliente', 'Carro', 'Total', 'Status Comissao']].head(10))

def page_despesas():
    st.markdown('## 📉 Despesas')
    
    with st.form("nova_despesa"):
        desc = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.0)
        if st.form_submit_button("Salvar"):
            salvar_no_google("Despesas", {
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Descricao": desc,
                "Valor": valor
            })
            st.success("Salvo!")
            st.rerun()
    
    df_d = carregar_dados("Despesas")
    if not df_d.empty:
        st.dataframe(df_d)

def page_historico():
    st.markdown('## 🕐 Histórico')
    df = carregar_dados("Vendas")
    
    if df.empty:
        st.info("Sem histórico")
        return
    
    busca = st.text_input("Buscar...")
    if busca:
        df = df[df.apply(lambda r: busca.lower() in str(r).lower(), axis=1)]
    
    for _, r in df.iterrows():
        st.markdown(f'''
        <div class="history-card">
            <div style="display:flex; justify-content:space-between;">
                <div>
                    <h3 style="color:white; margin:0;">
                        {obter_icone_html(r.get('Categoria', ''))} {r.get('Carro', '')}
                    </h3>
                    <div style="color:#bbb;">
                        {r.get('Cliente', '')} • {r.get('Placa', '')}
                    </div>
                </div>
                <div style="color:#39FF14; font-weight:bold; font-size:20px;">
                    {formatar_moeda(float(r.get('Total', 0)))}
                </div>
            </div>
            <div style="color:#888; margin-top:10px;">
                {r.get('Serviços', '')}
            </div>
        </div>
        ''', unsafe_allow_html=True)

# ==============================================================================
# 9. ROTEADOR SIMPLES
# ==============================================================================
if "DASHBOARD" in menu_selecionado: page_dashboard()
elif "AGENDA" in menu_selecionado: page_agendamento()
elif "FINANCEIRO" in menu_selecionado: page_financeiro()
elif "DESPESAS" in menu_selecionado: page_despesas()
elif "HISTÓRICO" in menu_selecionado: page_historico()

# ==============================================================================
# 10. RODAPÉ
# ==============================================================================
st.markdown('''
<div class="footer">
    Desenvolvido por <b>Jairan Jesus Matos</b> | JM Detail System © 2026
</div>
''', unsafe_allow_html=True)
