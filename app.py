def page_historico():
    st.markdown('## <i class="bi bi-clock-history"></i> Histórico & CRM', unsafe_allow_html=True)
    try:
        df = carregar_dados("Vendas")
        
        if not df.empty:
            # 1. PROCESSAMENTO DE DADOS
            df["Total_Num"] = df["Total"].apply(converter_valor)
            df['Data_dt'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
            
            # FASE 1: CRM COM 3 MENSAGENS PERSONALIZADAS
            st.markdown("### 🧠 Gestão de Retorno (CRM)")
            with st.expander("Ver Clientes para Recontato", expanded=False):
                hoje = pd.to_datetime(date.today())
                
                # Filtra apenas datas válidas
                df_valid = df.dropna(subset=['Data_dt'])
                if not df_valid.empty:
                    df_crm = df_valid.groupby("Cliente").agg({'Data_dt': 'max', 'Telefone': 'first', 'Carro': 'first'}).reset_index()
                    df_crm["Dias sem vir"] = (hoje - df_crm["Data_dt"]).dt.days
                    
                    # Classificação Visual
                    def classificar_status(dias):
                        if dias <= 30: return "🟢 Recente"
                        elif dias <= 90: return "🟡 Atenção"
                        else: return "🔴 Inativo"
                    
                    df_crm["Status"] = df_crm["Dias sem vir"].apply(classificar_status)
                    
                    # Criação do Link de WhatsApp
                    def criar_link_zap(row):
                        tel = limpar_numero(row["Telefone"])
                        if not tel: return None
                        nome = row["Cliente"].split()[0]
                        carro = row["Carro"]
                        
                        # Lógica das Mensagens (Ajustada para o tom aprovado)
                        if row["Dias sem vir"] <= 30: # RECENTE
                            msg = f"Olá {nome}, tudo bem? Passando apenas para saber como está a conservação do {carro} após o nosso serviço. Se precisar de algum suporte, estou à disposição!"
                        elif row["Dias sem vir"] <= 90: # ATENÇÃO
                            msg = f"Fala {nome}, tudo na paz? Passando para desejar uma ótima semana! Se precisar dar aquele talento no {carro} nesses dias, é só dar um alô."
                        else: # INATIVO
                            msg = f"Olá {nome}. Faz um tempinho que cuidamos do {carro}, espero que esteja tudo certo. Quando sentir que é hora de renovar a proteção ou a limpeza, conte comigo."
                            
                        link = f"https://wa.me/55{tel}?text={urllib.parse.quote(msg)}"
                        return link

                    df_crm["LinkZap"] = df_crm.apply(criar_link_zap, axis=1)
                    
                    # Ordenar e mostrar
                    df_crm = df_crm.sort_values(by="Dias sem vir", ascending=True)
                    
                    st.dataframe(
                        df_crm[["Cliente", "Status", "Dias sem vir", "Carro", "LinkZap"]],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Dias sem vir": st.column_config.NumberColumn("Ausência", format="%d dias"),
                            "Status": st.column_config.TextColumn("Status", help="Estado atual do cliente"),
                            "LinkZap": st.column_config.LinkColumn(
                                "Contato",  # Cabeçalho da coluna mais curto
                                display_text="💬 WhatsApp", # <--- AQUI MUDOU (Visual Clean)
                                help="Clique para abrir a conversa"
                            )
                        }
                    )
                else:
                    st.info("Sem dados de datas válidos para CRM.")

            st.write("---")

            # 3. RANKING E HISTÓRICO GERAL
            ranking = df.groupby("Cliente")["Total_Num"].sum().reset_index().sort_values(by="Total_Num", ascending=False).head(5)
            st.markdown("### 🏆 Ranking VIP (Top 5)")
            col_rank = st.columns(len(ranking))
            for idx, (i, r) in enumerate(ranking.iterrows()):
                medalha, cor = ("🥇" if idx==0 else "🥈" if idx==1 else "🥉" if idx==2 else f"{idx+1}º"), ("bg-gold" if idx==0 else "")
                st.markdown(f'<div class="dash-card {cor}" style="height:100px; padding:10px; margin-bottom:10px"><div style="font-size:20px">{medalha}</div><div style="font-weight:bold; font-size:14px">{r["Cliente"]}</div><div style="font-size:12px">{formatar_moeda(r["Total_Num"])}</div></div>', unsafe_allow_html=True)
            
            st.write("---")
            busca = st.text_input("🔍 Buscar no Histórico...").strip().lower()
            df_f = df.iloc[::-1] # Inverte ordem
            if busca: df_f = df_f[df_f.apply(lambda r: busca in str(r).lower(), axis=1)]
            
            for _, r in df_f.iterrows():
                total_hist = formatar_moeda(converter_valor(r["Total"]))
                st.markdown(f'<div class="history-card" style="border-left:5px solid #28a745"><div style="display:flex;justify-content:space-between;"><div><b>{r["Carro"]}</b><br>{r["Cliente"]} | {r["Placa"]}</div><div style="text-align:right"><b style="color:#39FF14">{total_hist}</b><br><small>{r["Data"]}</small></div></div><div style="color:#888">{r.get("Serviços", "")}</div></div>', unsafe_allow_html=True)
        else: st.info("Histórico Vazio.")
    except Exception as e:
        st.error(f"Erro no Histórico: {e}")
