import streamlit as st
from datetime import datetime
from core.database import carregar_dados, salvar_no_google
from utils.helpers import formatar_moeda

def exibir_despesas():
    st.title("💸 Controle de Despesas")
    
    # Formuário de Despesas
    with st.form("nova_despesa", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            item = st.text_input("Descrição da Despesa")
            valor = st.number_input("Valor (R$)", min_value=0.0, step=5.0)
        with col2:
            data = st.date_input("Data", datetime.now())
            cat = st.selectbox("Categoria", ["Produtos", "Aluguel", "Luz/Água", "Marketing", "Outros"])
            
        if st.form_submit_button("Registrar Gasto"):
            if item and valor > 0:
                nova_d = {
                    "Data": data.strftime("%d/%m/%Y"),
                    "Descrição": item,
                    "Categoria": cat,
                    "Valor": valor
                }
                salvar_no_google("Despesas", nova_d)
                st.success("Despesa salva!")
