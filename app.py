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
# --- 3. ESTILO CSS (VISUAL PREMIUM) ---
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    * { font-family: 'Poppins', sans-serif !important; }
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { background-color: #000000 !important; }
    .block-container { padding-top: 1rem; padding-bottom: 6rem; }
    [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebar"] { display: none !important; }

    div[role="radiogroup"] { display: flex !important; flex-direction: row !important; width: 100% !important; justify-content: space-between !important; background-color: transparent !important; border: none !important; padding: 0 !important; gap: 12px !important; }
    div[role="radiogroup"] label { flex: 1 !important; background-color: #111 !important; border: 1px solid #333 !important; padding: 12px 5px !important; border-radius: 8px !important; transition: all 0.3s ease !important; margin: 0 !important; color: #888 !important; font-weight: 600 !important; font-size: 16px !important; white-space: nowrap !important; display: flex; align-items: center; justify-content: center !important; }
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
def formatar_moeda(valor):
    try: return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

def conectar_google_sheets():
    ID_FIXO = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg"
    try:
        if "app" in st.secrets and "spreadsheet_id" in st.secrets["app"]:
            ID_FIXO = st.secrets["app"]["spreadsheet_id"]
        if os.path.exists("chave_google.json"): client = gspread.service_account(filename="chave_google.json")
        elif "gcp_service_account" in st.secrets: client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        else: return None
        return client.open_by_key(ID_FIXO)
    except: return None

def carregar_dados(aba):
    sheet = conectar_google_sheets()
    if sheet is None: return pd.DataFrame()
    try: 
        df = pd.DataFrame(sheet.worksheet(aba).get_all_records())
        return df
    except: 
        return pd.DataFrame()

def salvar_no_google(aba, linha_dados):
    sheet = conectar_google_sheets()
    if sheet is None: return False, "Falha na conexão."
    try:
        ws = sheet.worksheet(aba)
        headers = ws.row_values(1)
        if not headers: headers = list(linha_dados.keys()); ws.append_row(headers)
        nova_linha = [linha_dados.get(h, "") for h in headers]
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
            df = pd.DataFrame(ws.get_all_records())
            if not df.empty:
                cols_num = [c for c in df.columns if c != "Categoria"]
                for c in cols_num: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)
                return df
    except: pass
    return pd.DataFrame({
        "Categoria": ["Hatch/Compacto", "Sedã", "SUV/Caminhonete", "Picapes Grandes", "Vans/Utilitários", "Moto (até 300cc)", "Moto (acima 300cc)"],
        "Lavagem Simples": [40, 50, 60, 70, 80, 0, 0],
        "Lavagem Técnica": [150, 170, 190, 210, 230, 50, 100],
        "Vitrificação": [800, 900, 1100, 1300, 1300, 150, 250]
    })

# --- BUSCA POR PLACA ---
def buscar_cliente_por_placa(placa_busca):
    df_a = carregar_dados("Agendamentos")
    df_v = carregar_dados("Vendas")
    df_c = pd.concat([df_a, df_v], ignore_index=True)
    if df_c.empty: return None
    placa_clean = placa_busca.replace("-", "").strip().upper()
    # Normaliza nomes de colunas
    df_c.columns = [c.strip().capitalize() for c in df_c.columns]
    if "Placa" in df_c.columns:
        df_c["Placa"] = df_c["Placa"].astype(str).str.replace("-", "").str.strip().str.upper()
        res = df_c[df_c["Placa"] == placa_clean]
        if not res.empty:
            u = res.iloc[-1]
            return {"Cliente": u.get("Cliente", ""), "Telefone": str(u.get("Telefone", "")), "Veiculo": u.get("Veiculo", u.get("Carro", "")), "Categoria": u.get("Categoria", "")}
    return None

# --- GERADOR PDF PREMIUM ---
def gerar_pdf_orcamento(dados):
    pdf = FPDF()
    pdf.add_page()
    logo = None
    for n in ["logo.png", "Logo.png", "LOGO.png"]:
        if os.path.exists(n): logo = n; break
    if logo: pdf.image(logo, x=10, y=8, w=50)
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_y(25); pdf.set_font("Arial", "B", 16); pdf.cell(0, 10, txt("JM DETAIL - ORÇAMENTO"), ln=True, align='C')
    pdf.set_font("Arial", size=10); pdf.cell(0, 10, txt("Estética Automotiva Premium | (75) 99830-3753"), ln=True, align='C'); pdf.ln(10)
    pdf.set_font("Arial", "B", 12); pdf.cell(0, 8, txt(f"CLIENTE: {dados['Cliente']}"), ln=True)
    pdf.cell(0, 8, txt(f"VEÍCULO: {dados['Veiculo']} | PLACA: {dados['Placa']}"), ln=True)
    pdf.cell(0, 8, txt(f"DATA: {dados['Data']}"), ln=True); pdf.ln(5)
    pdf.set_fill_color(220, 220, 220); pdf.cell(140, 10, txt("Descrição"), 1, 0, 'L', 1); pdf.cell(50, 10, txt("Valor"), 1, 1, 'C', 1)
    pdf.set_font("Arial", size=12)
    for item in dados['Itens']:
        pdf.cell(140, 10, txt(item['desc']), 1); pdf.cell(50, 10, txt(f"R$ {item['val']:.2f}"), 1, 1, 'C')
    pdf.ln(5); pdf.set_font("Arial", "B", 14); pdf.cell(140, 10, "TOTAL ESTIMADO", 1, 0, 'R'); pdf.cell(50, 10, txt(f"R$ {dados['Total']:.2f}"), 1, 1, 'C')
    pdf.ln(20); sig = None
    for s in ["assinatura.png", "Assinatura.png"]:
        if os.path.exists(s): sig = s; break
    if sig: pdf.image(sig, x=80, y=pdf.get_y()-10, w=50)
    pdf.cell(0, 10, "________________________________________", ln=True, align='C')
    pdf.cell(0, 5, txt("Jairan Jesus Matos - JM Detail"), ln=True, align='C')
    return pdf.output(dest="S").encode("latin-1")

# ==============================================================================
# --- LAYOUT PRINCIPAL ---
# ==============================================================================
c_logo1, c_logo2, c_logo3 = st.columns([1,2,1])
with c_logo2:
    logo_path = next((f for f in ["logo.png", "Logo.png", "LOGO.png"] if os.path.exists(f)), None)
    if logo_path: st.image(logo_path, use_container_width=True)
    else: st.markdown("<h1 style='text-align:center; color:#D90429; font-weight:800'>JM DETAIL</h1>", unsafe_allow_html=True)

st.write("") 
menu_selecionado = st.radio("Navegação", ["DASHBOARD", "AGENDA", "FINANCEIRO", "DESPESAS", "HISTÓRICO"], horizontal=True, label_visibility="collapsed")
st.write("---") 

# --- DASHBOARD ---
def page_dashboard():
    hoje = datetime.now()
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    
    receita_mes, despesa_mes, pendente_total, count_p = 0.0, 0.0, 0.0, 0
    
    if not df_v.empty:
        # Padroniza nomes de colunas
        df_v.columns = [c.strip().capitalize() for c in df_v.columns]
        for c in ["Total"]:
            if c in df_v.columns: df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
        
        df_v['Data_dt'] = pd.to_datetime(df_v['Data'], format='%d/%m/%Y', errors='coerce')
        df_mes = df_v[(df_v['Data_dt'].dt.month == hoje.month) & (df_v['Data_dt'].dt.year == hoje.year)]
        receita_mes = df_mes[df_mes["Status"]=="Concluído"]["Total"].sum()
        pendente_total = df_v[df_v["Status"]=="Pendente"]["Total"].sum()
        count_p = len(df_v[df_v["Status"]=="Pendente"])

    if not df_d.empty:
        df_d.columns = [c.strip().capitalize() for c in df_d.columns]
        df_d['Data_dt'] = pd.to_datetime(df_d['Data'], format='%d/%m/%Y', errors='coerce')
        df_d_mes = df_d[(df_d['Data_dt'].dt.month == hoje.month) & (df_d['Data_dt'].dt.year == hoje.year)]
        despesa_mes = pd.to_numeric(df_d_mes["Valor"].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0).sum()
    
    lucro_final = (receita_mes * 0.50) - despesa_mes
    
    META = 5000.00 
    pct = min((receita_mes / META) * 100, 100.0)
    st.markdown(f'<div style="background:#161616;padding:10px 15px;border-radius:12px;border:1px solid #333;margin-bottom:20px;"><div style="display:flex;justify-content:space-between;color:#bbb;font-size:12px;margin-bottom:5px;"><span>🎯 META: {formatar_moeda(META)}</span><span>ATUAL: <b style="color:white">{formatar_moeda(receita_mes)}</b></span></div><div style="width:100%;background:#333;border-radius:15px;height:22px;"><div style="width:{pct}%;background:linear-gradient(90deg,#00b09b,#96c93d);height:22px;border-radius:15px;display:flex;align-items:center;justify-content:flex-end;padding-right:10px;box-shadow:0 0 10px rgba(150,201,61,0.5);"><span style="color:white;font-weight:bold;font-size:12px;text-shadow:1px 1px 2px black;">{pct:.1f}%</span></div></div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    c1.markdown(f'<div class="dash-card bg-orange"><i class="bi bi-hourglass-split card-icon-bg"></i><h4>PENDENTES</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(pendente_total)}</div><small>{count_p} na fila</small></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="dash-card bg-blue"><i class="bi bi-currency-dollar card-icon-bg"></i><h4>FATURAMENTO</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(receita_mes)}</div><small>Mês Atual</small></div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    c3.markdown(f'<div class="dash-card bg-red"><i class="bi bi-graph-down-arrow card-icon-bg"></i><h4>DESPESAS</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(despesa_mes)}</div><small>Gastos</small></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="dash-card {"bg-green" if lucro_final >= 0 else "bg-red"}"><i class="bi bi-wallet2 card-icon-bg"></i><h4>LUCRO LÍQUIDO</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_final)}</div><small>50% Bruto - Despesas</small></div>', unsafe_allow_html=True)

# --- AGENDA ---
def page_agendamento():
    st.markdown('## <i class="bi bi-calendar-check" style="color: white;"></i> Agenda')
    t1, t2 = st.tabs(["NOVO AGENDAMENTO", "LISTA DE SERVIÇOS"])
    df_cat = carregar_catalogo()
    
    with t1:
        with st.container(border=True):
            p_in = st.text_input("🔍 Digite a Placa para Buscar ou Cadastrar")
            v_cli, v_veic, v_zap, v_cat_idx = "", "", "", 0
            if p_in:
                d_c = buscar_cliente_por_placa(p_in)
                if d_c:
                    st.success(f"Encontrado: {d_c['Cliente']}"); v_cli, v_veic, v_zap = d_c['Cliente'], d_c['Veiculo'], d_c['Telefone']
                    cats = df_cat["Categoria"].tolist(); v_cat_idx = cats.index(d_c['Categoria']) if d_c['Categoria'] in cats else 0
            
            c1, c2 = st.columns(2)
            cli = c1.text_input("Nome", value=v_cli); zap = c2.text_input("WhatsApp", value=v_zap)
            c3, c4 = st.columns(2)
            veic = c3.text_input("Veículo", value=v_veic); dt = c4.date_input("Data", value=date.today()); hr = c4.time_input("Hora", value=time(8,0)).strftime("%H:%M")
            cat = st.selectbox("Categoria:", df_cat["Categoria"], index=v_cat_idx)
            servs = st.multiselect("Serviços:", [c for c in df_cat.columns if c != "Categoria"])
            ce1, ce2, ce3 = st.columns(3)
            ext = ce1.number_input("Extra", min_value=0.0); desc = ce2.number_input("Desconto", min_value=0.0); qm = ce3.radio("Executor:", ["Eu Mesmo", "Equipe"])
            
            if servs:
                itens = [{"desc": s, "val": float(df_cat[df_cat["Categoria"] == cat][s].values[0])} for s in servs]
                total = sum(i['val'] for i in itens) + ext - desc
                if ext > 0: itens.append({"desc": "Valor Extra", "val": ext})
                if desc > 0: itens.append({"desc": "Desconto", "val": -desc})
                st.markdown(f"<h3 style='text-align:right; color:#39FF14'>Total: {formatar_moeda(total)}</h3>", unsafe_allow_html=True)
                
                b1, b2 = st.columns(2)
                if b1.button("CONFIRMAR AGENDAMENTO", use_container_width=True):
                    d = {"Data": dt.strftime("%d/%m/%Y"), "Hora": hr, "Cliente": cli, "Telefone": zap, "Veiculo": veic, "Placa": p_in, "Servicos": ", ".join(servs), "Total": total, "Executor": qm, "Status": "Pendente", "Categoria": cat}
                    ok, msg = salvar_no_google("Agendamentos", d)
                    if ok:
                        st.success("Salvo!"); t_sleep.sleep(1)
                        if zap: st.markdown(f'<a href="https://wa.me/55{zap}?text=Oi {cli}, JM Detail confirma seu agendamento dia {dt.strftime("%d/%m/%Y")} às {hr}." target="_blank"><button style="background:#25D366;color:white;width:100%;border:none;padding:10px;border-radius:5px">ZAP CONFIRMAÇÃO</button></a>', unsafe_allow_html=True)
                
                if b2.button("📄 GERAR PDF", use_container_width=True):
                    d_p = {"Cliente": cli, "Veiculo": veic, "Placa": p_in, "Data": dt.strftime("%d/%m/%Y"), "Itens": itens, "Total": total}
                    st.download_button("📥 BAIXAR PDF", gerar_pdf_orcamento(d_p), f"Orcamento_{cli}.pdf", "application/pdf", use_container_width=True)

    with t2:
        df_a = carregar_dados("Agendamentos")
        if df_a.empty: st.info("Vazio.")
        else:
            for i, r in df_a.iterrows():
                st.markdown(f'<div class="agenda-card"><div style="display:flex;justify-content:space-between;"><b>{r["Data"]} {r["Hora"]}</b><b style="color:#39FF14">{formatar_moeda(r["Total"])}</b></div><div style="font-size:18px"><b>{obter_icone_html(r.get("Categoria",""))} {r["Veiculo"]}</b> ({r["Placa"]})</div><div>{r["Cliente"]}</div><div style="color:#888">🔧 {r["Servicos"]}</div></div>', unsafe_allow_html=True)
                c1, c2, c3 = st.columns([2,1,1])
                if c1.button("✅ Concluir", key=f"ok_{i}", use_container_width=True):
                    t = float(r["Total"]); f = t * 0.10; c = t * 0.40 if "Equipe" in r["Executor"] else 0.0
                    v = {"Data": r["Data"], "Cliente": r["Cliente"], "Telefone": r.get("Telefone",""), "Carro": r["Veiculo"], "Placa": r["Placa"], "Serviços": r["Servicos"], "Total": t, "Status": "Concluído", "Funcionario": r["Executor"], "Valor Comissao": c, "Fundo Caixa": f, "Lucro Liquido": t-f-c, "Status Comissao": "Pendente", "Categoria": r.get("Categoria","")}
                    salvar_no_google("Vendas", v); excluir_agendamento(i); st.rerun()
                if c2.button("📱", key=f"zap_{i}", use_container_width=True):
                    if r.get("Telefone"): st.markdown(f'<meta http-equiv="refresh" content="0; url=https://wa.me/55{r["Telefone"]}?text=Seu {r["Veiculo"]} está pronto!">', unsafe_allow_html=True)
                if c3.button("🗑️", key=f"del_{i}", use_container_width=True): excluir_agendamento(i); st.rerun()

def page_historico():
    st.markdown('## <i class="bi bi-clock-history"></i> Histórico')
    df = carregar_dados("Vendas")
    if df.empty: st.info("Vazio.")
    else:
        busca = st.text_input("🔍 Buscar...").lower()
        df_f = df.iloc[::-1]
        if busca: df_f = df_f[df_f.apply(lambda r: busca in str(r).lower(), axis=1)]
        for _, r in df_f.iterrows():
            st.markdown(f'<div class="history-card" style="border-left:5px solid #28a745"><div style="display:flex;justify-content:space-between;"><div><b>{r["Carro"]}</b><br>{r["Cliente"]} | {r["Placa"]}</div><div style="text-align:right"><b style="color:#39FF14">{formatar_moeda(r["Total"])}</b><br><small>{r["Data"]}</small></div></div><div style="color:#888">{r["Serviços"]}</div></div>', unsafe_allow_html=True)

if menu_selecionado == "DASHBOARD": page_dashboard()
elif menu_selecionado == "AGENDA": page_agendamento()
elif menu_selecionado == "HISTÓRICO": page_historico()

st.markdown('<div class="footer">JM Detail System © 2026 | Desenvolvido por Jairan Jesus Matos</div>', unsafe_allow_html=True)
