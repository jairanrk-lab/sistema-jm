import sys
import os
import streamlit as st

# 1. Configuração de Pastas (Obrigatório para não dar erro de Import)
sys.path.append(os.path.abspath(os.path.curdir))

# 2. Configuração da Página
st.set_page_config(
    page_title="JM DETAIL PRO",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. Importação Segura dos Estilos
try:
    from core.styles import aplicar_estilos_customizados
    aplicar_estilos_customizados()
except Exception:
    pass # Se der erro no estilo, o site abre sem estilo mesmo

# 4. SISTEMA DE LOGIN (Puxando dos Secrets)
def check_password():
    """Retorna True se o usuário acertar a senha dos Secrets."""
    
    # Se já acertou antes, libera direto
    if st.session_state.get("password_correct", False):
        return True

    st.markdown("<h1 style='text-align: center;'>🔐 Acesso Restrito - JM Detail</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha_digitada = st.text_input("Digite a senha de acesso", type="password")
        
        if st.button("Entrar", use_container_width=True):
            # AQUI ESTÁ O SEGREDO: Ele busca a senha "password" configurada no site
            if senha_digitada == st.secrets["password"]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("🚫 Senha incorreta")
                
    return False

# 5. EXECUÇÃO DO APP
if not check_password():
    st.stop()  # Para tudo aqui se a senha estiver errada

# --- SEU SITE COMEÇA AQUI ---
st.success(f"Bem-vindo, Mestre Jairan! O sistema está online.")

# Aqui você vai colocar o dashboard depois
# from pages.dashboard import show_dashboard
# show_dashboard()
