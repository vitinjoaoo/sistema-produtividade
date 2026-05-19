import streamlit as st

def renderizar_404(nome_pagina="Página"):
    """
    Traduz o componente PageNotFound.jsx para Streamlit.
    Mostra o erro 404 e uma nota especial para administradores.
    """
    
    # Simula o estilo min-h-screen e centralização (Linhas 21-22)
    st.markdown("""
        <style>
            .container-404 {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                padding: 50px 20px;
            }
            .erro-404 {
                font-size: 72px;
                color: #cbd5e1;
                font-weight: 300;
                margin: 0;
            }
            .linha-separadora {
                height: 2px;
                width: 64px;
                background-color: #e2e8f0;
                margin: 10px auto;
            }
            .admin-note {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                margin-top: 30px;
                text-align: left;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="container-404">', unsafe_allow_html=True)
        
        # Código do Erro (Linhas 26-29)
        st.markdown('<h1 class="erro-404">404</h1>', unsafe_allow_html=True)
        st.markdown('<div class="linha-separadora"></div>', unsafe_allow_html=True)
        
        # Mensagem Principal (Linhas 32-37)
        st.subheader("Página Não Encontrada")
        st.write(f'A página **"{nome_pagina}"** não foi encontrada nesta aplicação.')

        # Nota de Administrador (Linhas 40-52)
        # Verificamos no st.session_state que criamos no arquivo de autenticacao
        if st.session_state.get('esta_autenticado'):
            usuario = st.session_state.get('usuario', {})
            if usuario.get('perfil') == 'Admin':
                st.markdown(f"""
                    <div class="admin-note">
                        <p style="color: #334155; font-weight: 500; margin-bottom: 5px;">⚠️ Nota do Administrador</p>
                        <p style="color: #475569; font-size: 14px; line-height: 1.5;">
                            Isso pode significar que a página ainda não foi implementada no Python. 
                            Verifique se o arquivo existe na pasta <b>/pages</b>.
                        </p>
                    </div>
                """, unsafe_allow_html=True)

        # Botão de Voltar (Linhas 56-65)
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("🏠 Voltar para o Início"):
            st.switch_page("app.py") # Comando do Streamlit para mudar de página