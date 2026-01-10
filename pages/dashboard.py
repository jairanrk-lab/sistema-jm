import streamlit as st
import pandas as pd
from core.database import carregar_dados
from utils.helpers import formatar_moeda

def exibir_dashboard():
    st.markdown('<div class="main-title"><h1>📊 Painel Geral</h1></div>', unsafe_allow_html=True)
    
    # Carregar dados
    df_agendamentos = carregar_dados("Agendamentos")
    df_despesas = carregar_dados("Despesas")
    
    if df_agendamentos.empty:
        st.warning("Nenhum dado encontrado para o Dashboard.")
        return

    # Cálculos Simples
    total_faturado = df_agendamentos[df_agendamentos['Status'] == 'Concluído']['Preço'].sum()
    total_pendente = df_agendamentos[df_agendamentos['Status'] == 'Pendente']['Preço'].sum()
    total_despesas = df_despesas['Valor'].sum() if not df_despesas.empty else 0
    lucro_estimado = total_faturado - total_despesas

    # Exibição dos Cards Coloridos
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f'''
            <div class="dash-card bg-orange">
                <div class="card-icon-bg"><i class="bi bi-hourglass-split"></i></div>
                <small>PENDENTES (GERAL)</small>
                <h2>{formatar_moeda(total_pendente)}</h2>
            </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown(f'''
            <div class="dash-card bg-blue">
                <div class="card-icon-bg"><i class="bi bi-cash-stack"></i></div>
                <small>FATURAMENTO (MÊS)</small>
                <h2>{formatar_moeda(total_faturado)}</h2>
            </div>
        ''', unsafe_allow_html=True)

    with col3:
        st.markdown(f'''
            <div class="dash-card bg-red">
                <div class="card-icon-bg"><i class="bi bi-graph-down-arrow"></i></div>
                <small>DESPESAS (MÊS)</small>
                <h2>{formatar_moeda(total_despesas)}</h2>
            </div>
        ''', unsafe_allow_html=True)

    with col4:
        st.markdown(f'''
            <div class="dash-card bg-green">
                <div class="card-icon-bg"><i class="bi bi-piggy-bank-fill"></i></div>
                <small>LUCRO ESTIMADO</small>
                <h2>{formatar_moeda(lucro_estimado)}</h2>
            </div>
        ''', unsafe_allow_html=True)
