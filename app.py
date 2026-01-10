def page_financeiro():
    """Página de gestão financeira - CÁLCULOS CORRETOS"""
    st.markdown(
        '## <i class="bi bi-cash-coin" style="color: #28a745;"></i> Gestão Financeira',
        unsafe_allow_html=True
    )
    
    # Adicionar botão de limpeza
    with st.expander("🧹 Ferramentas de Limpeza (USE COM CUIDADO!)", expanded=False):
        limpar_dados_antigos()
    
    # Carregar dados
    df_v = carregar_vendas_corrigida()
    
    if df_v.empty:
        st.info("📊 Nenhuma venda registrada.")
        
        # Adicionar serviços manuais para teste
        if st.button("➕ Adicionar Serviços de Exemplo (R$ 208 + R$ 140)"):
            try:
                sheet = conectar_google_sheets()
                if sheet:
                    ws = sheet.worksheet("Vendas")
                    
                    # Cabeçalho se não existir
                    header = ws.row_values(1)
                    if not header:
                        ws.update('A1', [['Data', 'Cliente', 'Carro', 'Placa', 'Serviços', 'Total', 'Status', 'Funcionario', 'Valor Comissao', 'Fundo Caixa', 'Lucro Liquido', 'Status Comissao', 'Categoria']])
                    
                    # Adicionar os 2 serviços
                    novos_dados = [
                        ['01/02/2025', 'Cliente Exemplo 1', 'Fiat Toro', 'ABC1D23', 'Lavagem Completa', 208.00, 'Concluído', 'Equipe', 83.20, 20.80, 104.00, 'Pendente', 'SUV/Caminhonete'],
                        ['02/02/2025', 'Cliente Exemplo 2', 'Chevrolet Onix', 'DEF4G56', 'Lavagem Simples', 140.00, 'Concluído', 'Eu Mesmo', 0.00, 14.00, 126.00, 'Pago', 'Hatch/Compacto']
                    ]
                    
                    for dados in novos_dados:
                        ws.append_row(dados)
                    
                    st.success("✅ Serviços de exemplo adicionados!")
                    st.cache_data.clear()
                    t_sleep.sleep(2)
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
        
        return
    
    # Mostrar dados brutos para debug
    with st.expander("👁️ Ver todos os dados da planilha", expanded=True):
        st.dataframe(df_v, use_container_width=True)
        st.write(f"**Total de registros na planilha:** {len(df_v)}")
    
    # CÁLCULOS CORRETOS - Baseado na sua explicação
    st.write("---")
    st.markdown("### 🧮 Cálculos Financeiros")
    
    # 1. Somar todos os valores totais
    faturamento_bruto = df_v['Total'].sum()
    
    # 2. Calcular caixa (10% do total)
    caixa_empresa = faturamento_bruto * 0.10
    
    # 3. Calcular comissões (40% apenas dos serviços com equipe)
    if 'Funcionario' in df_v.columns:
        # Serviços feitos pela equipe
        servicos_equipe = df_v[df_v['Funcionario'].str.contains('Equipe|equipe', na=False)]
        comissoes_pendentes = servicos_equipe['Valor Comissao'].sum()
    else:
        comissoes_pendentes = 0
    
    # 4. Calcular lucro líquido
    lucro_liquido = faturamento_bruto - caixa_empresa - comissoes_pendentes
    
    # 5. Contar serviços
    total_servicos = len(df_v)
    servicos_com_equipe = len(df_v[df_v['Funcionario'].str.contains('Equipe|equipe', na=False)]) if 'Funcionario' in df_v.columns else 0
    servicos_sem_equipe = total_servicos - servicos_com_equipe
    
    # Exibir resultados
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Métricas Principais")
        
        metricas = [
            ("💰 Faturamento Bruto", faturamento_bruto),
            ("🏦 Caixa da Empresa (10%)", caixa_empresa),
            ("👥 Comissões da Equipe (40%)", comissoes_pendentes),
            ("📊 Lucro Líquido", lucro_liquido)
        ]
        
        for nome, valor in metricas:
            st.metric(nome, formatar_moeda(valor))
    
    with col2:
        st.markdown("#### 📊 Estatísticas")
        
        estatisticas = [
            ("📋 Total de Serviços", total_servicos),
            ("👨‍🔧 Com Equipe", servicos_com_equipe),
            ("👤 Sem Equipe", servicos_sem_equipe),
            ("📅 Mês Atual", datetime.now().strftime("%B/%Y"))
        ]
        
        for nome, valor in estatisticas:
            if isinstance(valor, (int, float)):
                st.metric(nome, valor)
            else:
                st.markdown(f"**{nome}:** {valor}")
    
    st.write("---")
    
    # TABELA DETALHADA
    st.markdown("### 📋 Detalhamento por Serviço")
    
    # Criar tabela formatada
    df_detalhes = df_v.copy()
    
    # Ordenar por data
    if 'Data_dt' in df_detalhes.columns:
        df_detalhes = df_detalhes.sort_values('Data_dt', ascending=False)
    
    # Mostrar tabela
    st.dataframe(
        df_detalhes[['Data', 'Cliente', 'Carro', 'Total', 'Funcionario', 'Valor Comissao', 'Fundo Caixa', 'Lucro Liquido', 'Status Comissao']],
        use_container_width=True,
        column_config={
            "Data": "📅 Data",
            "Cliente": "👤 Cliente", 
            "Carro": "🚗 Veículo",
            "Total": st.column_config.NumberColumn("💰 Total", format="R$ %.2f"),
            "Funcionario": "👷 Executor",
            "Valor Comissao": st.column_config.NumberColumn("💸 Comissão", format="R$ %.2f"),
            "Fundo Caixa": st.column_config.NumberColumn("🏦 Caixa", format="R$ %.2f"),
            "Lucro Liquido": st.column_config.NumberColumn("📈 Lucro", format="R$ %.2f"),
            "Status Comissao": "📌 Status"
        }
    )
    
    st.write("---")
    
    # VERIFICAÇÃO DOS CÁLCULOS
    st.markdown("### 🔍 Verificação dos Cálculos")
    
    # Fórmula explicada
    st.markdown("""
    #### 📝 Como são calculados os valores:
    
    **Para cada serviço:**
    ```
    1. Faturamento Bruto = Valor Total do Serviço
    2. Caixa da Empresa = 10% do Valor Total
    3. Comissão da Equipe = 40% do Valor Total (apenas se "Funcionario" = "Equipe")
    4. Lucro Líquido = Total - Caixa - Comissão
    ```
    
    **Exemplo com R$ 208,00 (com equipe):**
    ```
    Total: R$ 208,00
    Caixa (10%): R$ 20,80
    Comissão (40%): R$ 83,20
    Lucro: R$ 104,00
    ```
    
    **Exemplo com R$ 140,00 (sem equipe):**
    ```
    Total: R$ 140,00
    Caixa (10%): R$ 14,00
    Comissão (40%): R$ 0,00
    Lucro: R$ 126,00
    ```
    """)
    
    # Botão para corrigir valores automaticamente
    if st.button("🔄 Corrigir Valores Automaticamente", type="secondary", use_container_width=True):
        try:
            sheet = conectar_google_sheets()
            if sheet:
                ws = sheet.worksheet("Vendas")
                dados = ws.get_all_records()
                
                for i, linha in enumerate(dados, start=2):  # Começa na linha 2
                    total = float(linha.get('Total', 0))
                    
                    # Calcular valores corretos
                    fundo_caixa = total * 0.10
                    
                    # Verificar se é serviço com equipe
                    funcionario = str(linha.get('Funcionario', '')).lower()
                    if 'equipe' in funcionario:
                        valor_comissao = total * 0.40
                    else:
                        valor_comissao = 0
                    
                    lucro_liquido = total - fundo_caixa - valor_comissao
                    
                    # Atualizar células
                    ws.update_cell(i, 9, valor_comissao)   # Coluna I = Valor Comissao
                    ws.update_cell(i, 10, fundo_caixa)     # Coluna J = Fundo Caixa
                    ws.update_cell(i, 11, lucro_liquido)   # Coluna K = Lucro Liquido
                
                st.success("✅ Valores recalculados com sucesso!")
                st.cache_data.clear()
                t_sleep.sleep(2)
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
