import streamlit as st
import pandas as pd
from core.database import carregar_dados
from utils.helpers import formatar_moeda

def exibir_financeiro():
    st.title("💰 Gestão Financeira")
    
    df = carregar_dados("Agendamentos")
    
    if df.empty:
        st.info("Aguardando dados para exibir o financeiro.")
        return

    # Filtro apenas de serviços concluídos (dinheiro no bolso)
    pagos = df[df['Status'] == 'Concluído']
    total = pagos['Preço'].sum()

    st.metric("Total Faturado (Bruto)", formatar_moeda(total))

    # Tabela simples de faturamento
    if not pagos.empty:
        st.subheader("Entradas Detalhadas")
        st.dataframe(pagos[['Data', 'Cliente', 'Veículo', 'Preço']], use_container_width=True)
