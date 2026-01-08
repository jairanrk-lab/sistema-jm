import streamlit as st
import pandas as pd
import os
import altair as alt
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="JM Detail System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILO (Dark Mode - JM Detail Premium) ---
st.markdown("""
<style>
    /* Fundo Preto Profundo */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Títulos e Cabeçalhos */
    h1, h2, h3 { color: #ff4b4b !important; font-family: 'Arial', sans-serif; }
    
    /* Textos Gerais */
    p, .stMarkdown, .stRadio label { color: #e0e0e0 !important; font-size: 16px !important; }
    
    /* Inputs e Labels */
    .stTextInput>label, .stNumberInput>label, .stSelectbox>label, .stMultiSelect>label {
        color: #ffffff !important; font-weight: bold !important;
    }
    .stTextInput>div>div>input { background-color: #262730; color: white; border-radius: 5px; }
    
    /* Botões */
    .stButton>button {
        background-color: #ff0000; color: white; font-weight: bold; 
        border-radius: 8px; border: none; transition: 0.3s;
    }
    .stButton>button:hover { 
        background-color: #b30000; box-shadow: 0px 0px 10px #ff0000;
    }
    
    /* Menu Lateral */
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #333; }
    
    /* Métricas */
    [data-testid="stMetricValue"] { font-size: 26px !important; color: #ffffff !important; }
    [data-testid="stMetricLabel"] { font-size: 16px !important; color: #aaaaaa !important; }
</style>
""", unsafe_allow_html=True)

# --- ARQUIVOS DE DADOS ---
DB_VENDAS = "orcamentos_jm.csv"
DB_DESPESAS = "despesas_jm.csv"

# --- FUNÇÕES ---
def carregar_vendas():
    if not os.path.exists(DB_VENDAS):
        return pd.DataFrame(columns=["Data", "Cliente", "Carro", "Placa", "Serviços", "Total", "Status", "Pagamento"])
    return pd.read_csv(DB_VENDAS)

def carregar_despesas():
    if not os.path.exists(DB_DESPESAS):
        return pd.DataFrame(columns=["Data", "Descricao", "Categoria", "Valor"])
    return pd.read_csv(DB_DESPESAS)

def salvar_venda(cliente, carro, placa, servicos, total, status, pagamento):
    novo = {
        "Data": [datetime.now().strftime("%d/%m/%Y %H:%M")],
        "Cliente": [cliente], "Carro": [carro], "Placa": [placa],
        "Serviços": [", ".join(servicos)], "Total": [total],
        "Status": [status], "Pagamento": [pagamento]
    }
    df = pd.DataFrame(novo)
    modo = 'a' if os.path.exists(DB_VENDAS) else 'w'
    header = not os.path.exists(DB_VENDAS)
    df.to_csv(DB_VENDAS, mode=modo, header=header, index=False)

def salvar_despesa(descricao, categoria, valor):
    novo = {
        "Data": [datetime.now().strftime("%d/%m/%Y %H:%M")],
        "Descricao": [descricao], "Categoria": [categoria], "Valor": [valor]
    }
    df = pd.DataFrame(novo)
    modo = 'a' if os.path.exists(DB_DESPESAS) else 'w'
    header = not os.path.exists(DB_DESPESAS)
    df.to_csv(DB_DESPESAS, mode=modo, header=header, index=False)

def carregar_catalogo():
    dados = {
        "Categoria": ["Hatch/Compacto", "Sedã", "SUV/Caminhonete", "Picapes Grandes", "Moto (Até 300cc)", "Moto (Acima 300cc)"],
        "Lavagem Simples": [40, 50, 60, 70, 30, 40],
        "Lavagem Detalhada": [150, 170, 190, 210, 50, 100],
        "Higienização Interna": [300, 300, 300, 350, 0, 0],
        "Vitrificação de Pintura": [800, 900, 1100, 1300, 150, 250],
        "Restauração de Faróis": [200, 200, 200, 200, 50, 50],
        "Cristalização de Vidros": [90, 120, 150, 150, 30, 30],
        "Limpeza Técnica de Motor": [100, 100, 100, 120, 30, 50],
        "Vitrificação de Motor": [120, 120, 120, 140, 80, 100]
    }
    return pd.DataFrame(dados)

def gerar_pdf(cliente, carro, placa, servicos, total, status):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    def texto(t): return t.encode('latin-1', 'replace').decode('latin-1')
    
    # Cabeçalho
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt=texto("JM DETAIL - Estética Automotiva"), ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt=texto("Tucano - BA | Especialista em Detalhamento"), ln=True, align='C')
    pdf.ln(10)
    
    # Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt=texto(f"CLIENTE: {cliente}"), ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=texto(f"Veículo: {carro} | Placa: {placa}"), ln=True)
    pdf.cell(0, 10, txt=texto(f"Data: {datetime.now().strftime('%d/%m/%Y')} | Status: {status}"), ln=True)
    pdf.ln(5)
    
    # Tabela
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(140, 10, txt=texto("Serviço"), border=1, fill=True)
    pdf.cell(50, 10, txt="Valor", border=1, ln=True, fill=True)
    pdf.set_font("Arial", size=12)
    
    for servico in servicos:
        try: nome, valor = servico.rsplit("(", 1); valor = "(" + valor
        except: nome, valor = servico, "-"
        pdf.cell(140, 10, txt=texto(nome.strip()), border=1)
        pdf.cell(50, 10, txt=texto(valor), border=1, ln=True)
        
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(140, 10, txt="TOTAL", align='R')
    pdf.cell(50, 10, txt=texto(f"R$ {total:.2f}"), border=1, align='C')
    pdf.ln(20)
    pdf.cell(0, 10, txt="_"*50, ln=True, align='C')
    pdf.cell(0, 10, txt=texto("Assinatura JM Detail"), ln=True, align='C')
    
    return pdf.output(dest="S").encode("latin-1")

# --- PÁGINAS ---

def page_dashboard():
    st.title("📊 Painel de Controle")
    
    df_vendas = carregar_vendas()
    df_despesas = carregar_despesas()
    
    # Cálculos
    if not df_vendas.empty:
        receita = df_vendas[df_vendas["Status"] == "Concluído"]["Total"].sum()
        a_receber = df_vendas[df_vendas["Status"] == "Orçamento/Pendente"]["Total"].sum()
    else: receita, a_receber = 0.0, 0.0
        
    if not df_despesas.empty: despesa = df_despesas["Valor"].sum()
    else: despesa = 0.0
        
    lucro = receita - despesa
    
    # Métricas Estilizadas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Entradas", f"R$ {receita:.2f}")
    c2.metric("💸 Saídas", f"R$ {despesa:.2f}")
    c3.metric("📈 Lucro Líquido", f"R$ {lucro:.2f}", delta="Saldo Final")
    c4.metric("⏳ A Receber", f"R$ {a_receber:.2f}")
    
    st.write("---")
    
    # GRÁFICO SLIM FIT (Barras Finas)
    col_grafico, _ = st.columns([2, 1]) 
    
    with col_grafico:
        st.subheader("Balanço Financeiro")
        dados_grafico = pd.DataFrame({
            "Tipo": ["Receitas", "Despesas"],
            "Valor": [receita, despesa],
        })
        
        # Ajuste: size=50 define a largura da barra
        grafico = alt.Chart(dados_grafico).mark_bar(
            cornerRadiusTopLeft=10, 
            cornerRadiusTopRight=10,
            size=60  # <--- BARRAS MAIS FINAS AQUI
        ).encode(
            x=alt.X('Tipo', axis=None), 
            y=alt.Y('Valor', axis=alt.Axis(title='Valor (R$)', grid=False)),
            color=alt.Color('Tipo', scale=alt.Scale(domain=['Receitas', 'Despesas'], range=['#00FF00', '#FF0000']), legend=None),
            tooltip=['Tipo', 'Valor']
        ).properties(
            height=350,
            background='#0e1117'
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            labelColor='#ffffff',
            titleColor='#ffffff',
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            color='#ffffff'
        )
        
        st.altair_chart(grafico, use_container_width=True)

def page_orcamentos():
    st.title("📝 Novo Serviço")
    c1, c2 = st.columns(2)
    cliente = c1.text_input("Cliente")
    zap = c1.text_input("WhatsApp (Opcional)")
    carro = c2.text_input("Veículo")
    placa = c2.text_input("Placa")
    
    st.write("---")
    df_cat = carregar_catalogo()
    cat = st.selectbox("Categoria:", df_cat["Categoria"])
    precos = df_cat[df_cat["Categoria"] == cat].iloc[0]
    servs = st.multiselect("Serviços:", [c for c in df_cat.columns if c != "Categoria"])
    
    ce1, ce2 = st.columns([3, 1])
    extra_nome = ce1.text_input("Serviço Extra")
    extra_val = ce2.number_input("Valor Extra", min_value=0.0)
    
    total = sum([precos[s] for s in servs]) + extra_val
    lista = [f"{s} (R$ {precos[s]})" for s in servs]
    if extra_val > 0: lista.append(f"{extra_nome} (R$ {extra_val})")
    
    st.subheader(f"Total: R$ {total:.2f}")
    
    col_st, col_pg = st.columns(2)
    status = col_st.selectbox("Status", ["Orçamento/Pendente", "Concluído"])
    pagamento = col_pg.selectbox("Pagamento", ["Aguardando", "Pix", "Cartão", "Dinheiro"])
    
    if st.button("💾 Salvar Serviço"):
        if cliente:
            salvar_venda(cliente, carro, placa, lista, total, status, pagamento)
            st.success("Registrado!")
            
            pdf = gerar_pdf(cliente, carro, placa, lista, total, status)
            st.download_button("📄 Baixar PDF da OS", pdf, f"OS_{cliente}.pdf", "application/pdf")
            
            msg = f"*JM DETAIL*\nOlá {cliente}!\nVeículo: {carro}\n*Total: R$ {total:.2f}*\nStatus: {status}"
            st.code(msg, language="text")
        else: st.warning("Nome obrigatório.")

def page_despesas():
    st.title("💸 Registrar Despesas")
    c1, c2 = st.columns([3, 1])
    desc = c1.text_input("Descrição (Ex: Luz, Água, Produtos)")
    cat = c1.selectbox("Categoria", ["Insumos", "Funcionários", "Fixas", "Outros"])
    val = c2.number_input("Valor (R$)", min_value=0.0)
    
    if st.button("Registrar Saída"):
        if desc and val > 0:
            salvar_despesa(desc, cat, val)
            st.success(f"Saída de R$ {val} lançada!")
    
    df = carregar_despesas()
    if not df.empty:
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)

def page_clientes():
    st.title("👥 Histórico Geral")
    df = carregar_vendas()
    if not df.empty: st.dataframe(df, use_container_width=True)

# --- NAVEGAÇÃO ---
st.sidebar.image("https://img.icons8.com/ios-filled/100/ff0000/car-cleaning.png", width=80)
st.sidebar.title("JM DETAIL")
menu = st.sidebar.radio("Menu", ["Dashboard", "Novo Serviço", "Despesas", "Clientes"])

if menu == "Dashboard": page_dashboard()
elif menu == "Novo Serviço": page_orcamentos()
elif menu == "Despesas": page_despesas()
elif menu == "Clientes": page_clientes()