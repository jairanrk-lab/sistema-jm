import streamlit as st
import gspread
import os
import pandas as pd

def conectar_google_sheets():
    """Faz a conexão segura com a sua planilha do Google."""
    try: 
        # Tenta pegar o ID da planilha nos segredos do Streamlit
        ID = st.secrets["app"]["spreadsheet_id"]
    except: 
        # ID reserva caso o de cima falhe
        ID = "1-8Xie9cOvQ26WRHJ_ltUr1kfqbIvHLr0qP21h6mqZjg"
    
    try:
        # Verifica se você está usando o arquivo de chave local ou os Secrets da nuvem
        if os.path.exists("chave_google.json"): 
            client = gspread.service_account(filename="chave_google.json")
        else: 
            client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        return client.open_by_key(ID)
    except Exception as e: 
        return None

def carregar_dados(aba):
    """Busca as informações de uma aba específica (ex: 'Agendamentos')."""
    sheet = conectar_google_sheets()
    if sheet is None: return pd.DataFrame()
    try: 
        return pd.DataFrame(sheet.worksheet(aba).get_all_records())
    except: 
        return pd.DataFrame()

def salvar_no_google(aba, linha_dados):
    """Salva uma nova linha na planilha de forma organizada."""
    sheet = conectar_google_sheets()
    if sheet is None: return False, "Falha na conexão."
    try:
        ws = sheet.worksheet(aba)
        headers = ws.row_values(1) # Lê os títulos da primeira linha
        
        if not headers: 
            headers = list(linha_dados.keys())
            ws.append_row(headers)
        
        # Cria uma linha vazia do tamanho certo e preenche cada coluna
        nova_linha = [''] * len(headers)
        for col_name, valor in linha_dados.items():
            if col_name in headers:
                index = headers.index(col_name)
                nova_linha[index] = valor
        
        ws.append_row(nova_linha)
        return True, "Sucesso"
    except Exception as e: 
        return False, str(e)

def excluir_agendamento(indice_linha):
    """Remove uma linha da planilha quando você deleta um serviço."""
    sheet = conectar_google_sheets()
    if sheet is None: return False
    try: 
        ws = sheet.worksheet("Agendamentos")
        # +2 porque o Python começa no 0 e a planilha tem cabeçalho
        ws.delete_rows(indice_linha + 2) 
        return True
    except: 
        return False
