import streamlit as st

# 1. Importando nossas fatias (O que criamos nos passos anteriores)
from core.styles import aplicar_estilos_customizados
from pages.dashboard import exibir_dashboard
from pages.agenda import exibir_agenda
from pages.financeiro import exibir_financeiro
from pages.despesas import exibir_despesas
from pages.historico import exibir_historico

# Configuração da Página (Deve ser a primeira coisa)
st.set_page_config(page_title="JM DETAIL PRO", layout="wide", initial_sidebar_state="collapsed")

# 2. Aplicando o Visual
aplicar_estilos_customizados()

# 3. Cabeçalho com Logo
st.markdown(f'''
    <div style="text-align: center; padding: 20px;">
        <img src="https://raw.githubusercontent.com/{st.secrets.get("github_user", "jairanrk-lab")}/sistema-jm/main/logo.png" width="250">
    </div>
''', unsafe_allow_html=True)

# 4. Menu de Navegação Superior
menu = st.radio(
    "Navegação",
    ["📊 DASHBOARD", "📅 AGENDA", "💰 FINANCEIRO", "💸 DESPESAS", "📜 HISTÓRICO"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# 5. Lógica de Troca de Páginas
if "DASHBOARD" in menu:
    exibir_dashboard()
elif "AGENDA" in menu:
    exibir_agenda()
elif "FINANCEIRO" in menu:
    exibir_financeiro()
elif "DESPESAS" in menu:
    exibir_despesas()
elif "HISTÓRICO" in menu:
    exibir_historico()

# 6. Rodapé Fixo
st.markdown('''
    <div class="footer">
        Desenvolvido por Jairan Jesus Matos | JM Detail System © 2026
    </div>
''', unsafe_allow_html=True)
