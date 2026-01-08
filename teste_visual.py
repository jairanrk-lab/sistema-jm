import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date
from fpdf import FPDF
import gspread
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide")

# ==============================================================================
# --- ESTILO CSS PREMIUM (V6.2) 🎨 ---
# ==============================================================================
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    h1, h2, h3, h4, p, span, div { color: #ffffff; font-family: 'Segoe UI', sans-serif; }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] { background-color: #111; border-right: 1px solid #333; }
    section[data-testid="stSidebar"] .block-container { padding-top: 1rem !important; }
    
    /* LOGO */
    [data-testid="stSidebar"] img {
        transform: scale(1.4) !important; transform-origin: center top !important;
        margin-bottom: 2rem !important; margin-top: 1rem !important;
    }

    /* Oculta radio buttons */
    div[role="radiogroup"] label > div:first-child { display: none !important; }

    /* BOTÕES SIDEBAR */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 12px 20px !important; margin-bottom: 8px !important;
        background-color: #1E1E1E !important; border-radius: 8px !important;
        border: 1px solid #333 !important; color: #aaa !important;
        display: flex !important; transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: #333 !important; border-color: #FF4B4B !important; transform: translateX(5px);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] [aria-checked="true"] {
        background-color: #FF4B4B !important; color: white !important; font-weight: bold !important;
    }

    /* BOTÕES GERAIS */
    [data-testid="stMain"] div[role="radiogroup"] label {
        padding: 15px 25px !important; background-color: #262626 !important;
        border-radius: 12px !important; border: 1px solid #444 !important;
        color: #FFF !important; margin-right: 15px !important;
        justify-content: center !important; display: inline-flex !important;
    }
    [data-testid="stMain"] div[role="radiogroup"] label:has(input:checked) {
        background-color: #FF4B4B !important; border: 2px solid white !important;
    }

    /* CARDS */
    .history-card, .agenda-card {
        background-color: #1E1E1E; border-radius: 12px; padding: 20px;
        margin-bottom: 15px; border-left: 5px solid #FF4B4B;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .agenda-card { border-left-color: #00B4DB; }

    /* DASHBOARD CARDS */
    .dash-card { border-radius: 12px; padding: 20px; color: white; margin-bottom: 15px; height: 130px; border: 1px solid rgba(255,255,255,0.05); }
    .bg-orange { background: linear-gradient(160deg, #FF9800 0%, #F57C00 100%); }
    .bg-blue { background: linear-gradient(160deg, #00B4DB 0%, #0083B0 100%); }
    .bg-red { background: linear-gradient(160deg, #FF416C 0%, #FF4B2B 100%); }
    .bg-green { background: linear-gradient(160deg, #11998e 0%, #38ef7d 100%); }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO AUXILIAR DE FORMATAÇÃO (NOVO!) ---
def formatar_moeda(valor):
    # Transforma 1250.50 em "1.250,50"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- CONEXÕES E DADOS ---
def conectar_google_sheets():
    ID = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg"
    try:
        if os.path.exists("chave_google.json"): client = gspread.service_account(filename="chave_google.json")
        else: client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        return client.open_by_key(ID)
    except: return None

def carregar_dados(aba):
    sheet = conectar_google_sheets()
    if sheet is None: return pd.DataFrame()
    try: return pd.DataFrame(sheet.worksheet(aba).get_all_records())
    except: return pd.DataFrame()

def salvar_no_google(aba, linha):
    sheet = conectar_google_sheets()
    if sheet is None: return False
    try:
        ws = sheet.worksheet(aba)
        if not ws.get_all_values(): ws.append_row(list(linha.keys()))
        ws.append_row(list(linha.values()))
        return True
    except: return False

def carregar_catalogo():
    return pd.DataFrame({
        "Categoria": ["Hatch/Compacto", "Sedã", "SUV/Caminhonete", "Picapes Grandes", "Vans/Utilitários"],
        "Lavagem Simples": [40.0, 50.0, 60.0, 70.0, 80.0],
        "Lavagem Técnica": [150.0, 170.0, 190.0, 210.0, 230.0],
        "Higienização Interna": [300.0, 300.0, 300.0, 350.0, 400.0],
        "Restauração Faróis": [200.0, 200.0, 200.0, 200.0, 200.0],
        "Cristalização Vidros": [90.0, 120.0, 150.0, 150.0, 150.0],
        "Vitrificação Pintura": [800.0, 900.0, 1100.0, 1300.0, 1300.0]
    })

# --- PDF ---
def gerar_pdf(cliente, carro, placa, servicos_com_precos, total):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=85, y=10, w=40) 
        pdf.ln(45) 
    else: pdf.ln(20)
    
    def txt(t): return t.encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Arial", "B", 16); pdf.cell(0, 10, txt=txt("JM DETAIL - Estética Automotiva Premium"), ln=True, align='C')
    pdf.set_font("Arial", size=10); pdf.cell(0, 10, txt=txt("Tucano - BA | Rua São João, 54 | (75) 99830-3753"), ln=True, align='C')
    pdf.ln(10); pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt=txt(f"CLIENTE: {cliente}"), ln=True)
    pdf.cell(0, 10, txt=txt(f"VEÍCULO: {carro} | PLACA: {placa}"), ln=True)
    pdf.cell(0, 10, txt=txt(f"DATA: {datetime.now().strftime('%d/%m/%Y')}"), ln=True); pdf.ln(5)
    pdf.set_fill_color(240, 240, 240); pdf.cell(140, 10, txt=txt("Serviços Realizados"), border=1, fill=True)
    pdf.cell(50, 10, txt="Valor", border=1, ln=True, fill=True, align='C'); pdf.set_font("Arial", size=12)
    for s, v in servicos_com_precos.items():
        pdf.cell(140, 10, txt=txt(s), border=1); pdf.cell(50, 10, txt=txt(f"R$ {v:.2f}"), border=1, ln=True, align='C')
    pdf.ln(10); pdf.set_font("Arial", "B", 14); pdf.cell(140, 10, txt="TOTAL", align='R')
    pdf.cell(50, 10, txt=txt(f"R$ {total:.2f}"), border=1, align='C')
    return pdf.output(dest="S").encode("latin-1")

# --- PÁGINAS ---
def page_dashboard():
    st.title("📊 Painel de Controle")
    df_v = carregar_dados("Vendas"); df_d = carregar_dados("Despesas"); df_a = carregar_dados("Agendamentos")
    receita, despesa, pendente, count_p, lucro_vendas = 0.0, 0.0, 0.0, 0, 0.0
    
    if not df_v.empty:
        for c in ["Total", "Lucro Liquido"]:
            df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0)
        receita = df_v[df_v["Status"]=="Concluído"]["Total"].sum()
        pendente = df_v[df_v["Status"]=="Orçamento/Pendente"]["Total"].sum()
        count_p = len(df_v[df_v["Status"]=="Orçamento/Pendente"])
        lucro_vendas = df_v[df_v["Status"]=="Concluído"]["Lucro Liquido"].sum()
    if not df_d.empty:
        despesa = pd.to_numeric(df_d["Valor"].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0).sum()
    lucro_total = lucro_vendas - despesa

    # APLICAÇÃO DA FORMATAÇÃO NOS CARDS
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="dash-card bg-orange"><h4>PENDENTES ({count_p})</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(pendente)}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="dash-card bg-blue"><h4>FATURAMENTO</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(receita)}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="dash-card bg-red"><h4>DESPESAS</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(despesa)}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="dash-card bg-green"><h4>LUCRO LÍQUIDO</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_total)}</div></div>', unsafe_allow_html=True)
    
    st.write("---")
    col_g, col_a = st.columns([2, 1])
    with col_g:
        st.subheader("📈 Performance Financeira")
        if not df_v.empty:
            base = alt.Chart(df_v).encode(x=alt.X('Data', title='Histórico'))
            bars = base.mark_bar(size=40, cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                y='Total', color=alt.Color('Status', scale=alt.Scale(domain=['Concluído', 'Orçamento/Pendente'], range=['#00B4DB', '#FF8C00']), legend=None))
            line = base.mark_line(color='#39FF14', strokeWidth=3).encode(y='Lucro Liquido')
            st.altair_chart(alt.layer(bars, line).properties(height=380), use_container_width=True)
    with col_a:
        st.subheader("📅 Próximos na Agenda")
        if df_a.empty: st.info("Agenda livre.")
        else:
            for _, r in df_a.tail(4).iloc[::-1].iterrows():
                st.markdown(f'<div style="background:#1E1E1E; padding:12px; border-radius:10px; margin-bottom:8px; border-left:3px solid #00B4DB"><div style="font-size:12px; color:#00B4DB"><b>{r["Data"]} às {r["Hora"]}</b></div><div style="font-size:14px; font-weight:bold">{r["Veiculo"]}</div><div style="font-size:12px; color:#aaa">{r["Cliente"]}</div></div>', unsafe_allow_html=True)

def page_agendamento():
    st.title("📅 Agenda de Serviços Integrada")
    tab_list, tab_new = st.tabs(["📋 Próximos Serviços", "➕ Agendar Novo Carro"])
    df_cat = carregar_catalogo()
    
    with tab_new:
        st.markdown("### 📝 Dados do Agendamento")
        c1, c2 = st.columns(2)
        cli = c1.text_input("Cliente"); veic = c1.text_input("Modelo Veículo"); placa = c1.text_input("Placa")
        dt = c2.date_input("Data", min_value=date.today()); hr = c2.selectbox("Horário", ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"])
        cat = c2.selectbox("Categoria:", df_cat["Categoria"])
        
        servs_disp = [c for c in df_cat.columns if c != "Categoria"]
        escolhidos = st.multiselect("Serviços:", servs_disp, placeholder="Escolha os serviços do catálogo...")
        
        st.write("---")
        extra_n = st.text_input("Serviço Extra (Opcional)")
        extra_v = st.number_input("Valor do Serviço Extra (R$)", min_value=0.0)
        
        quem = st.radio("Quem vai executar?", ["Eu Mesmo", "Irmão/Equipe"], horizontal=True)
        
        precos_dict = {s: df_cat[df_cat["Categoria"] == cat][s].values[0] for s in escolhidos}
        total = sum(precos_dict.values()) + extra_v
        comissao = total * 0.40 if "Irmão" in quem else 0.0
        lucro = total - (total * 0.10) - comissao
        
        st.markdown(f"<div style='background:#262730;padding:15px;border-radius:10px;border:1px solid #444'><h4>Orçamento Previsto: {formatar_moeda(total)}</h4><p style='color:#39FF14; margin:0'>Lucro Final JM: {formatar_moeda(lucro)}</p></div>", unsafe_allow_html=True)
        
        if st.button("Confirmar Agendamento", use_container_width=True):
            if cli and veic and (escolhidos or extra_v > 0):
                servicos_finais = ", ".join(escolhidos)
                if extra_n: servicos_finais += f" (+ {extra_n})"
                
                dados = {"Data": dt.strftime("%d/%m/%Y"), "Hora": hr, "Cliente": cli, "Veiculo": veic, "Placa": placa, "Servicos": servicos_finais, "Total": total, "Executor": quem, "LucroPrevisto": lucro}
                if salvar_no_google("Agendamentos", dados):
                    st.success("✅ Agendado com sucesso!"); st.balloons()
                else: st.error("❌ ERRO AO CONECTAR: Verifique a aba 'Agendamentos' na planilha.")
            else: st.error("Preencha o cliente e pelo menos um serviço!")
    
    with tab_list:
        df_a = carregar_dados("Agendamentos")
        if df_a.empty: st.info("Sua agenda está vazia.")
        else:
            for i, r in df_a.iterrows():
                with st.container():
                    st.markdown(f'<div class="agenda-card"><b>📅 {r["Data"]} - ⏰ {r["Hora"]}</b><br>🚗 {r["Veiculo"]} ({r["Cliente"]})<br><small>Serviço: {r["Servicos"]}</small><br><b>Valor: {formatar_moeda(float(r["Total"]))}</b></div>', unsafe_allow_html=True)
                    if st.button(f"🏁 Concluir e Efetivar: {r['Veiculo']}", key=f"efet_{i}"):
                        nova_venda = {"Data": r["Data"], "Cliente": r["Cliente"], "Carro": r["Veiculo"], "Placa": r["Placa"], "Serviços": r["Servicos"], "Total": r["Total"], "Status": "Concluído", "Lucro Liquido": r["LucroPrevisto"]}
                        if salvar_no_google("Vendas", nova_venda):
                            st.success("🚀 Serviço Efetivado!")
                            st.rerun()
                        else: st.error("Erro ao salvar venda.")

def page_despesas():
    st.title("💸 Despesas Externas")
    c1, c2 = st.columns([3, 1]); desc = c1.text_input("Descrição"); val = c2.number_input("Valor", min_value=0.0)
    if st.button("Lançar"):
        if salvar_no_google("Despesas", {"Data": datetime.now().strftime("%d/%m/%Y"), "Descricao": desc, "Valor": val}): st.success("Salvo!")
        else: st.error("Erro ao conectar na planilha.")

def page_historico():
    st.title("📂 Garagem & Histórico")
    df = carregar_dados("Vendas")
    if df.empty: st.info("Sem registros."); return
    busca = st.text_input("🔍 Buscar...").strip().lower(); df_f = df.iloc[::-1]
    if busca: df_f = df_f[df_f.apply(lambda r: busca in str(r).lower(), axis=1)]
    for _, r in df_f.iterrows():
        cor = "#28a745" if r['Status'] == "Concluído" else "#ffc107"
        total_formatado = formatar_moeda(float(r["Total"]))
        st.markdown(f'<div class="history-card" style="border-left-color: {cor}"><div style="display: flex; justify-content: space-between"><div><h3>🚗 {r["Carro"]}</h3><p>{r["Cliente"]} • {r["Data"]}</p><small>{r["Serviços"]}</small></div><div style="text-align: right"><h2 style="color: #38ef7d">{total_formatado}</h2><span>{r["Status"]}</span></div></div></div>', unsafe_allow_html=True)

# --- MENU COM META E DUAS LOGOS ---
with st.sidebar:
    if os.path.exists("logo_sidebar.png"): st.image("logo_sidebar.png", use_container_width=True)
    elif os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    
    menu = st.radio("NAVEGAÇÃO", ["DASHBOARD", "AGENDAMENTO", "DESPESAS", "HISTÓRICO"], label_visibility="collapsed")
    st.write("---")
    
    # META MENSAL (Com formatação BR)
    df_meta = carregar_dados("Vendas")
    if not df_meta.empty:
        for c in ["Total"]:
            df_meta[c] = pd.to_numeric(df_meta[c].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0)
        
        total_vendido = df_meta[df_meta["Status"]=="Concluído"]["Total"].sum()
        META_MENSAL = 5000.00
        progresso = min(total_vendido / META_MENSAL, 1.0)
        
        st.markdown(f"""
        <div style="background-color: #1E1E1E; padding: 15px; border-radius: 10px; border: 1px solid #333; margin-bottom: 5px;">
            <p style="margin: 0; font-size: 14px; color: #aaa; text-transform: uppercase; letter-spacing: 1px;">Meta do Mês 🎯</p>
            <p style="margin: 5px 0 0 0; font-size: 22px; font-weight: bold; color: #FFF;">
                {formatar_moeda(total_vendido)} <span style="font-size:14px; color:#666; font-weight:normal;">/ {formatar_moeda(META_MENSAL)}</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(progresso)
        if progresso >= 1.0: st.success("🚀 META BATIDA! PARABÉNS!")

    st.markdown("<div style='text-align: center; color: #444; font-size: 11px; margin-top: 30px;'>v6.2 Platinum • JM System</div>", unsafe_allow_html=True)

if menu == "DASHBOARD": page_dashboard()
elif menu == "AGENDAMENTO": page_agendamento()
elif menu == "DESPESAS": page_despesas()
elif menu == "HISTÓRICO": page_historico()