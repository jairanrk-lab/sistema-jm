import streamlit as st

def formatar_moeda(valor):
    """Transforma números em R$ 0,00 (Ex: 350 -> R$ 350,00)."""
    try:
        valor_float = float(valor)
        return f"R$ {valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def obter_icone_html(cat):
    """Escolhe o desenho do carrinho baseado no tipo de veículo."""
    if not isinstance(cat, str): 
        return '<i class="bi bi-car-front-fill"></i>'
    
    c = cat.lower()
    if "moto" in c: 
        return '<i class="bi bi-motorcycle"></i>'
    elif "suv" in c or "picape" in c or "caminhonete" in c: 
        return '<i class="bi bi-truck-front-fill"></i>'
    elif "van" in c: 
        return '<i class="bi bi-bus-front-fill"></i>'
    else: 
        return '<i class="bi bi-car-front-fill"></i>'
