def page_vistoria():
    st.markdown('## <i class="bi bi-camera-fill" style="color: #39FF14;"></i> Vistoria de Entrada (Cautelar)', unsafe_allow_html=True)
    
    # --- CSS: MELHORIA VISUAL DOS BOTÕES E TEXTOS ---
    st.markdown("""
    <style>
        /* Área de Upload */
        [data-testid="stFileUploader"] {
            padding: 15px; border: 1px dashed rgba(57, 255, 20, 0.3); border-radius: 12px; text-align: center;
            background-color: rgba(20, 20, 20, 0.6);
        }
        /* Texto de ajuda do uploader */
        [data-testid="stFileUploader"] small { display: none; }
        
        /* Estilo das Etiquetas de Título das Fotos */
        .foto-label {
            font-size: 14px;
            font-weight: 700;
            color: #39FF14; /* Verde Neon */
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
            display: flex; 
            align-items: center;
            gap: 5px;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        c_placa, c_buscar = st.columns([3, 1]); placa_input = c_placa.text_input("Buscar Placa ou Digitar Nova", key="placa_vistoria")
        v_cli, v_veic, v_comb = "", "", 50
        if placa_input:
            dados = buscar_cliente_por_placa(placa_input)
            if dados:
                st.success(f"Cliente Encontrado: {dados['Cliente']}")
                v_cli, v_veic = dados['Cliente'], dados['Veiculo']
        
        c1, c2 = st.columns(2)
        cli = c1.text_input("Nome do Cliente", value=v_cli)
        veic = c2.text_input("Modelo do Veículo", value=v_veic)
        
        st.write("---")
        st.markdown("### 1. Estado Geral & Avarias")
        combustivel = st.slider("Nível de Combustível (%)", 0, 100, 50, step=5)
        
        # LISTA COMPLETA DE AVARIAS
        lista_avarias = [
            "Capô: Risco/Arranhão", "Capô: Amassado", "Capô: Pintura Queimada",
            "Teto: Pintura Queimada", "Teto: Amassado (Granizo/Outros)",
            "Para-brisa: Trincado/Estrela", "Vidros Laterais: Risco/Mancha",
            "Para-choque Diant: Ralado/Quebrado", "Para-choque Tras: Ralado/Quebrado",
            "Lateral Esq (Motorista): Risco", "Lateral Esq (Motorista): Amassado",
            "Lateral Dir (Passageiro): Risco", "Lateral Dir (Passageiro): Amassado",
            "Retrovisor Esq: Quebrado/Ralado", "Retrovisor Dir: Quebrado/Ralado",
            "Faróis: Quebrados/Trincados", "Faróis: Amarelados/Foscos",
            "Rodas/Calotas: Raladas (Meio-fio)", "Pneus: Carecas/Murchos",
            "Interior: Banco Rasgado/Furado", "Interior: Teto Sujo/Descolando",
            "Interior: Painel Riscado/Quebrado", "Manchas de Chuva Ácida (Geral)"
        ]
        
        avarias = st.multiselect(
            "Marcar Avarias Visíveis:", 
            options=lista_avarias,
            placeholder="Selecione as avarias na lista..."
        )
        
        pertences = st.text_area("Pertences no Veículo (Opcional)", placeholder="Ex: Óculos, Pen Drive, Cadeirinha de bebê...")
        
        st.write("---")
        st.markdown("### 2. Registro Fotográfico (Câmera Traseira/Galeria)")
        st.info("💡 Dica: Clique em 'Browse files' e escolha **'Câmera'** ou **'Arquivos'**.")
        
        # Grid de 6 Uploaders COM VISUAL DESTACADO
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="foto-label"><i class="bi bi-car-front"></i> 1. FRENTE / CAPÔ</div>', unsafe_allow_html=True)
            img_frente = st.file_uploader("label_oculto_1", type=["jpg", "png", "jpeg"], key="up_frente", label_visibility="collapsed")
        
        with col_b:
            st.markdown('<div class="foto-label"><i class="bi bi-car-front-fill"></i> 2. TRASEIRA / MALA</div>', unsafe_allow_html=True)
            img_tras = st.file_uploader("label_oculto_2", type=["jpg", "png", "jpeg"], key="up_tras", label_visibility="collapsed")
        
        st.write("") # Espaço
        
        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown('<div class="foto-label"><i class="bi bi-arrow-left-circle"></i> 3. LATERAL ESQ.</div>', unsafe_allow_html=True)
            img_lat_e = st.file_uploader("label_oculto_3", type=["jpg", "png", "jpeg"], key="up_lat_e", label_visibility="collapsed")
        
        with col_d:
            st.markdown('<div class="foto-label"><i class="bi bi-arrow-right-circle"></i> 4. LATERAL DIR.</div>', unsafe_allow_html=True)
            img_lat_d = st.file_uploader("label_oculto_4", type=["jpg", "png", "jpeg"], key="up_lat_d", label_visibility="collapsed")
        
        st.write("") # Espaço
        
        col_e, col_f = st.columns(2)
        with col_e:
            st.markdown('<div class="foto-label"><i class="bi bi-zoom-in"></i> 5. DETALHE 1</div>', unsafe_allow_html=True)
            img_det1 = st.file_uploader("label_oculto_5", type=["jpg", "png", "jpeg"], key="up_det1", label_visibility="collapsed")
        
        with col_f:
            st.markdown('<div class="foto-label"><i class="bi bi-zoom-in"></i> 6. DETALHE 2</div>', unsafe_allow_html=True)
            img_det2 = st.file_uploader("label_oculto_6", type=["jpg", "png", "jpeg"], key="up_det2", label_visibility="collapsed")
        
        st.write("---")
        if st.button("📄 GERAR TERMO DE VISTORIA (PDF)", use_container_width=True):
            if not cli or not veic:
                st.error("Preencha o Nome e Veículo!")
            else:
                fotos = {
                    "Frente/Capô": img_frente, "Traseira": img_tras, 
                    "Lat. Esquerda": img_lat_e, "Lat. Direita": img_lat_d,
                    "Detalhe 1": img_det1, "Detalhe 2": img_det2
                }
                
                # Salvar temporariamente
                temp_paths = {}
                try:
                    for nome, buffer in fotos.items():
                        if buffer:
                            path = f"temp_{nome}.jpg"
                            with open(path, "wb") as f: f.write(buffer.getbuffer())
                            temp_paths[nome] = path
                    
                    dados_pdf = {
                        "Cliente": cli, "Veiculo": veic, "Placa": placa_input, 
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Combustivel": combustivel, "Avarias": avarias, "Pertences": pertences
                    }
                    
                    pdf_bytes = gerar_pdf_vistoria(dados_pdf, temp_paths)
                    st.download_button("📥 BAIXAR PDF ASSINADO", pdf_bytes, f"Vistoria_{cli}.pdf", "application/pdf", use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Erro ao gerar: {e}")
                finally:
                    # Limpeza
                    for p in temp_paths.values():
                        if os.path.exists(p): os.remove(p)
