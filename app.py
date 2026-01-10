import sys
import os
import streamlit as st

# --- 1. CONFIGURAÇÃO INICIAL (Obrigatório vir no topo) ---
# Adiciona o diretório atual ao sistema para encontrar suas pastas
sys.path.append(os.path.abspath(os.path.curdir))

st.set_page_config(
    page_title="JM DETAIL PRO",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. IMPORTAÇÃO DOS ESTILOS (Com proteção contra erro) ---
try:
    from core.styles import aplicar_estilos_customizados
    aplicar_estilos_customizados()
except Exception as e:
    # Se der erro no estilo, o app avisa mas NÃO trava
    st.warning(f"⚠️ Aviso: O arquivo de estilos (styles.py) tem um erro e não foi carregado. Detalhe: {e}")

# --- 3. SISTEMA DE LOGIN ---
def check_password():
    """Retorna `True` se o usuário tiver a senha correta."""
    if st.session_state.get("password_correct", False):
        return True

    # Verifica parâmetros da URL (opcional)
    try:
        if st.query_params.get("acesso_liberado") == "sim_mestre":
            return True
    except:
        pass

    # Formulário de Login
    st.markdown("<h1 style='text-align: center;'>🔐 Acesso Restrito - JM Detail</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha_digitada = st.text_input("Digite a senha de acesso", type="password")
        
        if st.button("Entrar", use_container_width=True):
            # SENHA MESTRA AQUI (Mude se quiser)
            if senha_digitada == "admin123":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("🚫 Senha incorreta")
                
    return False

# --- 4. EXECUÇÃO PRINCIPAL ---
if not check_password():
    st.stop()  # Para o código aqui se não estiver logado

# Se passou do login, mostra o resto do app
st.success("Login realizado com sucesso! Carregando dashboard...")

# Aqui viria a importação das páginas (Dashboard, Clientes, etc)
# from pages.dashboard import show_dashboard
# show_dashboard()
