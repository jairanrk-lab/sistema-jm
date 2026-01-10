import streamlit as st
from datetime import datetime
from core.database import carregar_dados, salvar_no_google
from utils.helpers import obter_icone_html, formatar_moeda

def exibir_agenda():
    st.title("📅 Agenda de Serviços")
    
    # --- FORMULÁRIO DE NOVO AGENDAMENTO ---
    with st.expander("➕ Novo Agendamento", expanded=False):
        with st.form("form_agendamento", clear_on_submit=True):
            data = st.date_input("Data", datetime.now())
            cliente = st.text_input("Nome do Cliente")
            veiculo = st.text_input("Veículo (Modelo/Cor)")
            # PLACA: Se ficar vazio, o sistema preenche com "S/P" (Sem Placa)
            placa = st.text_input("Placa (Opcional)")
            
            servico = st.multiselect("Serviços", ["Lavagem Simples", "Lavagem Técnica", "Polimento", "Higienização", "Cera"])
            valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
            
            if st.form_submit_button("Agendar"):
                if cliente and veiculo:
                    nova_linha = {
                        "Data": data.strftime("%d/%m/%Y"),
                        "Cliente": cliente,
                        "Veículo": veiculo,
                        "Placa": placa if placa else "S/P", # RESOLVIDO: Se vazio, vira S/P
                        "Serviço": ", ".join(servico),
                        "Preço": valor,
                        "Status": "Pendente"
                    }
                    sucesso, msg = salvar_no_google("Agendamentos", nova_linha)
                    if sucesso: st.success("Agendado com sucesso!")
                    else: st.error(f"Erro: {msg}")
                else:
                    st.warning("Preencha Nome e Veículo!")

    # --- LISTA DE AGENDAMENTOS ---
    df = carregar_dados("Agendamentos")
    if not df.empty:
        for i, row in df.iterrows():
            icone = obter_icone_html(row['Veículo'])
            st.markdown(f'''
                <div class="agenda-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span>{icone} <b>{row['Veículo']}</b> - {row['Placa']}</span>
                        <span style="color: #00B4DB;">{row['Data']}</span>
                    </div>
                    <div style="margin-top: 10px;">
                        <small>Cliente:</small> {row['Cliente']}<br>
                        <small>Serviço:</small> {row['Serviço']}
                    </div>
                    <div style="text-align: right; font-weight: bold; color: #38ef7d;">
                        {formatar_moeda(row['Preço'])}
                    </div>
                </div>
            ''', unsafe_allow_html=True)
