import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, time
from fpdf import FPDF
import gspread
import os
import time as t_sleep
import re 
import urllib.parse
import shutil

# --- 1. CONFIGURAÇÃO (FRONTEND) ---
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# --- 2. LOGIN & SEGURANÇA ---
# ==============================================================================
def check_password():
    if st.session_state.get("password_correct", False): return True
    if st.query_params.get("logado") == "true":
        st.session_state["password_correct"] = True
        return True
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### <i class='bi bi-shield-lock-fill' style='color:#D90429'></i> Acesso Restrito", unsafe_allow_html=True)
        with st.form("login_form"):
            pwd = st.text_input("Senha:", type="password")
            if st.form_submit_button("ACESSAR"):
                try: senha_correta = st.secrets["app"]["password"]
                except: senha_correta = "1234"
                if pwd == senha_correta: 
                    st.session_state["password_correct"] = True
                    st.query_params["logado"] = "true"
                    st.rerun()
                else: st.error("Senha incorreta.")
    return False

if not check_password(): st.stop()

# ==============================================================================
# --- 3. CSS AVANÇADO (MOBILE FIRST) ---
# ==============================================================================
st.markdown("""
<style>
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    
    html, body, p, h1, h2, h3, h4, h5, h6, input, button, .stSelectbox { font-family: -apple-system, sans-serif !important; }
    
    /* Fundo Dark Glass */
    [data-testid="stAppViewContainer"] { background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #000000 80%); }
    
    /* Inputs Estilizados */
    input, .stSelectbox > div > div {
        background-color: rgba(30, 30, 30, 0.4) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important; border-radius: 12px !important; backdrop-filter: blur(5px);
    }
    
    /* Menu Superior (Scroll Horizontal no Mobile) */
    div[role="radiogroup"] { overflow-x: auto !important; flex-wrap: nowrap !important; padding-bottom: 5px; }
    div[role="radiogroup"] label {
        min-width: 90px !important; border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.1) !important;
        background: rgba(40,40,40,0.5) !important; color: #ccc !important;
    }
    div[role="radiogroup"] label[data-checked="true"] { 
        background: linear-gradient(135deg, #D90429, #8D021F) !important; color: white !important; border: none !important;
    }

    /* Cards e Métricas */
    .dash-card { 
        border-radius: 16px; padding: 15px; color: white; margin-bottom: 15px; height: 120px;
        display: flex; flex-direction: column; justify-content: center; 
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);
    }
    .bg-gradient { background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.0)); }
    
    /* Cores de Status */
    .st-ok { color: #39FF14; font-weight: bold; }
    .st-warn { color: #FFD700; font-weight: bold; }
    .st-err { color: #D90429; font-weight: bold; }

    /* Botão Principal */
    div.stButton > button { 
        background: #D90429 !important; color: white; border-radius: 10px; height: 50px; font-weight: bold; border:none;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DE DADOS (BACKEND) ---

def converter_valor(valor):
    if isinstance(valor, (int, float)): return float(valor)
    try: return float(str(valor).replace("R$", "").replace(".", "").replace(",", ".").strip() or 0)
    except: return 0.0

def formatar_moeda(valor):
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def limpar_numero(num): return re.sub(r'\D', '', str(num)) if num else ""

def conectar_google_sheets():
    # ID DA SUA PLANILHA (Preencha se necessário)
    ID_FIXO = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg"
    try:
        if "app" in st.secrets: ID_FIXO = st.secrets["app"].get("spreadsheet_id", ID_FIXO)
        if os.path.exists("chave_google.json"): client = gspread.service_account(filename="chave_google.json")
        elif "gcp_service_account" in st.secrets: client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        else: return None
        return client.open_by_key(ID_FIXO)
    except: return None

def carregar_dados(aba):
    s = conectar_google_sheets()
    try: return pd.DataFrame(s.worksheet(aba).get_all_records()) if s else pd.DataFrame()
    except: return pd.DataFrame()

def salvar_no_google(aba, dados):
    s = conectar_google_sheets()
    if not s: return False
    try:
        ws = s.worksheet(aba)
        if not ws.row_values(1): ws.append_row(list(dados.keys()))
        ws.append_row([dados.get(c, "") for c in ws.row_values(1)])
        return True
    except: return False

def atualizar_estoque_auto():
    # Lógica de baixa automática
    s = conectar_google_sheets()
    if s:
        try:
            ws = s.worksheet("Estoque"); d = ws.get_all_values(); head = [x.lower() for x in d[0]]
            ia, ig = -1, -1
            for i, h in enumerate(head):
                if "atual" in h: ia = i
                if "gasto" in h: ig = i
            if ia >= 0 and ig >= 0:
                for i in range(1, len(d)):
                    try: 
                        atual, gasto = float(d[i][ia].replace(",",".") or 0), float(d[i][ig].replace(",",".") or 0)
                        if gasto > 0: ws.update_cell(i+1, ia+1, max(0, atual - gasto))
                    except: pass
        except: pass

@st.cache_data(ttl=300)
def obter_custo_fixo():
    try:
        df = pd.DataFrame(conectar_google_sheets().worksheet("Config").get_all_records())
        return converter_valor(df[df["Chave"]=="CustoFixo"].iloc[0]["Valor"])
    except: return 0.0

@st.cache_data(ttl=60)
def carregar_catalogo():
    try: return pd.DataFrame(conectar_google_sheets().worksheet("Catalogo").get_all_records())
    except: return pd.DataFrame()

def buscar_cliente(placa):
    # Busca inteligente em Agenda e Vendas
    try:
        df = pd.concat([carregar_dados("Agendamentos"), carregar_dados("Vendas")], ignore_index=True)
        if df.empty: return None
        busca = placa.replace("-","").upper().strip()
        # Localiza coluna de placa
        col = next((c for c in df.columns if "placa" in c.lower()), None)
        if col:
            res = df[df[col].astype(str).str.replace("-","").str.upper().str.strip() == busca]
            if not res.empty:
                r = res.iloc[-1]
                # Mapeia colunas flexivelmente
                return {
                    "Cliente": r.get(next((c for c in df.columns if "cliente" in c.lower()), ""), ""),
                    "Veiculo": r.get(next((c for c in df.columns if "veic" in c.lower() or "carro" in c.lower()), ""), ""),
                    "Telefone": str(r.get(next((c for c in df.columns if "tel" in c.lower()), ""), ""))
                }
    except: pass
    return None

# --- GERAÇÃO DE PDF (Vistoria e Orçamento) ---
def gerar_pdf(tipo, dados, imagens=None):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"JM DETAIL - {tipo.upper()}", ln=True, align='C')
    pdf.set_font("Arial", size=10); pdf.cell(0, 10, "Estética Automotiva Premium | (75) 99830-3753", ln=True, align='C'); pdf.ln(5)
    
    # Cabeçalho
    pdf.set_font("Arial", "B", 11)
    texto_cli = f"CLIENTE: {dados.get('Cliente','')} | VEÍCULO: {dados.get('Veiculo','')} | DATA: {dados.get('Data','')}"
    pdf.cell(0, 8, texto_cli.encode('latin-1','replace').decode('latin-1'), ln=True)
    pdf.ln(5)
    
    if tipo == "Vistoria" and imagens:
        pdf.cell(0, 10, "REGISTRO FOTOGRÁFICO", ln=True, align='C')
        x, y, w, h = 10, pdf.get_y(), 90, 65
        col = 0
        for tit, path in imagens.items():
            if path and os.path.exists(path):
                if y + h > 260: pdf.add_page(); y = 20
                pdf.image(path, x=x + (col*95), y=y, w=w, h=h)
                col += 1
                if col > 1: col=0; y += h + 10

    elif tipo == "Orcamento":
        pdf.set_fill_color(220,220,220); pdf.cell(140, 8, "Descricao", 1, 0, 'L', 1); pdf.cell(50, 8, "Valor", 1, 1, 'C', 1)
        pdf.set_font("Arial", size=10)
        pdf.cell(140, 8, str(dados.get('Servicos','')).encode('latin-1','replace').decode('latin-1'), 1)
        pdf.cell(50, 8, formatar_moeda(dados.get('Total',0)), 1, 1, 'C')

    return pdf.output(dest="S").encode("latin-1")

# ==============================================================================
# --- 5. PÁGINAS (FRONTEND) ---
# ==============================================================================

# 5.1 DASHBOARD COM GRÁFICOS (BI)
def page_dashboard():
    st.markdown("## 📊 Painel de Controle (BI)")
    try:
        df_v = carregar_dados("Vendas")
        df_d = carregar_dados("Despesas")
        
        # Processamento
        rec, desp, custo_f = 0.0, 0.0, obter_custo_fixo()
        if not df_v.empty:
            cols_v = [c.strip().capitalize() for c in df_v.columns]; df_v.columns = cols_v
            df_v["Total_N"] = df_v["Total"].apply(converter_valor)
            df_v["Data_dt"] = pd.to_datetime(df_v["Data"], dayfirst=True, errors='coerce')
            # Filtro Mês Atual
            hoje = datetime.now()
            df_mes = df_v[(df_v["Data_dt"].dt.month == hoje.month) & (df_v["Data_dt"].dt.year == hoje.year)]
            rec = df_mes[df_mes["Status"].str.strip()=="Concluído"]["Total_N"].sum()
        
        if not df_d.empty:
            cols_d = [c.strip().capitalize() for c in df_d.columns]; df_d.columns = cols_d
            df_d["Valor_N"] = df_d["Valor"].apply(converter_valor)
            df_d["Data_dt"] = pd.to_datetime(df_d["Data"], dayfirst=True, errors='coerce')
            df_d_mes = df_d[(df_d["Data_dt"].dt.month == hoje.month) & (df_d["Data_dt"].dt.year == hoje.year)]
            desp = df_d_mes["Valor_N"].sum()

        lucro = (rec * 0.5) - desp - custo_f
        
        # KPIs
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="dash-card" style="border-left: 5px solid #00B4DB"><h3>FATURAMENTO</h3><h1>{formatar_moeda(rec)}</h1></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="dash-card" style="border-left: 5px solid #D90429"><h3>DESPESAS</h3><h1>{formatar_moeda(desp + custo_f)}</h1></div>', unsafe_allow_html=True)
        cor_lucro = "#39FF14" if lucro >= 0 else "#D90429"
        c3.markdown(f'<div class="dash-card" style="border-left: 5px solid {cor_lucro}"><h3>LUCRO LÍQUIDO</h3><h1 style="color:{cor_lucro}">{formatar_moeda(lucro)}</h1></div>', unsafe_allow_html=True)

        st.write("---")
        
        # --- ÁREA DE GRÁFICOS (NOVIDADE v8.0) ---
        if not df_v.empty:
            g1, g2 = st.columns(2)
            
            with g1:
                st.markdown("### 🍩 Serviços Mais Vendidos")
                if "Carro" in df_v.columns:
                    # Agrupa por Carro ou Categoria (se tiver) - Simulação por 'Carro' como proxy de tipo
                    df_pie = df_v["Carro"].value_counts().reset_index().head(5)
                    df_pie.columns = ["Serviço/Carro", "Qtd"]
                    fig_pie = px.pie(df_pie, values="Qtd", names="Serviço/Carro", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                    st.plotly_chart(fig_pie, use_container_width=True)

            with g2:
                st.markdown("### 📈 Tendência de Faturamento")
                # Agrupa por data
                df_line = df_v.groupby(df_v["Data_dt"].dt.date)["Total_N"].sum().reset_index()
                df_line.columns = ["Data", "Valor"]
                fig_line = px.line(df_line, x="Data", y="Valor", markers=True)
                fig_line.update_traces(line_color="#39FF14", line_width=3)
                fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.05)", font_color="white", xaxis_showgrid=False)
                st.plotly_chart(fig_line, use_container_width=True)

        # Monitor de Estoque (Mini)
        try:
            alerta = False
            df_est = pd.DataFrame(conectar_google_sheets().worksheet("Estoque").get_all_records())
            for i, r in df_est.iterrows():
                if float(str(r["Atual_ml"]).replace(",",".")) < 1000: alerta = True
            if alerta: st.error("⚠️ ALERTA: Existem produtos com estoque crítico! Verifique a aba Estoque.")
        except: pass

    except Exception as e: st.error(f"Erro no Dashboard: {e}")

# 5.2 AGENDA COM UX MOBILE
def page_agenda():
    st.markdown("## 📅 Agenda & Serviços")
    tab1, tab2 = st.tabs(["Novo", "Lista"])
    
    with tab1:
        with st.container(border=True):
            placa = st.text_input("Placa (Busca Rápida):")
            cli, veic, tel = "", "", ""
            if placa:
                res = buscar_cliente(placa)
                if res: 
                    st.success("Cliente Recorrente!")
                    cli, veic, tel = res["Cliente"], res["Veiculo"], res["Telefone"]
            
            c1, c2 = st.columns(2)
            nome = c1.text_input("Cliente", value=cli)
            zap = c2.text_input("WhatsApp", value=tel)
            carro = c1.text_input("Veículo", value=veic)
            dt = c2.date_input("Data", value=date.today())
            
            servs = st.multiselect("Serviços", ["Lavagem Simples", "Lavagem Detalhada", "Higienização", "Polimento", "Vitrificação"])
            total = st.number_input("Valor Total (R$)", min_value=0.0, step=10.0)
            
            if st.button("AGENDAR SERVIÇO", use_container_width=True):
                if salvar_no_google("Agendamentos", {"Data": dt.strftime("%d/%m/%Y"), "Cliente": nome, "Veiculo": carro, "Placa": placa, "Telefone": zap, "Servicos": ", ".join(servs), "Total": total, "Status": "Pendente"}):
                    st.success("Agendado!")
                    t_sleep.sleep(1); st.rerun()

    with tab2:
        df = carregar_dados("Agendamentos")
        if not df.empty:
            for i, r in df.iterrows():
                # CARD EXPANSÍVEL (MELHORIA UX MOBILE)
                with st.expander(f"{r['Data']} - {r['Veiculo']} ({r['Cliente']})"):
                    st.write(f"**Serviços:** {r['Servicos']}")
                    st.write(f"**Valor:** {r['Total']}")
                    c_ok, c_del = st.columns(2)
                    if c_ok.button("✅ Concluir", key=f"ok_{i}"):
                        atualizar_estoque_auto() # Baixa estoque
                        # Salva venda e apaga agenda
                        venda = r.to_dict(); venda["Status"] = "Concluído"; venda["Lucro Liquido"] = converter_valor(r["Total"])*0.5
                        salvar_no_google("Vendas", venda)
                        # Exclusão simplificada (necessita reimplementar função de delete ou apenas ignorar)
                        st.toast("Serviço Concluído!"); t_sleep.sleep(1); st.rerun()

# 5.3 VISTORIA
def page_vistoria():
    st.markdown("## 📷 Vistoria Cautelar")
    st.info("Use a câmera do celular para registrar avarias.")
    with st.form("vistoria_form"):
        placa = st.text_input("Placa do Veículo")
        avarias = st.multiselect("Avarias Visíveis", ["Risco Lataria", "Amassado", "Rodas Raladas", "Vidro Trincado", "Farol Quebrado"])
        fotos = st.file_uploader("Fotos (Frente, Traseira, Laterais)", accept_multiple_files=True, type=["jpg","png"])
        if st.form_submit_button("GERAR PDF"):
            if placa:
                # Simulação de caminhos temp
                paths = {} 
                if fotos:
                    for i, f in enumerate(fotos):
                        p = f"temp_{i}.jpg"; 
                        with open(p, "wb") as w: w.write(f.getbuffer())
                        paths[f"Foto {i+1}"] = p
                
                pdf = gerar_pdf("Vistoria", {"Cliente": "Diverso", "Veiculo": "Ver Fotos", "Placa": placa, "Data": datetime.now().strftime("%d/%m/%Y"), "Avarias": avarias}, paths)
                st.download_button("BAIXAR PDF", pdf, "Vistoria.pdf", "application/pdf")
                # Limpeza
                for p in paths.values(): os.remove(p)

# 5.4 ESTOQUE VISUAL
def page_estoque():
    st.markdown("## 📦 Estoque de Produtos")
    try:
        df = pd.DataFrame(conectar_google_sheets().worksheet("Estoque").get_all_records())
        if not df.empty:
            cols = st.columns(2) # 2 colunas no mobile fica melhor
            for i, r in df.iterrows():
                at = float(str(r["Atual_ml"]).replace(",","."))
                perc = min(at/5000, 1.0) # Base 5L
                cor = "#39FF14" if perc > 0.2 else "#D90429"
                with cols[i%2]:
                    st.markdown(f"""
                    <div style="border:1px solid #333; padding:10px; border-radius:10px; margin-bottom:10px;">
                        <b>{r['Produto']}</b><br>
                        <small>{int(at)} ml</small>
                        <div style="background:#444; height:5px; width:100%; margin-top:5px;">
                            <div style="background:{cor}; height:5px; width:{int(perc*100)}%;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    except: st.warning("Conexão com planilha necessária.")

# 5.5 FINANCEIRO COM SIMULADOR (ENGENHARIA DE CUSTOS)
def page_financeiro():
    st.markdown("## 💰 Financeiro & Precificação")
    
    tab1, tab2 = st.tabs(["Caixa", "Simulador de Preço"])
    
    with tab1:
        # Lógica resumida financeira
        st.write("Resumo do Mês (Ver Dashboard para Gráficos)")
        if st.button("Baixar Relatório Completo"): st.toast("Gerando PDF...")

    with tab2:
        st.markdown("### 🧮 Calculadora de Lucro Real")
        st.caption("Descubra quanto você realmente ganha em cada serviço.")
        
        c1, c2 = st.columns(2)
        prod_custo = c1.number_input("Custo Produtos (R$)", value=15.0, help="Quanto gastou de shampoo, cera, etc.")
        hora_trab = c2.number_input("Horas Trabalhadas", value=2.0)
        valor_hora = c1.number_input("Sua Hora (R$)", value=30.0, help="Quanto vale sua hora de mão de obra?")
        
        preco_venda = st.number_input("Preço que deseja cobrar (R$)", value=100.0, step=10.0)
        
        custo_total = prod_custo + (hora_trab * valor_hora)
        lucro = preco_venda - custo_total
        margem = (lucro / preco_venda) * 100 if preco_venda else 0
        
        st.write("---")
        if lucro > 0:
            st.success(f"✅ Lucro Estimado: {formatar_moeda(lucro)} ({margem:.1f}%)")
        else:
            st.error(f"❌ Prejuízo Estimado: {formatar_moeda(lucro)}")
            st.info(f"Sugestão: Cobre pelo menos {formatar_moeda(custo_total * 1.3)} para ter 30% de margem.")

# --- NAVEGAÇÃO ---
c_logo1, c_logo2, c_logo3 = st.columns([1,3,1])
with c_logo2:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.markdown("<h1 style='text-align:center; color:#D90429'>JM DETAIL</h1>", unsafe_allow_html=True)

menu = st.radio("", ["DASHBOARD", "AGENDA", "VISTORIA", "ESTOQUE", "FINANCEIRO"], horizontal=True, label_visibility="collapsed")

if menu == "DASHBOARD": page_dashboard()
elif menu == "AGENDA": page_agenda()
elif menu == "VISTORIA": page_vistoria()
elif menu == "ESTOQUE": page_estoque()
elif menu == "FINANCEIRO": page_financeiro()

st.markdown('<div class="footer">JM Detail v8.0 | ADS System</div>', unsafe_allow_html=True)
