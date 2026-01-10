import streamlit as st
from core.database import carregar_dados
from utils.helpers import formatar_moeda, obter_icone_html

def exibir_historico():
    st.markdown('## <i class="bi bi-clock-history" style="color: #FFC107;"></i> Garagem & Histórico', unsafe_allow_html=True)
    df = carregar_dados("Vendas")
    if df.empty: st.info("Nenhum serviço registrado ainda."); return

    busca = st.text_input("🔍 Buscar Cliente ou Carro...", placeholder="Ex: Fiat Toro ou João").strip().lower()
    df_f = df.iloc[::-1]
    
    if busca: df_f = df_f[df_f.apply(lambda r: busca in str(r).lower(), axis=1)]

    for index, r in df_f.iterrows():
        html_card = f"""
        <div class="history-card" style="border-left: 5px solid #28a745">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h3 style="margin: 0; font-size: 20px; color: white; font-weight: 700;">{obter_icone_html(r.get("Categoria", ""))} {r["Carro"]}</h3>
                    <p style="margin: 5px 0 0 0; color: #bbb; font-size: 14px;"><i class="bi bi-person"></i> {r["Cliente"]} &nbsp;|&nbsp; {r["Placa"]}</p>
                </div>
                <div style="text-align: right;">
                    <h2 style="margin: 0; color: #39FF14; font-weight: 700; font-size: 22px;">{formatar_moeda(float(r["Total"]))}</h2>
                    <span style="background-color: #222; padding: 4px 8px; border-radius: 6px; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #aaa;">{r["Data"]}</span>
                </div>
            </div>
            <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid #333; color: #888; font-size: 13px;"><i class="bi bi-tools"></i> {r["Serviços"]}</div>
        </div>
        """
        st.markdown(html_card, unsafe_allow_html=True)
