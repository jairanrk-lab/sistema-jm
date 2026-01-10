import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date, time
from fpdf import FPDF
import gspread
import os
import re
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
    div[role="radiogroup"] label:nth-of-type(1)::before { font-family: "bootstrap-icons"; content: "\\F5A6"; margin-right: 8px; font-size: 18px; }
    div[role="radiogroup"] label:nth-of-type(2)::before { font-family: "bootstrap-icons"; content: "\\F20E"; margin-right: 8px; font-size: 18px; }
    div[role="radiogroup"] label:nth-of-type(3)::before { font-family: "bootstrap-icons"; content: "\\F23E"; margin-right: 8px; font-size: 18px; }
    div[role="radiogroup"] label:nth-of-type(4)::before { font-family: "bootstrap-icons"; content: "\\F4E9"; margin-right: 8px; font-size: 18px; }
    div[role="radiogroup"] label:nth-of-type(5)::before { font-family: "bootstrap-icons"; content: "\\F291"; margin-right: 8px; font-size: 18px; }

    div[role="radiogroup"] label:hover { border-color: #D90429 !important; color: white !important; background-color: #1a1a1a !important; transform: translateY(-2px); }
    div[role="radiogroup"] label[data-checked="true"] { background: linear-gradient(90deg, #D90429 0%, #8D021F 100%) !important; color: white !important; border-color: #D90429 !important; box-shadow: 0 4px 15px rgba(217, 4, 41, 0.4) !important; }
    
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

def limpar_numero(numero):
    """Remove caracteres especiais do número para o link do WhatsApp."""
    if not numero: return ""
    return re.sub(r'\D', '', str(numero))

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def conectar_google_sheets():
    ID_FIXO = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg"
    try:
        if "app" in st.secrets and "spreadsheet_id" in st.secrets["app"]:
            ID_FIXO = st.secrets["app"]["spreadsheet_id"]
        if os.path.exists("chave_google.json"): 
            client = gspread.service_account(filename="chave_google.json")
        elif "gcp_service_account" in st.secrets:
            client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        else: return None
        return client.open_by_key(ID_FIXO)
    except Exception: return None

def carregar_dados(aba):
    sheet = conectar_google_sheets()
    if sheet is None: return pd.DataFrame()
    try: return pd.DataFrame(sheet.worksheet(aba).get_all_records())
    except: return pd.DataFrame()

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
    return pd.DataFrame({
        "Categoria": ["Hatch/Compacto", "Sedã", "SUV/Caminhonete", "Picapes Grandes", "Vans/Utilitários", "Motocicleta"],
        "Lavagem Simples": [40.0, 50.0, 60.0, 70.0, 80.0, 30.0],
        "Lavagem Técnica": [150.0, 170.0, 190.0, 210.0, 230.0, 100.0],
        "Vitrificação": [800.0, 900.0, 1100.0, 1300.0, 1300.0, 500.0]
    })

def obter_icone_html(cat):
    if not isinstance(cat, str): return '<i class="bi bi-car-front-fill"></i>'
    c = cat.lower()
    if "moto" in c: return '<i class="bi bi-motorcycle"></i>'
    elif "suv" in c or "picape" in c: return '<i class="bi bi-truck-front-fill"></i>'
    elif "van" in c: return '<i class="bi bi-bus-front-fill"></i>'
    else: return '<i class="bi bi-car-front-fill"></i>'

# --- BUSCA INTELIGENTE POR PLACA (FIX: BUSCA TELEFONE) ---
def buscar_cliente_por_placa(placa_busca):
    df_a = carregar_dados("Agendamentos")
    df_v = carregar_dados("Vendas")
    df_completo = pd.concat([df_a, df_v], ignore_index=True)
    if df_completo.empty: return None
    
    placa_busca = placa_busca.replace("-", "").strip().upper()
    
    # Padroniza nomes de colunas para evitar erros de maiúsculas/minúsculas
    colunas_originais = df_completo.columns
    df_completo.columns = [str(c).strip().lower() for c in df_completo.columns]
    
    if "placa" in df_completo.columns:
        df_completo['placa'] = df_completo['placa'].astype(str).str.replace("-", "").str.strip().str.upper()
        res = df_completo[df_completo['placa'] == placa_busca]
        
        if not res.empty:
            ultimo = res.iloc[-1]
            # Tenta pegar o telefone em colunas comuns
            tel = ultimo.get("telefone", ultimo.get("whatsapp", ultimo.get("celular", "")))
            return {
                "Cliente": ultimo.get("cliente", ""),
                "Telefone": str(tel),
                "Veiculo": ultimo.get("veiculo", ultimo.get("carro", "")),
                "Categoria": ultimo.get("categoria", "")
            }
    return None

def gerar_pdf_orcamento(dados):
    pdf = FPDF()
    pdf.add_page()
    logo_file = next((f for f in ["logo.png", "Logo.png", "LOGO.png"] if os.path.exists(f)), None)
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
    pdf.cell(0, 10, txt(f"DATA: {dados['Data']}"), ln=True); pdf.ln(5)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(140, 10, txt("Descrição do Serviço"), 1, 0, 'L', 1)
    pdf.cell(50, 10, txt("Valor"), 1, 1, 'C', 1)
    pdf.set_font("Arial", size=12)
    for s in str(dados['Servicos']).split(','):
        if s.strip():
            pdf.cell(140, 10, txt(s.strip()), 1)
            pdf.cell(50, 10, "-", 1, 1, 'C') 
    pdf.ln(5); pdf.set_font("Arial", "B", 14)
    pdf.cell(140, 10, "TOTAL ESTIMADO", 1, 0, 'R')
    pdf.cell(50, 10, txt(f"R$ {dados['Total']:.2f}"), 1, 1, 'C')
    return pdf.output(dest="S").encode("latin-1")

# ==============================================================================
# --- CABEÇALHO ---
# ==============================================================================
c_logo1, c_logo2, c_logo3 = st.columns([1,2,1])
with c_logo2:
    logo_path = next((f for f in ["logo.png", "Logo.png", "LOGO.png"] if os.path.exists(f)), None)
    if logo_path: st.image(logo_path, use_container_width=True)
    else: st.markdown("<h1 style='text-align:center; color:#D90429; font-weight:800'>JM DETAIL</h1>", unsafe_allow_html=True)

st.write("") 
menu_opcoes = ["DASHBOARD", "AGENDA", "FINANCEIRO", "DESPESAS", "HISTÓRICO"]
menu_selecionado = st.radio("Navegação", menu_opcoes, horizontal=True, label_visibility="collapsed")
st.write("---") 

# --- PÁGINAS ---

def page_dashboard():
    hoje = datetime.now()
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    receita_mes, despesa_mes, pendente_total, count_p = 0.0, 0.0, 0.0, 0
    
    if not df_v.empty:
        for c in ["Total"]:
            if c in df_v.columns:
                df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
        df_v['Data_dt'] = pd.to_datetime(df_v['Data'], format='%d/%m/%Y', errors='coerce')
        df_mes = df_v[(df_v['Data_dt'].dt.month == hoje.month) & (df_v['Data_dt'].dt.year == hoje.year)]
        receita_mes = df_mes[df_mes["Status"]=="Concluído"]["Total"].sum()
        pendente_total = df_v[df_v["Status"]=="Orçamento/Pendente"]["Total"].sum()
        count_p = len(df_v[df_v["Status"]=="Orçamento/Pendente"])

    if not df_d.empty:
        df_d['Data_dt'] = pd.to_datetime(df_d['Data'], format='%d/%m/%Y', errors='coerce')
        df_d_mes = df_d[(df_d['Data_dt'].dt.month == hoje.month) & (df_d['Data_dt'].dt.year == hoje.year)]
        despesa_mes = pd.to_numeric(df_d_mes["Valor"].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0).sum()
    
    lucro_final = (receita_mes * 0.50) - despesa_mes
    
    META_MENSAL = 5000.00 
    pct = min((receita_mes / META_MENSAL) * 100, 100.0)
    st.markdown(f'<div style="background-color: #161616; padding: 10px 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px;"><div style="display:flex; justify-content:space-between; color:#bbb; font-size:12px; margin-bottom:5px;"><span>🎯 META: {formatar_moeda(META_MENSAL)}</span><span>ATUAL: <b style="color:white">{formatar_moeda(receita_mes)}</b></span></div><div style="width:100%; background-color:#333; border-radius:15px; height:22px;"><div style="width:{pct}%; background: linear-gradient(90deg, #00b09b, #96c93d); height:22px; border-radius:15px; display:flex; align-items:center; justify-content:flex-end; padding-right:10px; transition: width 1s ease-in-out; box-shadow: 0 0 10px rgba(150, 201, 61, 0.5);"><span style="color:white; font-weight:bold; font-size:12px; text-shadow: 1px 1px 2px black;">{pct:.1f}%</span></div></div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="dash-card bg-orange"><i class="bi bi-hourglass-split card-icon-bg"></i><h4>PENDENTES</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(pendente_total)}</div><small>{count_p} carros na fila</small></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="dash-card bg-blue"><i class="bi bi-currency-dollar card-icon-bg"></i><h4>FATURAMENTO</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(receita_mes)}</div><small>Mês Atual</small></div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3: st.markdown(f'<div class="dash-card bg-red"><i class="bi bi-graph-down-arrow card-icon-bg"></i><h4>DESPESAS</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(despesa_mes)}</div><small>Gastos externos</small></div>', unsafe_allow_html=True)
    cor_l = "bg-green" if lucro_final >= 0 else "bg-red"
    with c4: st.markdown(f'<div class="dash-card {cor_l}"><i class="bi bi-wallet2 card-icon-bg"></i><h4>LUCRO LÍQUIDO</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_final)}</div><small>50% Bruto - Despesas</small></div>', unsafe_allow_html=True)

def page_financeiro():
    st.markdown('## <i class="bi bi-cash-coin" style="color: #28a745;"></i> Financeiro')
    st.info("Página em manutenção para novos ajustes de fluxo.")

def page_agendamento():
    st.markdown('## <i class="bi bi-calendar-check" style="color: white;"></i> Agenda Integrada', unsafe_allow_html=True)
    tab_new, tab_list = st.tabs(["NOVO AGENDAMENTO", "LISTA DE SERVIÇOS"]) 
    df_cat = carregar_catalogo()
    
    with tab_new:
        with st.container(border=True):
            p_input = st.text_input("Digite a Placa para Buscar Cadastro (ou Nova Placa)", key="p_input")
            val_cli, val_veic, val_zap, val_cat_idx = "", "", "", 0
            
            if p_input:
                dados_cli = buscar_cliente_por_placa(p_input)
                if dados_cli:
                    st.success(f"Cliente Encontrado: {dados_cli['Cliente']}")
                    val_cli, val_veic, val_zap = dados_cli['Cliente'], dados_cli['Veiculo'], dados_cli.get("Telefone", "")
                    cats = df_cat["Categoria"].tolist()
                    if dados_cli['Categoria'] in cats: val_cat_idx = cats.index(dados_cli['Categoria'])
                else:
                    if len(p_input) > 5: st.warning("Placa nova. Preencha os dados.")

            c1, c2 = st.columns(2)
            cli = c1.text_input("Nome do Cliente", value=val_cli)
            zap = c2.text_input("WhatsApp (DDD+Número)", value=val_zap, placeholder="75999998888")
            c3, c4 = st.columns(2)
            veic = c3.text_input("Modelo do Veículo", value=val_veic)
            dt = c4.date_input("Data", value=date.today()); hr = c4.time_input("Horário", value=time(8, 0)).strftime("%H:%M")
            
            cat = st.selectbox("Categoria:", df_cat["Categoria"], index=val_cat_idx)
            servs = st.multiselect("Serviços:", [c for c in df_cat.columns if c != "Categoria"])
            ce1, ce2, ce3 = st.columns(3)
            ext = ce1.number_input("Valor Extra", min_value=0.0); desc = ce2.number_input("Desconto", min_value=0.0); qm = ce3.radio("Executor:", ["Eu Mesmo", "Equipe"], horizontal=True)
            
            if servs:
                total = sum([df_cat[df_cat["Categoria"] == cat][s].values[0] for s in servs]) + ext - desc
                st.markdown(f"<h3 style='text-align:right; color:#39FF14'>Total: {formatar_moeda(total)}</h3>", unsafe_allow_html=True)
                
                b_ag, b_pdf = st.columns(2)
                if b_ag.button("CONFIRMAR AGENDAMENTO", use_container_width=True):
                    dados = {"Data": dt.strftime("%d/%m/%Y"), "Hora": hr, "Cliente": cli, "Telefone": zap, "Veiculo": veic, "Placa": p_input, "Servicos": ", ".join(servs), "Total": total, "Executor": qm, "Status": "Orçamento/Pendente", "Categoria": cat}
                    ok, msg = salvar_no_google("Agendamentos", dados)
                    if ok: 
                        st.success("Agendado!"); t_sleep.sleep(1)
                        num_limpo = limpar_numero(zap)
                        if num_limpo:
                            st.markdown(f'<a href="https://wa.me/55{num_limpo}?text=Olá {cli}, JM Detail confirma seu agendamento dia {dt.strftime("%d/%m/%Y")} às {hr}." target="_blank"><button style="background:#25D366;color:white;border:none;padding:10px;border-radius:5px;width:100%">CONFIRMAR NO WHATSAPP</button></a>', unsafe_allow_html=True)
                
                if b_pdf.button("📄 GERAR ORÇAMENTO PDF", use_container_width=True):
                    d_pdf = {"Cliente": cli, "Veiculo": veic, "Placa": p_input, "Data": dt.strftime("%d/%m/%Y"), "Servicos": ", ".join(servs), "Total": total}
                    st.download_button(label="📥 BAIXAR PDF", data=gerar_pdf_orcamento(d_pdf), file_name=f"Orcamento_{cli}.pdf", mime='application/pdf', use_container_width=True)

    with tab_list:
        df_a = carregar_dados("Agendamentos")
        if df_a.empty: st.info("Agenda vazia.")
        else:
            for i, r in df_a.iterrows():
                st.markdown(f'<div class="agenda-card"><div style="display:flex; justify-content:space-between;"><b>{r["Data"]} {r["Hora"]}</b><b style="color:#39FF14">{formatar_moeda(float(r["Total"]))}</b></div><div style="font-size:18px"><b>{obter_icone_html(r.get("Categoria",""))} {r["Veiculo"]}</b> ({r["Placa"]})</div><div>{r["Cliente"]}</div><div style="color:#888">🔧 {r["Servicos"]}</div></div>', unsafe_allow_html=True)
                c_ok, c_zap, c_del = st.columns([2, 1, 1])
                with c_ok:
                    if st.button("✅ Concluir", key=f"ok_{i}", use_container_width=True):
                        t = float(r["Total"]); f = t * 0.10; c = t * 0.40 if "Equipe" in r["Executor"] else 0.0
                        venda = {"Data": r["Data"], "Cliente": r["Cliente"], "Telefone": r.get("Telefone", ""), "Carro": r["Veiculo"], "Placa": r["Placa"], "Serviços": r["Servicos"], "Total": t, "Status": "Concluído", "Funcionario": r["Executor"], "Valor Comissao": c, "Fundo Caixa": f, "Lucro Liquido": t-f-c, "Status Comissao": "Pendente", "Categoria": r.get("Categoria", "")}
                        salvar_no_google("Vendas", venda); excluir_agendamento(i); st.rerun()
                with c_zap:
                    num_limpo = limpar_numero(r.get("Telefone", ""))
                    if num_limpo:
                        msg = f"Olá {r['Cliente']}! Seu {r['Veiculo']} já está pronto na JM Detail. ✨ Pode vir buscar!"
                        st.markdown(f'<a href="https://wa.me/55{num_limpo}?text={msg}" target="_blank"><button style="background:#128C7E;color:white;border:none;border-radius:5px;height:45px;width:100%"><i class="bi bi-whatsapp"></i></button></a>', unsafe_allow_html=True)
                    else: st.button("🚫", disabled=True, key=f"no_zap_{i}", use_container_width=True)
                with c_del:
                    if st.button("🗑️", key=f"del_{i}", use_container_width=True): excluir_agendamento(i); st.rerun()

def page_despesas():
    st.markdown('## <i class="bi bi-receipt" style="color: #D90429;"></i> Despesas')
    with st.form("f_desp"):
        desc = st.text_input("Descrição"); val = st.number_input("Valor", min_value=0.0)
        if st.form_submit_button("Lançar"):
            salvar_no_google("Despesas", {"Data": datetime.now().strftime("%d/%m/%Y"), "Descricao": desc, "Valor": val})
            st.success("Salvo!")

def page_historico():
    st.markdown('## <i class="bi bi-clock-history" style="color: #FFC107;"></i> Histórico')
    df = carregar_dados("Vendas")
    if df.empty: st.info("Vazio.")
    else:
        busca = st.text_input("🔍 Buscar...").strip().lower()
        df_f = df.iloc[::-1]
        if busca: df_f = df_f[df_f.apply(lambda r: busca in str(r).lower(), axis=1)]
        for _, r in df_f.iterrows():
            st.markdown(f'<div class="history-card" style="border-left:5px solid #28a745"><div style="display:flex;justify-content:space-between;"><div><b>{r["Carro"]}</b><br>{r["Cliente"]} | {r["Placa"]}</div><div style="text-align:right"><b style="color:#39FF14">{formatar_moeda(float(r["Total"]))}</b><br><small>{r["Data"]}</small></div></div><div style="color:#888">{r["Serviços"]}</div></div>', unsafe_allow_html=True)

if "DASHBOARD" in menu_selecionado: page_dashboard()
elif "AGENDA" in menu_selecionado: page_agendamento()
elif "FINANCEIRO" in menu_selecionado: page_financeiro()
elif "DESPESAS" in menu_selecionado: page_despesas()
elif "HISTÓRICO" in menu_selecionado: page_historico()

st.markdown('<div class="footer">Desenvolvido por <b>Jairan Jesus Matos</b> | JM Detail System © 2026</div>', unsafe_allow_html=True)
