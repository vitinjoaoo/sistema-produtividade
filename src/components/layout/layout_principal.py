import streamlit as st

def configurar_layout(titulo_pagina="Dashboard de Produtividade"):
    """
    Traduz o AppLayout.jsx para Streamlit.
    Configura a página, o menu lateral e o container principal.
    """
    
    # 1. Configurações da aba do navegador (Equivalente ao min-h-screen bg-background)
    st.set_page_config(
        page_title=titulo_pagina,
        page_icon="🚀",
        layout="wide", # Usa a tela toda (max-w-7xl mx-auto)
        initial_sidebar_state="expanded"
    )

    # 2. Sidebar (Equivalente ao componente <Sidebar /> da linha 10)
    with st.sidebar:
        st.title("Menu Principal")
        # Aqui é onde os links de navegação vão entrar depois
        # Ex: st.page_link("pages/dashboard.py", label="Dashboard", icon="📊")
        
    # 3. Área Principal (Equivalente ao <main> e <Outlet /> das linhas 11-13)
    # No Streamlit, tudo o que você escrever fora do 'with st.sidebar' 
    # cai automaticamente no Outlet central.
    
    st.markdown(f"# {titulo_pagina}")
    st.divider()

def renderizar_rodape():
    """Opcional: um rodapé padrão para o layout"""
    st.markdown("---")
    st.caption("Sistema de Gestão de Produtividade - TCC 2026")