import streamlit as st
from core.database import carregar_dados
from utils.helpers import formatar_moeda

def exibir_historico():
    st.title("📜 Histórico de Serviços")
    
    df = carregar_dados("Agendamentos")
    
    if df.empty:
        st.write("Nenhum histórico encontrado.")
        return

    # Mostra os serviços do mais novo para o mais antigo
    df_invertido = df.iloc[::-1]
    
    for i, row in df_invertido.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="history-card">
                <b>{row['Data']}</b> - {row['Cliente']} <br>
                <small>{row['Veículo']} ({row['Placa']})</small><br>
                <span style="color: #38ef7d;">{formatar_moeda(row['Preço'])}</span> | 
                <span style="color: #888;">{row['Status']}</span>
            </div>
            """, unsafe_allow_html=True)
