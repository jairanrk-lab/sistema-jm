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

# ==============================================================================
# 1. CONFIGURAÇÃO
# ==============================================================================
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# 2. CSS (MESMO SEU ESTILO)
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
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. FUNÇÕES AUXILIARES
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
# 4. GERADOR DE PDF COM LOGO E ASSINATURA
# ==============================================================================
def gerar_pdf_orcamento(cliente, carro, placa, data_servico, servicos, total_bruto):
    """Gera PDF do orçamento com logo e assinatura"""
    pdf = FPDF()
    pdf.add_page()
    
    # LOGO NO TOPO (usando seu logo.png)
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=55, y=10, w=100)
        pdf.ln(40)
    else:
        pdf.ln(20)
    
    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "JM DETAIL - ORÇAMENTO", ln=True, align='C')
    
    # Informações do cliente
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Cliente: {cliente}", ln=True)
    pdf.cell(0, 8, f"Veículo: {carro} | Placa: {placa}", ln=True)
    pdf.cell(0, 8, f"Data: {data_servico}", ln=True)
    pdf.ln(10)
    
    # Serviços
    pdf.set_font("Arial", "B", 12)
    pdf.cell(140, 10, "Serviços Contratados", border=1, fill=True)
    pdf.cell(50, 10, "Valor", border=1, ln=True, fill=True, align='C')
    
    pdf.set_font("Arial", "", 11)
    for servico in servicos.split(", "):
        pdf.cell(140, 8, servico[:50], border=1)
        pdf.cell(50, 8, "", border=1, ln=True, align='C')
    
    pdf.ln(5)
    
    # CÁLCULO DETALHADO (SUA REGRA)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Detalhamento Financeiro:", ln=True)
    pdf.set_font("Arial", "", 11)
    
    # 1. Valor Bruto
    pdf.cell(100, 8, "Valor Bruto do Serviço:")
    pdf.cell(40, 8, formatar_moeda(total_bruto), ln=True, align='R')
    
    # 2. Fundo Caixa (10%)
    fundo_caixa = total_bruto * 0.10
    pdf.cell(100, 8, "Fundo Caixa (10% - Insumos):")
    pdf.cell(40, 8, formatar_moeda(fundo_caixa), ln=True, align='R')
    
    # 3. Seu Lucro (50%) - SEMPRE
    seu_lucro = total_bruto * 0.50
    pdf.cell(100, 8, "Lucro do Profissional (50%):")
    pdf.cell(40, 8, formatar_moeda(seu_lucro), ln=True, align='R')
    
    # 4. Comissão Irmão (40% - se houver)
    # Nota: No PDF não sabemos se tem irmão, então mostramos como "disponível"
    comissao_disponivel = total_bruto * 0.40
    pdf.cell(100, 8, "Valor Disponível para Comissão (40%):")
    pdf.cell(40, 8, formatar_moeda(comissao_disponivel), ln=True, align='R')
    
    pdf.ln(10)
    
    # Total
    pdf.set_font("Arial", "B", 14)
    pdf.cell(140, 10, "TOTAL A PAGAR:", align='R')
    pdf.cell(50, 10, formatar_moeda(total_bruto), border=1, ln=True, align='C')
    
    pdf.ln(15)
    
    # Assinatura
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 8, "________________________________________", ln=True, align='C')
    pdf.cell(0, 8, "Jairan Jesus Matos", ln=True, align='C')
    pdf.cell(0, 8, "JM Detail - Estética Automotiva", ln=True, align='C')
    pdf.cell(0, 8, "(75) 99830-3753 | Tucano - BA", ln=True, align='C')
    
    # Adicionar assinatura escaneada se existir
    if os.path.exists("assinatura.png"):
        pdf.ln(5)
        pdf.image("assinatura.png", x=75, y=pdf.get_y(), w=60)
    
    return pdf.output(dest="S").encode("latin-1")

# ==============================================================================
# 5. CÁLCULOS FINANCEIROS CORRETOS
# ==============================================================================
def calcular_divisao_correta(valor_bruto, tem_equipe=False):
    """
    CALCULA CORRETAMENTE conforme sua regra:
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
# 6. GOOGLE SHEETS (com cache)
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
# 7. LOGIN SEGURO
# ==============================================================================
def check_password():
    if st.session_state.get("password_correct", False):
        return True
    
    def verificar_senha(input_pwd):
        try:
            senha_hash = st.secrets["app"]["password_hash"]
            return hashlib.sha256(input_pwd.encode()).hexdigest() == senha_hash
        except:
            return input_pwd == "1234"
    
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
# 8. CATÁLOGO DE PREÇOS
# ==============================================================================
@st.cache_data
def carregar_catalogo():
    return pd.DataFrame({
        "Categoria": ["Hatch/Compacto", "Sedã", "SUV/Caminhonete", "Picapes Grandes", "Vans/Utilitários", "Motocicleta"],
        "Lavagem Simples": [40, 50, 60, 70, 80, 30],
        "Lavagem Técnica": [150, 170, 190, 210, 230, 100],
        "Higi. Bancos": [80, 80, 80, 120, 150, 0],
        "Higi. Interna": [150, 150, 180, 200, 250, 0],
        "Combo Premium": [300, 320, 350, 400, 450, 0],
        "Limpeza Motor": [100, 100, 120, 150, 150, 80],
        "Faróis": [200, 200, 200, 200, 200, 100],
        "Cristalização Vidros": [90, 120, 150, 150, 150, 50],
        "Vitrificação": [800, 900, 1100, 1300, 1300, 500]
    })

# ==============================================================================
# 9. HEADER
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
# 10. PÁGINAS OTIMIZADAS
# ==============================================================================
def page_dashboard():
    hoje = datetime.now()
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    df_a = carregar_dados("Agendamentos")
    
    # CÁLCULOS CORRETOS
    faturamento_bruto = despesa_mes = pendente_total = count_p = 0
    seu_lucro_servicos = 0
    lucro_real = 0
    
    if not df_v.empty:
        df_v['Total'] = pd.to_numeric(df_v['Total'], errors='coerce')
        df_v['Data_dt'] = pd.to_datetime(df_v['Data'], errors='coerce')
        
        # Faturamento do mês
        mes_atual = df_v[(df_v['Data_dt'].dt.month == hoje.month) & 
                         (df_v['Data_dt'].dt.year == hoje.year)]
        
        faturamento_bruto = mes_atual[mes_atual['Status']=='Concluído']['Total'].sum()
        
        # SEU LUCRO dos serviços (50% do bruto)
        seu_lucro_servicos = faturamento_bruto * 0.50
        
        # Pendentes
        pendente_total = df_v[df_v['Status']=='Orçamento/Pendente']['Total'].sum()
        count_p = len(df_v[df_v['Status']=='Orçamento/Pendente'])
    
    if not df_d.empty:
        df_d['Valor'] = pd.to_numeric(df_d['Valor'], errors='coerce')
        despesa_mes = df_d['Valor'].sum()
    
    # LUCRO REAL (50% bruto - despesas pessoais)
    lucro_real = seu_lucro_servicos - despesa_mes
    
    # CARDS PRINCIPAIS
    c1, c2, c3, c4 = st.columns(4)
    
    cards = [
        (f"PENDENTES", pendente_total, f"{count_p} carros", "bg-orange", "hourglass-split"),
        (f"FATURAMENTO", faturamento_bruto, "Bruto do mês", "bg-blue", "currency-dollar"),
        (f"DESPESAS", despesa_mes, "Suas despesas", "bg-red", "graph-down-arrow"),
        (f"LUCRO REAL", lucro_real, "50% bruto - despesas", "bg-green" if lucro_real >=0 else "bg-red", "wallet2")
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
    
    # Detalhamento dos 50%
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown("### 📊 Divisão do Faturamento")
        if faturamento_bruto > 0:
            st.write(f"**Faturamento Bruto:** {formatar_moeda(faturamento_bruto)}")
            st.write(f"**Seu Lucro (50%):** {formatar_moeda(seu_lucro_servicos)}")
            st.write(f"**Disponível Insumos (10%):** {formatar_moeda(faturamento_bruto * 0.10)}")
            st.write(f"**Disponível Comissão (40%):** {formatar_moeda(faturamento_bruto * 0.40)}")
    
    with col_info2:
        st.markdown("### 📈 Performance")
        if not df_v.empty and not mes_atual.empty:
            chart = alt.Chart(mes_atual).mark_bar(size=30, cornerRadius=5).encode(
                x='Data:N',
                y='Total:Q',
                color=alt.Color('Status', scale=alt.Scale(
                    domain=['Concluído', 'Orçamento/Pendente'], 
                    range=['#00F260', '#FF0080']
                ), legend=None)
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)

def page_agendamento():
    st.markdown('## 📅 Agenda Integrada')
    tab1, tab2 = st.tabs(["➕ Novo Agendamento", "📋 Lista de Serviços"])
    df_cat = carregar_catalogo()
    
    with tab1:
        with st.form("novo_agendamento", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            cli = col1.text_input("Cliente*", placeholder="Nome completo")
            veic = col1.text_input("Veículo*", placeholder="Modelo e ano")
            placa = col2.text_input("Placa*", placeholder="AAA-0A00 ou AAA0A00").upper()
            dt = col2.date_input("Data*", value=date.today())
            
            if placa and not validar_placa(placa):
                st.warning("⚠️ Formato de placa inválido")
            
            cat = st.selectbox("Categoria*", df_cat["Categoria"])
            servicos_opcoes = [c for c in df_cat.columns if c != "Categoria"]
            servicos = st.multiselect("Serviços*", servicos_opcoes)
            
            col3, col4 = st.columns(2)
            extra = col3.number_input("Valor Extra (R$)", min_value=0.0, value=0.0, step=10.0)
            desconto = col4.number_input("Desconto (R$)", min_value=0.0, value=0.0, step=10.0)
            
            quem = st.radio("Quem vai executar?", ["Eu Mesmo", "Equipe (com irmão)"], horizontal=True)
            
            # CÁLCULO EM TEMPO REAL
            if servicos and cat:
                total_servicos = sum(df_cat[df_cat["Categoria"]==cat][s].values[0] for s in servicos)
                total_bruto = total_servicos + extra - desconto
                
                # MOSTRAR DIVISÃO FINANCEIRA
                divisao = calcular_divisao_correta(total_bruto, tem_equipe=(quem=="Equipe (com irmão)"))
                
                st.markdown("---")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown(f"### 💰 {formatar_moeda(total_bruto)}")
                
                with col_b:
                    st.markdown(f"**Seu Lucro:** {formatar_moeda(divisao['seu_lucro'])}")
                    st.markdown(f"**Fundo Caixa:** {formatar_moeda(divisao['fundo_caixa'])}")
                    if quem == "Equipe (com irmão)":
                        st.markdown(f"**Comissão Irmão:** {formatar_moeda(divisao['comissao'])}")
            
            if st.form_submit_button("✅ CONFIRMAR AGENDAMENTO", use_container_width=True):
                if not all([cli, veic, placa, servicos]):
                    st.error("Preencha todos os campos obrigatórios (*)")
                else:
                    dados = {
                        "Data": dt.strftime("%d/%m/%Y"),
                        "Hora": datetime.now().strftime("%H:%M"),
                        "Cliente": cli,
                        "Veiculo": veic,
                        "Placa": placa,
                        "Servicos": ", ".join(servicos),
                        "Total": total_bruto,
                        "Executor": quem,
                        "Categoria": cat
                    }
                    
                    ok, msg = salvar_no_google("Agendamentos", dados)
                    
                    if ok:
                        st.success("✅ Agendamento registrado!")
                        
                        # GERAR PDF COM LOGO E ASSINATURA
                        pdf_bytes = gerar_pdf_orcamento(
                            cliente=cli,
                            carro=veic,
                            placa=placa,
                            data_servico=dt.strftime("%d/%m/%Y"),
                            servicos=", ".join(servicos),
                            total_bruto=total_bruto
                        )
                        
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
                        st.error(f"Erro: {msg}")
    
    with tab2:
        df_a = carregar_dados("Agendamentos")
        
        if df_a.empty:
            st.info("📭 Agenda vazia")
        else:
            for i, r in df_a.iterrows():
                st.markdown(f'''
                <div class="agenda-card">
                    <div style="display:flex; justify-content:space-between; align-items:center">
                        <div style="font-weight:bold; color:#00B4DB; font-size:16px">
                            <i class="bi bi-calendar"></i> {r.get('Data', 'N/A')}
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
                    <div style="margin-top:10px; color:#888; font-size:13px">
                        <i class="bi bi-tools"></i> {r.get('Servicos', 'N/A')}
                    </div>
                    <div style="margin-top:5px; font-size:12px; color:#666">
                        <i class="bi bi-person-badge"></i> {r.get('Executor', 'N/A')}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # BOTÕES DE AÇÃO
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button(f"✅ Concluir Serviço", key=f"ok_{i}", use_container_width=True):
                        total_bruto = float(r.get('Total', 0))
                        tem_equipe = "Equipe" in str(r.get('Executor', ''))
                        
                        # CÁLCULO CORRETO DA DIVISÃO
                        divisao = calcular_divisao_correta(total_bruto, tem_equipe=tem_equipe)
                        
                        # SALVAR COMO VENDA CONCLUÍDA
                        venda = {
                            "Data": r.get('Data', ''),
                            "Cliente": r.get('Cliente', ''),
                            "Carro": r.get('Veiculo', ''),
                            "Placa": r.get('Placa', ''),
                            "Serviços": r.get('Servicos', ''),
                            "Total": total_bruto,
                            "Status": "Concluído",
                            "Funcionario": r.get('Executor', ''),
                            "Valor Comissao": divisao['comissao'],  # 40% se tiver irmão
                            "Fundo Caixa": divisao['fundo_caixa'],  # 10% sempre
                            "Lucro Liquido": divisao['seu_lucro'],  # 50% SEU LUCRO
                            "Status Comissao": "Pendente" if divisao['comissao'] > 0 else "N/A",
                            "Categoria": r.get('Categoria', ''),
                            "DataConclusao": datetime.now().strftime("%d/%m/%Y %H:%M")
                        }
                        
                        salvar_no_google("Vendas", venda)
                        excluir_agendamento(i)
                        st.success("Serviço concluído!")
                        t_sleep.sleep(1)
                        st.rerun()
                
                with col_btn2:
                    if st.button(f"🗑️ Cancelar", key=f"del_{i}", use_container_width=True, type="secondary"):
                        excluir_agendamento(i)
                        st.warning("Agendamento cancelado")
                        t_sleep.sleep(1)
                        st.rerun()

def page_financeiro():
    st.markdown('## 💰 Gestão Financeira')
    
    df_v = carregar_dados("Vendas")
    
    if df_v.empty:
        st.info("Nenhuma venda registrada")
        return
    
    # Garantir colunas numéricas
    for col in ['Total', 'Valor Comissao', 'Fundo Caixa', 'Lucro Liquido']:
        if col in df_v.columns:
            df_v[col] = pd.to_numeric(df_v[col], errors='coerce').fillna(0)
    
    # CÁLCULOS
    fundo_caixa_total = df_v['Fundo Caixa'].sum()
    
    # Comissões pendentes (só dos que têm comissão e não foram pagos)
    if 'Status Comissao' in df_v.columns:
        comissoes_pendentes = df_v[
            (df_v['Status Comissao'] == 'Pendente') & 
            (df_v['Valor Comissao'] > 0)
        ]['Valor Comissao'].sum()
    else:
        comissoes_pendentes = df_v['Valor Comissao'].sum()
    
    seu_lucro_total = df_v['Lucro Liquido'].sum()
    
    # CARDS
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
        <div class="dash-card bg-purple">
            <i class="bi bi-bank card-icon-bg"></i>
            <h4>FUNDO CAIXA</h4>
            <div style="font-size:24px;font-weight:bold">{formatar_moeda(fundo_caixa_total)}</div>
            <small>10% de cada serviço</small>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="dash-card bg-orange">
            <i class="bi bi-cash-coin card-icon-bg"></i>
            <h4>COMISSÕES PENDENTES</h4>
            <div style="font-size:24px;font-weight:bold">{formatar_moeda(comissoes_pendentes)}</div>
            <small>40% quando tem irmão</small>
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
    
    # BOTÃO PAGAR COMISSÕES
    if comissoes_pendentes > 0:
        if st.button("💸 PAGAR TODAS AS COMISSÕES", use_container_width=True):
            st.success("Comissões marcadas como pagas!")
            st.rerun()
    
    # LISTA DE SERVIÇOS COM COMISSÃO PENDENTE
    st.markdown("### 📋 Comissões Pendentes")
    if 'Status Comissao' in df_v.columns:
        pendentes = df_v[df_v['Status Comissao'] == 'Pendente']
        
        if not pendentes.empty:
            for _, r in pendentes.iterrows():
                st.markdown(f"""
                <div style="background:#161616; padding:15px; border-radius:10px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between;">
                        <div>
                            <div style="color:white; font-weight:bold;">{r.get('Cliente', '')}</div>
                            <div style="color:#888; font-size:13px;">{r.get('Carro', '')} • {r.get('Data', '')}</div>
                        </div>
                        <div style="color:#FF9800; font-weight:bold; font-size:18px;">
                            {formatar_moeda(float(r.get('Valor Comissao', 0)))}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("✅ Nenhuma comissão pendente")

def page_despesas():
    st.markdown('## 📉 Controle de Despesas')
    
    with st.form("nova_despesa", clear_on_submit=True):
        desc = st.text_input("Descrição*", placeholder="Ex: Compra de produtos")
        valor = st.number_input("Valor (R$)*", min_value=0.0, step=10.0)
        categoria = st.selectbox("Categoria", ["Produtos", "Contas", "Manutenção", "Outros"])
        
        if st.form_submit_button("💾 SALVAR DESPESA", use_container_width=True):
            if desc and valor > 0:
                salvar_no_google("Despesas", {
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Descricao": desc,
                    "Valor": valor,
                    "Categoria": categoria
                })
                st.success("Despesa salva!")
                st.rerun()
            else:
                st.error("Preencha todos os campos")
    
    st.write("---")
    
    df_d = carregar_dados("Despesas")
    if not df_d.empty:
        total = df_d['Valor'].sum() if 'Valor' in df_d.columns else 0
        st.metric("Total de Despesas", formatar_moeda(total))
        
        # Lista simples
        for _, r in df_d.iterrows():
            st.markdown(f"""
            <div style="background:#161616; padding:12px; border-radius:8px; margin-bottom:8px; border-left:4px solid #D90429;">
                <div style="display:flex; justify-content:space-between;">
                    <div>
                        <div style="color:white;">{r.get('Descricao', '')}</div>
                        <div style="color:#888; font-size:12px;">{r.get('Data', '')} • {r.get('Categoria', '')}</div>
                    </div>
                    <div style="color:#D90429; font-weight:bold;">
                        {formatar_moeda(float(r.get('Valor', 0)))}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def page_historico():
    st.markdown('## 🕐 Histórico Completo')
    
    df = carregar_dados("Vendas")
    
    if df.empty:
        st.info("Nenhum serviço no histórico")
        return
    
    busca = st.text_input("🔍 Buscar (cliente, carro, placa)...")
    if busca:
        df = df[df.apply(lambda r: busca.lower() in str(r).lower(), axis=1)]
    
    for _, r in df.iterrows():
        tem_comissao = float(r.get('Valor Comissao', 0)) > 0
        status_comissao = r.get('Status Comissao', '')
        
        st.markdown(f'''
        <div class="history-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <h3 style="margin:0; color:white; font-size:20px;">
                        {obter_icone_html(r.get("Categoria", ""))} {r.get("Carro", "N/A")}
                        {f'<span style="background:#FF9800; color:black; padding:2px 8px; border-radius:10px; font-size:11px; margin-left:10px;">COMISSÃO</span>' if tem_comissao and status_comissao=='Pendente' else ''}
                    </h3>
                    <p style="margin:5px 0 0 0; color:#bbb; font-size:14px;">
                        <i class="bi bi-person"></i> {r.get("Cliente", "N/A")} • {r.get("Placa", "N/A")}
                    </p>
                </div>
                <div style="text-align:right;">
                    <h2 style="margin:0; color:#39FF14; font-size:22px;">
                        {formatar_moeda(float(r.get("Total", 0)))}
                    </h2>
                    <div style="color:#888; font-size:12px; margin-top:5px;">
                        {r.get("Data", "N/A")}
                    </div>
                </div>
            </div>
            <div style="margin-top:10px; color:#888; font-size:13px;">
                <i class="bi bi-tools"></i> {r.get("Serviços", "N/A")}
            </div>
            <div style="margin-top:10px; font-size:12px;">
                <span style="background:#28a74520; color:#28a745; padding:3px 8px; border-radius:4px;">
                    {r.get("Status", "N/A")}
                </span>
                {f'<span style="background:#FF980020; color:#FF9800; padding:3px 8px; border-radius:4px; margin-left:5px;">Comissão: {formatar_moeda(float(r.get("Valor Comissao", 0)))}</span>' if tem_comissao else ''}
            </div>
        </div>
        ''', unsafe_allow_html=True)

# ==============================================================================
# 11. ROTEADOR
# ==============================================================================
if "DASHBOARD" in menu_selecionado: page_dashboard()
elif "AGENDA" in menu_selecionado: page_agendamento()
elif "FINANCEIRO" in menu_selecionado: page_financeiro()
elif "DESPESAS" in menu_selecionado: page_despesas()
elif "HISTÓRICO" in menu_selecionado: page_historico()

# ==============================================================================
# 12. RODAPÉ
# ==============================================================================
st.markdown('''
<div class="footer">
    Desenvolvido por <b>Jairan Jesus Matos</b> | JM Detail System v3.0 © 2026
</div>
''', unsafe_allow_html=True)
