import streamlit as st

def renderizar_sidebar():
    """
    Módulo de Navegação Estruturada (Sidebar).
    Centraliza a interface de navegação e o controle de sessão (Logout) para todas as páginas.
    """
    with st.sidebar:
        # Cabeçalho do Menu com Identidade Visual (Neumorfismo)
        st.markdown("""
            <div style='padding: 15px; border-radius: 15px; box-shadow: inset 2px 2px 5px #B8C2CC, inset -2px -2px 5px #F0F5FF; text-align: center; margin-bottom: 25px;'>
                <h2 style='margin:0; font-size: 15px; color: #313945; font-weight: 700;'>✅ Sistema de Gestão de Demandas (GD).</h2>
                <p style='margin:0; font-size: 11px; opacity: 0.7;'>Controle de Produtividade</p>
            </div>
        """, unsafe_allow_html=True)
        
        # --- LINKS DE NAVEGAÇÃO INTERNA ---
        # Define os pontos de entrada para os diferentes módulos do sistema
        st.page_link("app.py", label="Dashboard", icon="📊")
        st.page_link("pages/tarefas.py", label="Delegação de Atividades", icon="📝")
        st.page_link("pages/registro.py", label="Registro Diário", icon="⏱️")
        st.page_link("pages/relatorios.py", label="Relatórios", icon="📈")
        st.page_link("pages/equipe.py", label="Equipe", icon="👥")
        st.page_link("pages/perfil.py", label="Meu Perfil", icon="👤")
        
        st.write("")
        
        # Indicador de Status do Sistema
        try:
            st.checkbox("Produtividade Ativa", value=True, disabled=True, key="unique_sidebar_check")
        except:
            pass

        st.write("---") # Linha divisória visual

        # --- MÓDULO DE CONTROLE DE ACESSO (LOGOUT) ---
        # Centralizado aqui para aparecer em todas as páginas do sistema.
        # Ao ser clicado, altera o estado da sessão e força o redirecionamento para o login.
        if st.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state['autenticado'] = False
            # Limpa dados sensíveis da memória por segurança
            st.session_state['username_logado'] = None
            st.session_state['usuario_nome'] = None
            st.rerun() # Reinicia o app para voltar à tela de login