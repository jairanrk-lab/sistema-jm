import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, time
from fpdf import FPDF
import gspread
import os
import time as t_sleep
import re 
import urllib.parse
import shutil

# --- 1. CONFIGURAÇÃO GERAL ---
st.set_page_config(page_title="JM DETAIL", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# --- 2. CSS (VISUAL APPLE/NEON BLINDADO) ---
# ==============================================================================
st.markdown("""
<style>
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    
    html, body, p, h1, h2, h3, h4, h5, h6, li, a, button, input, textarea, label, .stTextInput, .stNumberInput, .stSelectbox {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #000000 80%);
    }
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    
    /* ELEMENTOS DE VIDRO */
    input[type="text"], input[type="number"], input[type="date"], input[type="time"], .stSelectbox > div > div, .stMultiSelect > div > div, .stTextArea > div > div {
        background-color: rgba(30, 30, 30, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important; border-radius: 10px !important;
        backdrop-filter: blur(5px) !important;
    }
    
    /* BOTÕES */
    div.stButton > button { 
        background-color: #D90429 !important; color: white !important; border-radius: 10px !important; 
        font-weight: 700 !important; border: none !important; height: 45px !important; 
        box-shadow: 0 4px 10px rgba(217, 4, 41, 0.3); transition: all 0.3s ease;
    }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 6px 15px rgba(217, 4, 41, 0.5); }

    /* MENU SUPERIOR */
    div[role="radiogroup"] { overflow-x: auto; padding-bottom: 5px; }
    div[role="radiogroup"] label {
        min-width: 90px; border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.1) !important;
        background: rgba(40,40,40,0.5) !important; color: #ccc !important;
    }
    div[role="radiogroup"] label[data-checked="true"] { 
        background: linear-gradient(135deg, rgba(217, 4, 41, 0.8), rgba(141, 2, 31, 0.8)) !important; 
        color: white !important; border-color: rgba(255,255,255,0.2) !important;
    }

    /* CARDS */
    .dash-card { 
        border-radius: 18px; padding: 20px; color: white; margin-bottom: 20px; height: 140px; 
        display: flex; flex-direction: column; justify-content: center; border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px); background: rgba(255,255,255,0.03);
    }
    .bg-orange { border-top: 2px solid #ff9800; }
    .bg-blue   { border-top: 2px solid #00b4db; }
    .bg-red    { border-top: 2px solid #D90429; }
    .bg-green  { border-top: 2px solid #39FF14; }
    
    .stock-alert {
        background-color: rgba(217, 4, 41, 0.15); border: 1px solid #D90429; color: #ffcccc;
        padding: 15px; border-radius: 12px; margin-bottom: 20px; display: flex; align-items: center; gap: 15px;
    }
    
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: rgba(0,0,0,0.9); backdrop-filter: blur(5px); color: #666; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #222; z-index: 9999; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES DE BACKEND ---

def converter_valor(valor):
    try: return float(str(valor).replace("R$", "").replace(".", "").replace(",", ".").strip() or 0)
    except: return 0.0

def formatar_moeda(valor):
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def limpar_numero(num): return re.sub(r'\D', '', str(num)) if num else ""

def conectar_google_sheets():
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
        vals = []
        for c in ws.row_values(1):
            vals.append(dados.get(c, ""))
        ws.append_row(vals)
        return True
    except: return False

def atualizar_estoque_auto():
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

def buscar_cliente(placa):
    # BUSCA SOMENTE PARA O ADMIN (Privacidade)
    try:
        df = pd.concat([carregar_dados("Agendamentos"), carregar_dados("Vendas")], ignore_index=True)
        if df.empty: return None
        busca = placa.replace("-","").upper().strip()
        col = next((c for c in df.columns if "placa" in c.lower()), None)
        if col:
            res = df[df[col].astype(str).str.replace("-","").str.upper().str.strip() == busca]
            if not res.empty:
                r = res.iloc[-1]
                return {
                    "Cliente": r.get(next((c for c in df.columns if "cliente" in c.lower()), ""), ""),
                    "Veiculo": r.get(next((c for c in df.columns if "veic" in c.lower() or "carro" in c.lower()), ""), ""),
                    "Telefone": str(r.get(next((c for c in df.columns if "tel" in c.lower()), ""), ""))
                }
    except: pass
    return None

# ==============================================================================
# --- 4. ÁREA PÚBLICA (MODO CLIENTE) ---
# ==============================================================================
def area_cliente():
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.markdown("<h1 style='text-align:center; color:#D90429'>JM DETAIL</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center; color:white'>Agendamento Online</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#aaa'>Preencha os dados abaixo para solicitar seu serviço.</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        nome = st.text_input("Seu Nome Completo")
        tel = st.text_input("Seu WhatsApp (DDD + Número)")
        carro = st.text_input("Modelo do Veículo (Ex: Fiat Toro)")
        placa = st.text_input("Placa (Opcional - Para cadastro)")
        
        st.write("---")
        dt = st.date_input("Data Preferida", value=date.today(), min_value=date.today())
        hr = st.time_input("Horário Preferido", value=time(8,0))
        
        servs = st.multiselect("Serviços Desejados", ["Lavagem Simples", "Lavagem Detalhada", "Higienização Interna", "Polimento", "Vitrificação", "Lavagem de Motor"])
        obs = st.text_area("Observações (Opcional)")
        
        if st.button("🚀 SOLICITAR AGENDAMENTO", use_container_width=True):
            if nome and tel and carro:
                dados = {
                    "Data": dt.strftime("%d/%m/%Y"), 
                    "Hora": hr.strftime("%H:%M"),
                    "Cliente": nome, 
                    "Telefone": tel, 
                    "Veiculo": carro, 
                    "Placa": placa, 
                    "Servicos": ", ".join(servs), 
                    "Obs": obs,
                    "Status": "Pendente (Site)", # Marca que veio pelo site
                    "Total": 0 # Valor a definir pelo Admin
                }
                if salvar_no_google("Agendamentos", dados):
                    st.success("✅ Solicitação enviada com sucesso!")
                    st.info("Entraremos em contato pelo WhatsApp para confirmar o valor e o horário.")
                    # Link para o cliente já chamar no Zap se quiser
                    msg = urllib.parse.quote(f"Olá, acabei de agendar um serviço para o {carro} pelo site.")
                    st.markdown(f'<br><a href="https://wa.me/5575998303753?text={msg}" target="_blank"><button style="background:#25D366; color:white; width:100%; border:none; padding:10px; border-radius:10px">💬 Falar com JM Detail</button></a>', unsafe_allow_html=True)
            else:
                st.error("Por favor, preencha Nome, Telefone e Veículo.")

# ==============================================================================
# --- 5. ÁREA RESTRITA (ADMIN) ---
# ==============================================================================
def area_admin():
    # MENU SUPERIOR
    menu = st.radio("", ["DASHBOARD", "AGENDA", "VISTORIA", "ESTOQUE", "FINANCEIRO", "HISTÓRICO"], horizontal=True, label_visibility="collapsed")
    st.write("---")

    if menu == "DASHBOARD":
        # DASHBOARD COMPLETO (Recuperado v8.0)
        st.markdown(f'## <i class="bi bi-speedometer2" style="color: #00B4DB;"></i> Painel Geral', unsafe_allow_html=True)
        try:
            df_v = carregar_dados("Vendas"); df_d = carregar_dados("Despesas")
            rec, desp, custo_f = 0.0, 0.0, obter_custo_fixo()
            hoje = datetime.now()
            
            if not df_v.empty:
                df_v.columns = [c.strip().capitalize() for c in df_v.columns]
                df_v["Total_N"] = df_v["Total"].apply(converter_valor)
                df_v["Data_dt"] = pd.to_datetime(df_v["Data"], dayfirst=True, errors='coerce')
                df_mes = df_v[(df_v["Data_dt"].dt.month == hoje.month) & (df_v["Data_dt"].dt.year == hoje.year)]
                rec = df_mes[df_mes["Status"].str.strip()=="Concluído"]["Total_N"].sum()
                pendente = df_v[df_v["Status"].str.contains("Pendente", case=False, na=False)]["Total_N"].sum()
            else: df_mes = pd.DataFrame()

            if not df_d.empty:
                df_d.columns = [c.strip().capitalize() for c in df_d.columns]
                df_d["Valor_N"] = df_d["Valor"].apply(converter_valor)
                df_d["Data_dt"] = pd.to_datetime(df_d["Data"], dayfirst=True, errors='coerce')
                df_d_mes = df_d[(df_d["Data_dt"].dt.month == hoje.month) & (df_d["Data_dt"].dt.year == hoje.year)]
                desp = df_d_mes["Valor_N"].sum()

            lucro = (rec * 0.5) - desp - custo_f
            
            # Cards
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="dash-card bg-blue"><h3>FATURAMENTO</h3><h1>{formatar_moeda(rec)}</h1><small>Pendentes: {formatar_moeda(pendente)}</small></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="dash-card bg-red"><h3>DESPESAS</h3><h1>{formatar_moeda(desp + custo_f)}</h1><small>Fixo: {formatar_moeda(custo_f)}</small></div>', unsafe_allow_html=True)
            cor = "#39FF14" if lucro >= 0 else "#D90429"
            c3.markdown(f'<div class="dash-card bg-green"><h3>LUCRO LÍQUIDO</h3><h1 style="color:{cor}">{formatar_moeda(lucro)}</h1><small>Margem Real</small></div>', unsafe_allow_html=True)
            
            st.write("---")
            
            # Alerta de Estoque
            try:
                ws = conectar_google_sheets().worksheet("Estoque"); d = ws.get_all_records(); df_est = pd.DataFrame(d)
                criticos = 0
                for i, r in df_est.iterrows():
                    if float(str(r.get("Atual_ml",0)).replace(",",".") or 0) < 1000: criticos += 1
                if criticos > 0:
                    st.markdown(f'<div class="stock-alert"><i class="bi bi-exclamation-triangle-fill"></i> <b>ALERTA:</b> {criticos} produtos com estoque baixo!</div>', unsafe_allow_html=True)
            except: pass

            # Gráficos
            if not df_mes.empty:
                g1, g2 = st.columns(2)
                with g1:
                    st.markdown("###### Serviços Mais Vendidos")
                    if "Carro" in df_mes.columns: # Usando Carro como proxy de tipo
                        df_pie = df_mes["Carro"].value_counts().reset_index().head(5)
                        fig = px.pie(df_pie, values="count", names="Carro", hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
                        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", showlegend=False, height=250, margin=dict(t=0,b=0,l=0,r=0))
                        st.plotly_chart(fig, use_container_width=True)
                with g2:
                    st.markdown("###### Evolução Diária")
                    df_line = df_mes.groupby(df_mes["Data_dt"].dt.date)["Total_N"].sum().reset_index()
                    fig = px.line(df_line, x="Data_dt", y="Total_N", markers=True)
                    fig.update_traces(line_color="#E0E0E0", line_width=3)
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.05)", font_color="white", height=250, margin=dict(t=10,b=10,l=0,r=0), xaxis_showgrid=False)
                    st.plotly_chart(fig, use_container_width=True)

        except Exception as e: st.error(f"Erro Dash: {e}")

    elif menu == "AGENDA":
        st.markdown('## <i class="bi bi-calendar-check" style="color: white;"></i> Gestão de Agenda', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["NOVO (ADMIN)", "LISTA DE PEDIDOS"])
        
        with tab1:
            with st.container(border=True):
                # AQUI TEM BUSCA POR PLACA (Só o Admin vê)
                placa = st.text_input("Placa (Busca Automática):")
                cli_val, veic_val, tel_val = "", "", ""
                if placa:
                    res = buscar_cliente(placa)
                    if res: 
                        st.success("Cliente Recorrente Encontrado!")
                        cli_val, veic_val, tel_val = res["Cliente"], res["Veiculo"], res["Telefone"]
                
                c1, c2 = st.columns(2)
                nome = c1.text_input("Cliente", value=cli_val)
                zap = c2.text_input("WhatsApp", value=tel_val)
                carro = c1.text_input("Veículo", value=veic_val)
                dt = c2.date_input("Data", value=date.today())
                servs = st.multiselect("Serviços", ["Lavagem Simples", "Lavagem Detalhada", "Higienização", "Polimento", "Vitrificação"])
                total = st.number_input("Valor Total (R$)", min_value=0.0)
                
                if st.button("AGENDAR (ADMIN)", use_container_width=True):
                    if salvar_no_google("Agendamentos", {"Data": dt.strftime("%d/%m/%Y"), "Cliente": nome, "Veiculo": carro, "Placa": placa, "Telefone": zap, "Servicos": ", ".join(servs), "Total": total, "Status": "Confirmado"}):
                        st.success("Agendado!")
        
        with tab2:
            df = carregar_dados("Agendamentos")
            if not df.empty:
                for i, r in df.iterrows():
                    # Destaque para pedidos do site
                    border_color = "#39FF14" if "Site" in str(r.get("Status","")) else "#444"
                    with st.expander(f"{r['Data']} | {r['Veiculo']} - {r['Cliente']} ({r.get('Status','Normal')})"):
                        st.write(f"**Serviços:** {r['Servicos']}")
                        st.write(f"**Obs:** {r.get('Obs','')}")
                        if "Site" in str(r.get("Status","")): st.info("🔔 Este cliente veio pelo Site! Confirme o valor.")
                        
                        col_conf, col_del = st.columns(2)
                        if col_conf.button("✅ Concluir Serviço", key=f"ok_{i}"):
                            atualizar_estoque_auto()
                            venda = r.to_dict(); venda["Status"] = "Concluído"; venda["Total"] = converter_valor(r["Total"]); venda["Lucro Liquido"] = venda["Total"]*0.5
                            salvar_no_google("Vendas", venda)
                            # (Aqui idealmente removeria da agenda, mas na v9 simplificada mantemos o aviso)
                            st.toast("Concluído e Baixado Estoque!")
                            t_sleep.sleep(1); st.rerun()

    elif menu == "ESTOQUE":
        st.markdown('## <i class="bi bi-box-seam" style="color: #F5A623;"></i> Estoque', unsafe_allow_html=True)
        try:
            df = pd.DataFrame(conectar_google_sheets().worksheet("Estoque").get_all_records())
            cols = st.columns(2)
            for i, r in df.iterrows():
                at = float(str(r["Atual_ml"]).replace(",","."))
                perc = min(at/5000, 1.0)
                cor = "#39FF14" if perc > 0.2 else "#D90429"
                with cols[i%2]:
                    st.markdown(f"""
                    <div style="border:1px solid rgba(255,255,255,0.1); background:rgba(255,255,255,0.05); padding:15px; border-radius:12px; margin-bottom:15px;">
                        <b style="font-size:16px">{r['Produto']}</b><br>
                        <small style="color:#aaa">{int(at)} ml</small>
                        <div style="background:#333; height:8px; width:100%; margin-top:8px; border-radius:4px">
                            <div style="background:{cor}; height:8px; width:{int(perc*100)}%;"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
        except: st.warning("Erro ao carregar estoque.")

    elif menu == "FINANCEIRO":
        st.markdown('## <i class="bi bi-cash-coin" style="color: #28a745;"></i> Financeiro', unsafe_allow_html=True)
        t1, t2 = st.tabs(["Fluxo", "Simulador Preço"])
        with t1: st.info("Resumo no Dashboard.")
        with t2:
            st.markdown("### 🧮 Calculadora de Preço")
            c1, c2 = st.columns(2)
            custo = c1.number_input("Custo Produtos", 15.0)
            horas = c2.number_input("Horas gastas", 2.0)
            valor_h = c1.number_input("Valor da Hora", 30.0)
            preco = st.number_input("Preço a cobrar", 100.0)
            lucro = preco - (custo + (horas*valor_h))
            if lucro > 0: st.success(f"Lucro: {formatar_moeda(lucro)}")
            else: st.error(f"Prejuízo: {formatar_moeda(lucro)}")

    elif menu == "HISTÓRICO":
        st.info("Histórico de Clientes (CRM) em manutenção.")
    
    elif menu == "VISTORIA":
        st.info("Módulo de Vistoria (Igual versão anterior).")

# ==============================================================================
# --- 6. CONTROLE DE ACESSO (LÓGICA PRINCIPAL) ---
# ==============================================================================

# Se já estiver logado, mostra ADMIN
if st.session_state.get("password_correct", False):
    # Botão de Sair no Sidebar
    with st.sidebar:
        st.write(f"Logado como Admin")
        if st.button("Sair / Logout"):
            st.session_state["password_correct"] = False
            st.rerun()
    area_admin()

# Se NÃO estiver logado, mostra CLIENTE + Botão de Login
else:
    # Mostra a área pública
    area_cliente()
    
    # Rodapé discreto para Login
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("---")
    col_login, _ = st.columns([1, 4])
    with col_login:
        with st.expander("🔒 Acesso Restrito (Admin)"):
            pwd = st.text_input("Senha do Sistema", type="password")
            if st.button("Entrar"):
                try: senha_correta = st.secrets["app"]["password"]
                except: senha_correta = "1234"
                
                if pwd == senha_correta:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")

st.markdown('<div class="footer">JM Detail System © 2026</div>', unsafe_allow_html=True)
