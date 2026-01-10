import streamlit as st
import pandas as pd
import time as t_sleep
from core.database import carregar_dados, conectar_google_sheets
from utils.helpers import formatar_moeda

def exibir_financeiro():
    st.markdown('## <i class="bi bi-cash-coin" style="color: #28a745;"></i> Gestão Financeira', unsafe_allow_html=True)
    df_v = carregar_dados("Vendas")
    comissao_pendente = 0.0; fundo_caixa = 0.0
    if not df_v.empty:
        if "Status Comissao" not in df_v.columns: df_v["Status Comissao"] = "Pendente"
        for c in ["Valor Comissao", "Fundo Caixa"]:
            if c in df_v.columns: df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0)
        comissao_pendente = df_v[df_v["Status Comissao"] != "Pago"]["Valor Comissao"].sum()
        fundo_caixa = df_v["Fundo Caixa"].sum()
    
    st.info(f"Caixa da Empresa (Acumulado): {formatar_moeda(fundo_caixa)}")
    
    col1, col2 = st.columns([2,1])
    with col1: st.metric("Comissões Pendentes", formatar_moeda(comissao_pendente))
    with col2:
        if comissao_pendente > 0:
            if st.button("Pagar Comissões"):
                sheet = conectar_google_sheets(); ws = sheet.worksheet("Vendas"); dados = ws.get_all_records()
                header = ws.row_values(1); col_idx = header.index("Status Comissao") + 1
                for i, linha in enumerate(dados):
                    v = pd.to_numeric(str(linha.get("Valor Comissao", "0")).replace('R$', '').replace(',', '.'), errors='coerce')
                    if v > 0 and str(linha.get("Status Comissao", "")) != "Pago": ws.update_cell(i + 2, col_idx, "Pago")
                st.success("Pago!"); t_sleep.sleep(1); st.rerun()
