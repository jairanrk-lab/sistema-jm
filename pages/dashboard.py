import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
from datetime import datetime, date
from core.database import carregar_dados
from utils.helpers import formatar_moeda, obter_icone_html

def exibir_dashboard():
    hoje = datetime.now()
    mes_atual, ano_atual = hoje.month, hoje.year
    nome_meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    st.markdown(f'## <i class="bi bi-speedometer2" style="color: #00B4DB;"></i> Painel Geral <small style="font-size:14px; color:#888">| {nome_meses[mes_atual]}/{ano_atual}</small>', unsafe_allow_html=True)
    
    df_v = carregar_dados("Vendas")
    df_d = carregar_dados("Despesas")
    df_a = carregar_dados("Agendamentos")
    
    receita_mes, despesa_mes, pendente_total, count_p = 0.0, 0.0, 0.0, 0
    
    if not df_v.empty:
        for c in ["Total", "Lucro Liquido"]:
            df_v[c] = pd.to_numeric(df_v[c].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0)
        df_v['Data_dt'] = pd.to_datetime(df_v['Data'], format='%d/%m/%Y', errors='coerce')
        df_mes = df_v[(df_v['Data_dt'].dt.month == mes_atual) & (df_v['Data_dt'].dt.year == ano_atual)]
        receita_mes = df_mes[df_mes["Status"]=="Concluído"]["Total"].sum()
        pendente_total = df_v[df_v["Status"]=="Orçamento/Pendente"]["Total"].sum()
        count_p = len(df_v[df_v["Status"]=="Orçamento/Pendente"])

    if not df_d.empty:
        df_d['Data_dt'] = pd.to_datetime(df_d['Data'], format='%d/%m/%Y', errors='coerce')
        df_d_mes = df_d[(df_d['Data_dt'].dt.month == mes_atual) & (df_d['Data_dt'].dt.year == ano_atual)]
        despesa_mes = pd.to_numeric(df_d_mes["Valor"].astype(str).str.replace('R$', '').str.replace(',', '.'), errors='coerce').fillna(0).sum()
    
    lucro_final = receita_mes - despesa_mes
    
    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="dash-card bg-orange"><i class="bi bi-hourglass-split card-icon-bg"></i><h4>PENDENTES (GERAL)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(pendente_total)}</div><small>{count_p} carros na fila</small></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="dash-card bg-blue"><i class="bi bi-currency-dollar card-icon-bg"></i><h4>FATURAMENTO (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(receita_mes)}</div><small>Ref: {nome_meses[mes_atual]}</small></div>', unsafe_allow_html=True)
    
    c3, c4 = st.columns(2)
    with c3: st.markdown(f'<div class="dash-card bg-red"><i class="bi bi-graph-down-arrow card-icon-bg"></i><h4>DESPESAS (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(despesa_mes)}</div><small>Gastos externos</small></div>', unsafe_allow_html=True)
    cor_lucro = "bg-green" if lucro_final >= 0 else "bg-red"
    with c4: st.markdown(f'<div class="dash-card {cor_lucro}"><i class="bi bi-wallet2 card-icon-bg"></i><h4>LUCRO LÍQUIDO (MÊS)</h4><div style="font-size:24px;font-weight:bold">{formatar_moeda(lucro_final)}</div><small>Após comissões/insumos</small></div>', unsafe_allow_html=True)

    st.write("---")
    
    col_graf, col_prox = st.columns([2, 1])
    
    with col_graf:
        st.markdown('### <i class="bi bi-graph-up-arrow" style="color: #39FF14;"></i> Performance Mensal', unsafe_allow_html=True)
        if not df_v.empty and 'df_mes' in locals() and not df_mes.empty:
            base = alt.Chart(df_mes).encode(x=alt.X('Data', title=None, axis=alt.Axis(labelColor='white')))
            bars = base.mark_bar(size=30, cornerRadiusEnd=5).encode(
                y=alt.Y('Total', axis=None),
                color=alt.Color('Status', scale=alt.Scale(domain=['Concluído', 'Orçamento/Pendente'], range=['#00F260', '#FF0080']), legend=None),
                tooltip=['Data', 'Cliente', 'Carro', 'Total', 'Lucro Liquido']
            )
            line = base.mark_line(color='#0575E6', strokeWidth=3).encode(y=alt.Y('Lucro Liquido', axis=None))
            chart = alt.layer(bars, line).properties(height=300, background='transparent').configure_view(strokeWidth=0).configure_axis(grid=False, domain=False, ticks=False)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Sem dados de vendas neste mês.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('##### <i class="bi bi-bullseye" style="color:#D90429"></i> Meta Mensal', unsafe_allow_html=True)
        fig = go.Figure(go.Indicator(mode = "gauge+number", value = receita_mes, domain = {'x': [0, 1], 'y': [0, 1]}, gauge = {'axis': {'range': [None, 6000], 'tickwidth': 1, 'tickcolor': "white"}, 'bar': {'color': "#D90429"}, 'bgcolor': "black", 'borderwidth': 2, 'bordercolor': "#333", 'steps': [{'range': [0, 1500], 'color': '#222'}, {'range': [1500, 3500], 'color': '#333'}], 'threshold': {'line': {'color': "#00B4DB", 'width': 4}, 'thickness': 0.75, 'value': 5000}}))
        fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "white", 'family': "Poppins"}, height=150, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col_prox:
        st.markdown('### <i class="bi bi-calendar-week"></i> Próximos na Agenda', unsafe_allow_html=True)
        if not df_a.empty:
            df_a['Data_dt'] = pd.to_datetime(df_a['Data'], format='%d/%m/%Y', errors='coerce')
            hoje_dt = pd.to_datetime(date.today())
            df_futuro = df_a[df_a['Data_dt'] >= hoje_dt].sort_values(by='Data_dt').head(4)
            if not df_futuro.empty:
                for _, r in df_futuro.iterrows():
                    st.markdown(f"""
                    <div style="background-color:#161616; padding:15px; border-radius:12px; margin-bottom:10px; border-left:4px solid #D90429;">
                        <div style="font-size:12px; color:#aaa; margin-bottom:5px"><i class="bi bi-calendar"></i> {r['Data']} • {r['Hora']}</div>
                        <div style="font-weight:bold; font-size:16px; color:white">{obter_icone_html(r.get("Categoria", ""))} {r['Veiculo']}</div>
                        <div style="font-size:13px; color:#888;">{r['Cliente']}</div>
                    </div>""", unsafe_allow_html=True)
            else: st.info("Agenda livre.")
        else: st.info("Agenda vazia.")
