import streamlit as st
import pandas as pd
from datetime import date, time
import time as t_sleep
from core.database import carregar_dados, salvar_no_google, excluir_agendamento
from utils.helpers import formatar_moeda, obter_icone_html, carregar_catalogo

def exibir_agenda():
    st.markdown('## <i class="bi bi-calendar-check" style="color: white;"></i> Agenda Integrada', unsafe_allow_html=True)
    tab_new, tab_list = st.tabs(["NOVO AGENDAMENTO", "LISTA DE SERVIÇOS"]) 
    df_cat = carregar_catalogo()
    
    with tab_new:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            cli = c1.text_input("Nome do Cliente")
            veic = c1.text_input("Modelo do Veículo")
            placa = c2.text_input("Placa")
            dt = c2.date_input("Data", value=date.today(), format="DD/MM/YYYY")
            hr = c2.time_input("Horário", value=time(8, 0)).strftime("%H:%M")
            
            cat = st.selectbox("Categoria do Veículo:", df_cat["Categoria"])
            servs_disp = [c for c in df_cat.columns if c != "Categoria"]
            escolhidos = st.multiselect("Selecione os Serviços:", servs_disp)
            
            st.divider()
            ce1, ce2, ce3 = st.columns(3)
            extra_v = ce1.number_input("Valor Extra (R$)", min_value=0.0)
            desconto_v = ce2.number_input("Desconto (R$)", min_value=0.0)
            quem = ce3.radio("Executor:", ["Eu Mesmo", "Equipe"], horizontal=True)
            
            if escolhidos:
                precos = {s: df_cat[df_cat["Categoria"] == cat][s].values[0] for s in escolhidos}
                total = sum(precos.values()) + extra_v - desconto_v
                st.markdown(f"<h3 style='text-align:right; color:#39FF14'>Total: {formatar_moeda(total)}</h3>", unsafe_allow_html=True)
                
                if st.button("CONFIRMAR AGENDAMENTO", use_container_width=True):
                    serv_str = ", ".join(escolhidos)
                    lucro = total - (total * 0.10) - (total * 0.40 if "Equipe" in quem else 0)
                    dados = {"Data": dt.strftime("%d/%m/%Y"), "Hora": hr, "Cliente": cli, "Veiculo": veic, "Placa": placa, "Servicos": serv_str, "Total": total, "Executor": quem, "LucroPrevisto": lucro, "Categoria": cat}
                    ok, msg = salvar_no_google("Agendamentos", dados)
                    if ok: st.success("Agendado!"); t_sleep.sleep(1); st.rerun()
                    else: st.error(msg)

    with tab_list:
        df_a = carregar_dados("Agendamentos")
        if df_a.empty: st.info("Agenda vazia.")
        else:
            for i, r in df_a.iterrows():
                st.markdown(f"""
                <div class="agenda-card">
                    <div style="display:flex; justify-content:space-between; align-items:center">
                        <div style="font-weight:bold; color:#00B4DB; font-size:16px"><i class="bi bi-clock"></i> {r['Data']} às {r['Hora']}</div>
                        <div style="font-weight:800; font-size:18px; color:#39FF14">{formatar_moeda(float(r['Total']))}</div>
                    </div>
                    <div style="margin-top:10px; font-size:18px; font-weight:700; color:white">
                        {obter_icone_html(r.get("Categoria", ""))} {r['Veiculo']} <span style="font-size:14px; color:#888">({r['Placa']})</span>
                    </div>
                    <div style="margin-top:5px; font-size:14px; color:#ccc"><i class="bi bi-person-fill"></i> {r['Cliente']}</div>
                    <div style="margin-top:10px; padding-top:10px; border-top:1px solid #333; font-size:13px; color:#888">🔧 {r['Servicos']}</div>
                </div>""", unsafe_allow_html=True)
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button(f"✅ Concluir Serviço", key=f"ok_{i}", use_container_width=True):
                        fundo = float(r["Total"]) * 0.10
                        comis = float(r["Total"]) * 0.40 if "Equipe" in r["Executor"] else 0.0
                        lucro = float(r["Total"]) - fundo - comis
                        venda = {"Data": r["Data"], "Cliente": r["Cliente"], "Carro": r["Veiculo"], "Placa": r["Placa"], "Serviços": r["Servicos"], "Total": r["Total"], "Status": "Concluído", "Funcionario": r["Executor"], "Valor Comissao": comis, "Fundo Caixa": fundo, "Lucro Liquido": lucro, "Status Comissao": "Pendente", "Categoria": r.get("Categoria", "")}
                        salvar_no_google("Vendas", venda)
                        excluir_agendamento(i)
                        st.rerun()
                with c_btn2:
                    if st.button(f"🗑️ Cancelar", key=f"del_{i}", use_container_width=True):
                        excluir_agendamento(i)
                        st.warning("Agendamento excluído.")
                        t_sleep.sleep(1); st.rerun()
