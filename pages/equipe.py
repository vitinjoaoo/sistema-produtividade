import streamlit as st
import sqlite3
import pandas as pd
# Importação de funções personalizadas de estilo e navegação
from src.styles.custom_css import estilo
from src.components.layout.menu_lateral import renderizar_sidebar

# 1. APLICAÇÃO DE ESTILO E RENDERIZAÇÃO DO MENU
# Ativa o CSS customizado e a barra lateral em todas as páginas
estilo()
renderizar_sidebar()

def renderizar_pagina_equipe():
    """Função principal para desenhar a interface da página da equipe."""
    st.title("👥 Minha Equipe")
    st.caption("Visualização dos colaboradores cadastrados no sistema")

    # --- CONEXÃO COM O BANCO PARA BUSCAR USUÁRIOS REAIS ---
    try:
        # Estabelece conexão com o banco de dados SQLite local
        conn = sqlite3.connect('produtividade.db')
        
        # Consulta 1: Busca o nome real e o login (username) de todos os usuários
        df_usuarios = pd.read_sql_query("SELECT nome, username FROM usuarios", conn)
        
        # Consulta 2: Busca a produtividade acumulada (soma de pontos)
        # Filtei apenas tarefas 'CONCLUÍDO' para contabilizar a produção real
        df_pontos = pd.read_sql_query("""
            SELECT usuario_id, SUM(pontos) as total 
            FROM tarefas 
            WHERE status = 'CONCLUÍDO' 
            GROUP BY usuario_id
        """, conn)
        
        # Fecha a conexão após a leitura para liberar o arquivo do banco
        conn.close()
    except Exception as e:
        # Caso o banco não exista ou as tabelas não tenham sido criadas, exibe erro
        st.error("Ainda não existem usuários cadastrados ou o banco não foi inicializado.")
        return

    # --- RENDERIZAÇÃO DOS CARDS ---
    # Verifica se a consulta retornou algum usuário
    if not df_usuarios.empty:
        # Itera sobre cada linha do DataFrame de usuários (colaboradores)
        for _, row in df_usuarios.iterrows():
            
            # Lógica de cruzamento de dados:
            # Tenta encontrar a pontuação total no df_pontos usando o nome do usuário como chave
            pontos_user = df_pontos[df_pontos['usuario_id'] == row['nome']]['total'].values
            
            # Se o usuário tiver pontos, armazena; caso contrário, define como zero
            total_pts = int(pontos_user[0]) if len(pontos_user) > 0 else 0

            # Renderização de Interface com HTML e CSS (Inline)
            # Criei um "card" visual para cada membro da equipe
            st.markdown(f'''
                <div class="task-row" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div>
                        <!-- Exibe o nome real do colaborador -->
                        <div style="font-weight:700; font-size: 16px;">👤 {row['nome']}</div>
                        <!-- Exibe o username com opacidade menor para diferenciar do nome principal -->
                        <div style="font-size: 11px; opacity: 0.7;">Usuário: @{row['username']}</div>
                    </div>
                    <div style="text-align: right;">
                        <!-- Badge visual para destacar a pontuação do servidor -->
                        <span class="badge-status" style="background: rgba(93, 120, 255, 0.1); color: #5D78FF;">
                            🏆 {total_pts} pts
                        </span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
    else:
        # Mensagem caso o banco de dados esteja vazio
        st.info("Nenhum colaborador encontrado no banco de dados.")

# Ponto de entrada do script: executa a função se o arquivo for chamado diretamente
if __name__ == "__main__":
    renderizar_pagina_equipe()