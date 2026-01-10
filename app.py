import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date, time, timedelta
from fpdf import FPDF
import gspread
import os
import time as t_sleep
import urllib.parse

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
                    try: st.query_params["acesso_liberado"] = "sim_mestre"
                    except: pass
                    st.rerun()
                else: st.error("Senha incorreta.")
    return False

if not check_password(): st.stop()

# ==============================================================================
# --- 3. ESTILO CSS (DARK NEON PREMIUM) ---
# ==============================================================================
st.markdown("""
<style>
    /* FONTE E GERAL */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    @import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css");
    * { font-family: 'Poppins', sans-serif !important; }
    
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] { background-color: #000000 !important; }
    .block-container { padding-top: 1rem; padding-bottom: 6rem; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }

    /* MENU DE NAVEGAÇÃO SUPERIOR */
    div[role="radiogroup"] {
        display: flex !important; flex-direction: row !important; width: 100% !important;
        justify-content: space-between !important; background-color: transparent !important;
        border: none !important; padding: 0 !important; gap: 12px !important; overflow: visible !important;
    }
    div[role="radiogroup"] label {
        flex: 1 !important; background-color: #111 !important; border: 1px solid #333 !important;
        padding: 12px 5px !important; border-radius: 8px !important; transition: all 0.3s ease !important;
        margin: 0 !important; color: #888 !important; font-weight: 600 !important; font-size: 16px !important;
        display: flex; align-items: center; justify-content: center !important;
    }
    /* ÍCONES DO MENU */
    div[role="radiogroup"] label:nth-of-type(1)::before { font-family: "bootstrap-icons"; content: "\\F5A6"; margin-right: 8px; font-size: 18px; }
    div[role="radiogroup"] label:nth-of-type(2)::before { font-family: "bootstrap-icons"; content: "\\F20E"; margin-right: 8px; font-size: 18px; }
    div[role="radiogroup"] label:nth-of-type(3)::before { font-family: "bootstrap-icons"; content: "\\F23E"; margin-right: 8px; font-size: 18px; }
    div[role="radiogroup"] label:nth-of-type(4)::before { font-family: "bootstrap-icons"; content: "\\F4E9"; margin-right: 8px; font-size: 18px; }
    div[role="radiogroup"] label:nth-of-type(5)::before { font-family: "bootstrap-icons"; content: "\\F291"; margin-right: 8px; font-size: 18px; }

    div[role="radiogroup"] label:hover { border-color: #D90429 !important; color: white !important; background-color: #1a1a1a !important; transform: translateY(-2px); }
    div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(90deg, #D90429 0%, #8D021F 100%) !important; color: white !important;
        border-color: #D90429 !important; box-shadow: 0 4px 15px rgba(217, 4, 41, 0.4) !important;
    }

    /* CARDS */
    .dash-card { border-radius: 15px; padding: 20px; color: white; margin-bottom: 20px; border: 1px solid #333; position: relative; overflow: hidden; height: 140px !important; display: flex; flex-direction: column; justify-content: center; }
    .card-icon-bg { position: absolute !important; top: -10px !important; right: -10px !important; font-size: 100px !important; opacity: 0.15 !important; transform: rotate(15deg) !important; pointer-events: none !important; color: white !important; }
    .bg-orange { background: linear-gradient(145deg, #FF9800, #F57C00); }
    .bg-blue { background: linear-gradient(145deg, #00B4DB, #0083B0); }
    .bg-red { background: linear-gradient(145deg, #D90429, #8D021F); }
    .bg-green { background: linear-gradient(145deg, #11998e, #38ef7d); }
    
    /* AGENDA & HISTÓRICO */
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
    try: ID = st.secrets["app"]["spreadsheet_id"]
    except: ID = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg" # Seu ID aqui
    try:
        if os.path.exists("chave_google.json"): client = gspread.service_account(filename="chave_google.json")
        else: client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        return client.open_by_key(ID)
    except Exception as e: return None

def carregar_dados(aba):
    sheet = conectar_google_sheets()
    if sheet is None: return pd.DataFrame()
    try: return pd.DataFrame(sheet.worksheet(aba).get_all_records())
    except: return pd.DataFrame()

# --- NOVO: CATÁLOGO DINÂMICO VIA GOOGLE SHEETS ---
@st.cache_data(ttl=600) # Atualiza a cada 10 minutos
def carregar_catalogo_nuvem():
    sheet = conectar_google_sheets()
    try:
        ws = sheet.worksheet("Catalogo")
        df = pd.DataFrame(ws.get_all_records())
        # Garante que Preco é float
        df["Preco"] = pd.to_numeric(df["Preco"], errors='coerce').fillna(0.0)
        return df
    except:
        # Fallback de Segurança (Se a internet cair ou aba não existir)
        return pd.DataFrame({
            "Categoria": ["Hatch", "Sedã", "SUV"],
            "Servico": ["Lavagem Simples", "Lavagem Simples", "Lavagem Simples"],
            "Preco": [40.0, 50.0, 60.0]
        })

def verificar_conflito_horario(data_str, hora_str):
    df_a = carregar_dados("Agendamentos")
    if df_a.empty: return False
    # Filtra por data e hora exata (Pode aprimorar para intervalo depois)
    conflito = df_a[(df_a["Data"] == data_str) & (df_a["Hora"] == hora_str)]
    return not conflito.empty

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

def gerar_link_whatsapp(telefone, cliente, veiculo, data, hora, total):
    msg = f"Olá {cliente}, seu agendamento na JM Detail para o *{veiculo}* está confirmado!\n\n📅 Data: {data}\n⏰ Horário: {hora}\n💲 Total Estimado: {formatar_moeda(total)}\n\nLocal: Rua São João, 54 - Tucano/BA."
    msg_encoded = urllib.parse.quote(msg)
    if telefone:
        # Remove caracteres não numéricos
        tel_limpo = "".join(filter(str.isdigit, str(telefone)))
        link = f"https://wa.me/55{tel_limpo}?text={msg_encoded}"
    else:
        link = f"https://wa.me/?text={msg_encoded}" # Link genérico para escolher contato
    return link

def obter_icone_html(cat):
    if not isinstance(cat, str): return '<i class="bi bi-car-front-fill"></i>'
    c = cat.lower()
    if "moto" in c: return '<i class="bi bi-motorcycle"></i>'
    elif "suv" in c or "picape" in c or "caminhonete" in c: return '<i class="bi bi-truck-front-fill"></i>'
    elif "van" in c: return '<i class="bi bi-bus-front-fill"></i>'
    else: return '<i class="bi bi-car-front-fill"></i>'

# ==============================================================================
# --- CABEÇALHO E NAVEGAÇÃO ---
# ==============================================================================
c_logo1, c_logo2, c_logo3 = st.columns([1,2,1])
with c_logo2:
    st.markdown("<h1 style='text-align:center; color:#D90429; font-weight:800; margin-bottom:0px'>JM DETAIL</h1>", unsafe_allow_html=True)

st.write("") 
menu_opcoes = ["DASHBOARD", "AGENDA", "FINANCEIRO", "DESPESAS", "HISTÓRICO"]
menu_selecionado = st.radio("Navegação", menu_opcoes, horizontal=True, label_visibility="collapsed")
st.write("---") 

# ==============================================================================
# --- PÁGINAS ---
# ==============================================================================

def page_dashboard():
    hoje = datetime.now()
    mes_atual, ano_atual = hoje.month, hoje.year
    nome_meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    st.markdown(f'## <i class="bi bi-speedometer2" style="color: #00B4DB;"></i> Painel Geral <small style="font-size:14px; color:#888">| {nome_meses[mes_atual]}/{ano_atual}</small>', unsafe_allow_html=True)
    
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    
    receita_mes, despesa_mes, pendente_total, count_p = 0.0, 0.0, 0.0, 0
    lucro_final = 0.0
    
    if not df_v.empty:
        for c in ["Total"]:
            if c in df_v.columns: df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
        
        df_v['Data_dt'] = pd.to_datetime(df_v['Data'], format='%d/%m/%Y', errors='coerce')
        df_mes = df_v[(df_v['Data_dt'].dt.month == mes_atual) & (df_v['Data_dt'].dt.year == ano_atual)]
        
        receita_mes = df_mes[df_mes["Status"]=="Concluído"]["Total"].sum()
        lucro_operacional = receita_mes * 0.50
        pendente_total = df_v[df_v["Status"]=="Orçamento/Pendente"]["Total"].sum()
        count_p = len(df_v[df_v["Status"]=="Orçamento/Pendente"])

    if not df_d.empty:
        df_d['Data_dt'] = pd.to_datetime(df_d['Data'], format='%d/%m/%Y', errors='coerce')
        df_d_mes = df_d[(df_d['Data_dt'].dt.month == mes_atual) & (df_d['Data_dt'].dt.year == ano_atual)]
        despesa_mes = pd.to_numeric(df_d_mes["Valor"].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0).sum()
    
    lucro_final = lucro_operacional - despesa_mes
    
    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="dash-card bg-orange"><i class="bi bi-hourglass-split card-icon-bg"></i><h4>PENDENTES</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(pendente_total)}</div><small>{count_p} na fila</small></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="dash-card bg-blue"><i class="bi bi-currency-dollar card-icon-bg"></i><h4>FATURAMENTO</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(receita_mes)}</div><small>Mês Atual</small></div>', unsafe_allow_html=True)
    
    c3, c4 = st.columns(2)
    with c3: st.markdown(f'<div class="dash-card bg-red"><i class="bi bi-graph-down-arrow card-icon-bg"></i><h4>DESPESAS</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(despesa_mes)}</div><small>Gastos</small></div>', unsafe_allow_html=True)
    cor_lucro = "bg-green" if lucro_final >= 0 else "bg-red"
    with c4: st.markdown(f'<div class="dash-card {cor_lucro}"><i class="bi bi-wallet2 card-icon-bg"></i><h4>LUCRO LÍQUIDO</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_final)}</div><small>Resultado Real</small></div>', unsafe_allow_html=True)

    st.write("---")
    
    # NOVO GRÁFICO DE EVOLUÇÃO FINANCEIRA
    st.markdown('### <i class="bi bi-graph-up-arrow" style="color: #39FF14;"></i> Evolução Financeira', unsafe_allow_html=True)
    if not df_v.empty:
        df_chart = df_v[df_v["Status"]=="Concluído"].copy()
        if not df_chart.empty:
            df_chart["Mes"] = df_chart["Data_dt"].dt.strftime("%Y-%m")
            df_agrupado = df_chart.groupby("Mes")["Total"].sum().reset_index()
            
            chart = alt.Chart(df_agrupado).mark_area(
                line={'color':'#39FF14'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#39FF14', offset=0),
                           alt.GradientStop(color='transparent', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x=alt.X('Mes', title='Mês'),
                y=alt.Y('Total', title='Faturamento'),
                tooltip=['Mes', 'Total']
            ).properties(height=300, background='transparent')
            st.altair_chart(chart, use_container_width=True)
        else: st.info("Sem dados concluídos para gráfico.")

def page_financeiro():
    st.markdown('## <i class="bi bi-cash-coin" style="color: #28a745;"></i> Gestão Financeira', unsafe_allow_html=True)
    df_v = carregar_dados("Vendas")
    comissao_pendente = 0.0; fundo_caixa = 0.0
    
    if not df_v.empty:
        if "Status Comissao" not in df_v.columns: df_v["Status Comissao"] = "Pendente"
        for c in ["Total", "Valor Comissao", "Fundo Caixa"]:
            if c in df_v.columns: df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
        
        df_pendente = df_v[df_v["Status Comissao"] != "Pago"]
        for index, row in df_pendente.iterrows():
             if row.get("Valor Comissao", 0) > 0 or "Equipe" in str(row.get("Funcionario", "")):
                 comissao_pendente += (row["Total"] * 0.40)
        fundo_caixa = df_v["Fundo Caixa"].sum()
    
    st.info(f"Caixa da Empresa (Acumulado): {formatar_moeda(fundo_caixa)}")
    
    col1, col2 = st.columns([2,1])
    with col1: st.metric("Comissões Pendentes (Recalculado 40%)", formatar_moeda(comissao_pendente))
    with col2:
        if comissao_pendente > 0:
            if st.button("Pagar Comissões"):
                sheet = conectar_google_sheets(); ws = sheet.worksheet("Vendas"); dados = ws.get_all_records()
                header = ws.row_values(1); col_idx = header.index("Status Comissao") + 1
                for i, linha in enumerate(dados):
                    v = pd.to_numeric(str(linha.get("Valor Comissao", "0")).replace('R$', '').replace(',', '.'), errors='coerce')
                    if v > 0 and str(linha.get("Status Comissao", "")) != "Pago": ws.update_cell(i + 2, col_idx, "Pago")
                st.success("Pago!"); t_sleep.sleep(1); st.rerun()

def page_agendamento():
    st.markdown('## <i class="bi bi-calendar-check" style="color: white;"></i> Agenda Integrada', unsafe_allow_html=True)
    tab_new, tab_list = st.tabs(["NOVO AGENDAMENTO", "LISTA DE SERVIÇOS"]) 
    
    # Carrega Catálogo da Nuvem (Nova Funcionalidade)
    with st.spinner("Sincronizando catálogo de preços..."):
        df_catalogo_nuvem = carregar_catalogo_nuvem()
    
    with tab_new:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            cli = c1.text_input("Nome do Cliente")
            tel = c1.text_input("WhatsApp (DDD+Número)", placeholder="Ex: 75999998888")
            veic = c2.text_input("Modelo do Veículo")
            placa = c2.text_input("Placa")
            
            c3, c4 = st.columns(2)
            dt = c3.date_input("Data", value=date.today(), format="DD/MM/YYYY")
            hr = c4.time_input("Horário", value=time(8, 0))
            
            # Seleção Dinâmica baseada no Catálogo
            lista_categorias = df_catalogo_nuvem["Categoria"].unique().tolist()
            cat = st.selectbox("Categoria do Veículo:", lista_categorias)
            
            # Filtra serviços da categoria selecionada
            servicos_da_categoria = df_catalogo_nuvem[df_catalogo_nuvem["Categoria"] == cat]
            opcoes_servico = servicos_da_categoria["Servico"].tolist()
            
            escolhidos = st.multiselect("Selecione os Serviços:", opcoes_servico)
            
            st.divider()
            ce1, ce2, ce3 = st.columns(3)
            extra_v = ce1.number_input("Valor Extra (R$)", min_value=0.0)
            desconto_v = ce2.number_input("Desconto (R$)", min_value=0.0)
            quem = ce3.radio("Executor:", ["Eu Mesmo", "Equipe"], horizontal=True)
            
            # Cálculo Dinâmico
            total = 0.0
            if escolhidos:
                for s in escolhidos:
                    preco = servicos_da_categoria[servicos_da_categoria["Servico"] == s]["Preco"].values[0]
                    total += float(preco)
            total = total + extra_v - desconto_v
            
            st.markdown(f"<h3 style='text-align:right; color:#39FF14'>Total: {formatar_moeda(total)}</h3>", unsafe_allow_html=True)
            
            if st.button("CONFIRMAR AGENDAMENTO", use_container_width=True):
                # 1. Validação de Conflito
                data_str = dt.strftime("%d/%m/%Y")
                hora_str = hr.strftime("%H:%M")
                
                if verificar_conflito_horario(data_str, hora_str):
                    st.error(f"⚠️ Já existe um agendamento para {data_str} às {hora_str}!")
                else:
                    serv_str = ", ".join(escolhidos)
                    dados = {
                        "Data": data_str, "Hora": hora_str, "Cliente": cli, 
                        "Telefone": tel, "Veiculo": veic, "Placa": placa, 
                        "Servicos": serv_str, "Total": total, "Executor": quem, 
                        "Categoria": cat
                    }
                    ok, msg = salvar_no_google("Agendamentos", dados)
                    if ok: 
                        st.success("Agendado com sucesso!")
                        # LINK WHATSAPP
                        link_wpp = gerar_link_whatsapp(tel, cli, veic, data_str, hora_str, total)
                        st.markdown(f"""
                            <a href="{link_wpp}" target="_blank">
                                <button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; width:100%; margin-top:10px; cursor:pointer;">
                                    <i class="bi bi-whatsapp"></i> ENVIAR CONFIRMAÇÃO NO WHATSAPP
                                </button>
                            </a>
                        """, unsafe_allow_html=True)
                    else: st.error(msg)

    with tab_list:
        df_a = carregar_dados("Agendamentos")
        if df_a.empty: st.info("Agenda vazia.")
        else:
            for i, r in df_a.iterrows():
                st.markdown(f"""
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
                        {obter_icone_html(r.get("Categoria", ""))} {r['Veiculo']} <span style="font-size:14px; color:#888">({r['Placa']})</span>
                    </div>
                    <div style="margin-top:5px; font-size:14px; color:#ccc">
                        <i class="bi bi-person-fill"></i> {r['Cliente']}
                    </div>
                    <div style="margin-top:10px; padding-top:10px; border-top:1px solid #333; font-size:13px; color:#888">
                        🔧 {r['Servicos']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button(f"✅ Concluir", key=f"ok_{i}", use_container_width=True):
                        total_bruto = float(r["Total"])
                        fundo = total_bruto * 0.10
                        comis = total_bruto * 0.40 if "Equipe" in r["Executor"] else 0.0
                        lucro = total_bruto - fundo - comis
                        venda = {"Data": r["Data"], "Cliente": r["Cliente"], "Carro": r["Veiculo"], "Placa": r["Placa"], "Serviços": r["Servicos"], "Total": total_bruto, "Status": "Concluído", "Funcionario": r["Executor"], "Valor Comissao": comis, "Fundo Caixa": fundo, "Lucro Liquido": lucro, "Status Comissao": "Pendente", "Categoria": r.get("Categoria", "")}
                        salvar_no_google("Vendas", venda)
                        excluir_agendamento(i)
                        st.rerun()
                with c_btn2:
                    if st.button(f"🗑️ Cancelar", key=f"del_{i}", use_container_width=True):
                        excluir_agendamento(i)
                        st.rerun()

def page_despesas():
    st.markdown('## <i class="bi bi-receipt" style="color: #D90429;"></i> Despesas', unsafe_allow_html=True)
    with st.form("form_desp"):
        desc = st.text_input("Descrição")
        val = st.number_input("Valor", min_value=0.0)
        if st.form_submit_button("Lançar"):
            salvar_no_google("Despesas", {"Data": datetime.now().strftime("%d/%m/%Y"), "Descricao": desc, "Valor": val})
            st.success("Salvo!")

def page_historico():
    st.markdown('## <i class="bi bi-clock-history" style="color: #FFC107;"></i> Garagem & Histórico', unsafe_allow_html=True)
    df = carregar_dados("Vendas")
    if df.empty: st.info("Nenhum serviço registrado ainda."); return

    busca = st.text_input("🔍 Buscar Cliente ou Carro...", placeholder="Ex: Fiat Toro ou João").strip().lower()
    df_f = df.iloc[::-1]
    
    if busca: df_f = df_f[df_f.apply(lambda r: busca in str(r).lower(), axis=1)]

    for index, r in df_f.iterrows():
        html_card = f"""
        <div class="history-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h3 style="margin: 0; font-size: 20px; color: white; font-weight: 700;">
                        {obter_icone_html(r.get("Categoria", ""))} {r["Carro"]}
                    </h3>
                    <p style="margin: 5px 0 0 0; color: #bbb; font-size: 14px;">
                        <i class="bi bi-person"></i> {r["Cliente"]} &nbsp;|&nbsp; {r["Placa"]}
                    </p>
                </div>
                <div style="text-align: right;">
                    <h2 style="margin: 0; color: #39FF14; font-weight: 700; font-size: 22px;">
                        {formatar_moeda(float(r["Total"]))}
                    </h2>
                    <span style="background-color: #222; padding: 4px 8px; border-radius: 6px; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #aaa;">
                        {r["Data"]}
                    </span>
                </div>
            </div>
            <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid #333; color: #888; font-size: 13px;">
                <i class="bi bi-tools"></i> {r["Serviços"]}
            </div>
        </div>
        """
        st.markdown(html_card, unsafe_allow_html=True)

# --- ROTEADOR ---
if "DASHBOARD" in menu_selecionado: page_dashboard()
elif "AGENDA" in menu_selecionado: page_agendamento()
elif "FINANCEIRO" in menu_selecionado: page_financeiro()
elif "DESPESAS" in menu_selecionado: page_despesas()
elif "HISTÓRICO" in menu_selecionado: page_historico()

# --- RODAPÉ ---
st.markdown('<div class="footer">Desenvolvido por <b>Jairan Jesus Matos</b> | JM Detail System © 2026</div>', unsafe_allow_html=True)
