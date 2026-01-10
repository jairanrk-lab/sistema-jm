import sys
import os
sys.path.append(os.path.abspath(os.path.curdir))

import streamlit as st
# ... resto dos seus imports abaixo
import streamlit as st
import os

# 1. Configuração da Página
st.set_page_config(page_title="JM DETAIL PRO", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# 2. Sistema de Login (Do seu código original)
def check_password():
    if st.session_state.get("password_correct", False): return True
    try:
        if st.query_params.get("acesso_liberado") == "sim_mestre": return True
    except: pass
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### <i class='bi bi-shield-lock-fill' style='color:#D90429'></i> Acesso Restrito - JM Detail", unsafe_allow_html=True)
        with st.form("login_form"):
            pwd = st.text_input("Digite a senha de acesso:", type="password")
            submit = st.form_submit_button("ACESSAR SISTEMA")
            if submit:
                try: senha_correta = st.secrets["app"]["password"]
                except: senha_correta = "1234"
                if pwd == senha_correta: 
                    st.session_state["password_correct"] = True
                    try: st.query_params["acesso_liberado"] = "sim_mestre"
                    except: pass
                    st.rerun()
                else: st.error("Senha incorreta.")
    return False

if not check_password(): st.stop()

# 3. Importar o Visual e as Páginas
from core.styles import aplicar_estilos_customizados
from pages.dashboard import exibir_dashboard
from pages.agenda import exibir_agenda
from pages.financeiro import exibir_financeiro
from pages.despesas import exibir_despesas
from pages.historico import exibir_historico

# 4. Vestir o site
aplicar_estilos_customizados()

# 5. Cabeçalho
c_logo1, c_logo2, c_logo3 = st.columns([1,2,1])
with c_logo2:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.markdown("<h1 style='text-align:center; color:#D90429; font-weight:800'>JM DETAIL</h1>", unsafe_allow_html=True)

st.write("") 

# 6. Menu Superior
menu_opcoes = ["DASHBOARD", "AGENDA", "FINANCEIRO", "DESPESAS", "HISTÓRICO"]
menu = st.radio("Navegação", menu_opcoes, horizontal=True, label_visibility="collapsed")

st.write("---") 

# 7. Navegação
if "DASHBOARD" in menu: exibir_dashboard()
elif "AGENDA" in menu: exibir_agenda()
elif "FINANCEIRO" in menu: exibir_financeiro()
elif "DESPESAS" in menu: exibir_despesas()
elif "HISTÓRICO" in menu: exibir_historico()

# 8. Rodapé
st.markdown('<div class="footer">Desenvolvido por <b>Jairan Jesus Matos</b> | JM Detail System © 2026</div>', unsafe_allow_html=True)
