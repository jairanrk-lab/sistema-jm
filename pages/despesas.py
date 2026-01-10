import streamlit as st
from datetime import datetime
from core.database import salvar_no_google

def exibir_despesas():
    st.markdown('## <i class="bi bi-receipt" style="color: #D90429;"></i> Despesas', unsafe_allow_html=True)
    with st.form("form_desp"):
        desc = st.text_input("Descrição")
        val = st.number_input("Valor", min_value=0.0)
        if st.form_submit_button("Lançar"):
            salvar_no_google("Despesas", {"Data": datetime.now().strftime("%d/%m/%Y"), "Descricao": desc, "Valor": val})
            st.success("Salvo!")
