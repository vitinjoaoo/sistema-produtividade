import streamlit as st
import sqlite3
import hashlib
from src.styles.custom_css import estilo
from src.components.layout.menu_lateral import renderizar_sidebar

# 1. CONFIGURAÇÕES INICIAIS DA PÁGINA
# Define o título da aba do navegador e o layout expandido (wide)
st.set_page_config(page_title="Meu Perfil", layout="wide")

# Aplica o tema visual e renderiza o menu de navegação lateral
estilo()
renderizar_sidebar()

def renderizar_perfil():
    """Função que constrói a interface de gerenciamento de conta do usuário."""
    
    # --- BARREIRA DE SEGURANÇA ---
    # Verifica se o dicionário de sessão possui os dados do usuário. 
    # Se não houver, impede o carregamento da página (Proteção de Rota).
    if 'usuario_nome' not in st.session_state:
        st.error("Acesso negado. Por favor, realize o login.")
        return

    st.title("👤 Configurações de Perfil")
    st.write("Gerencie suas informações e segurança da conta.")
    st.write("---")

    # Organiza a página em duas colunas de tamanhos iguais com um espaçamento grande entre elas
    col_info, col_senha = st.columns([1, 1], gap="large")

    # --- COLUNA 1: EXIBIÇÃO DE INFORMAÇÕES DO USUÁRIO ---
    with col_info:
        st.markdown("### 📋 Meus Dados")
        
        # Uso de st.session_state para resgatar dados persistidos desde o momento do login
        st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
                <p><b>Nome Completo:</b> {st.session_state['usuario_nome']}</p>
                <p><b>Usuário de Acesso:</b> {st.session_state['username_logado']}</p>
                <p><b>Perfil do Sistema:</b> {st.session_state['usuario_perfil']}</p>
                <p><small>Para alterar dados cadastrais, entre em contato com o Administrador.</small></p>
            </div>
        """, unsafe_allow_html=True)

    # --- COLUNA 2: FUNCIONALIDADE DE REDEFINIÇÃO DE SENHA ---
    with col_senha:
        st.markdown("### 🔐 Alterar Senha")
        st.caption("Por segurança, você precisa confirmar sua senha atual antes de cadastrar uma nova.")
        
        # Uso de st.form para garantir que o processamento só ocorra após clicar no botão (evita recarregamentos desnecessários)
        with st.form("form_alterar_senha"):
            # Entrada de dados sensíveis ocultada (type="password")
            senha_antiga = st.text_input("Senha Atual", type="password")
            st.markdown("<hr style='margin: 10px 0; opacity: 0.2;'>", unsafe_allow_html=True)
            
            nova_senha = st.text_input("Nova Senha", type="password", help="Mínimo de 4 caracteres")
            confirmar_senha = st.text_input("Confirmar Nova Senha", type="password")
            
            btn_alterar = st.form_submit_button("Atualizar Minha Senha", use_container_width=True)
            
            if btn_alterar:
                username = st.session_state['username_logado']
                
                # --- PROCESSO DE VALIDAÇÃO E BANCO DE DADOS ---
                # 1. Conexão com o banco SQLite para verificar a autenticidade da senha atual
                conn = sqlite3.connect('produtividade.db')
                c = conn.cursor()
                c.execute("SELECT password FROM usuarios WHERE username = ?", (username,))
                resultado = c.fetchone()
                senha_db = resultado[0] if resultado else None
                hash_antiga = hashlib.sha256(senha_antiga.encode()).hexdigest()

                # --- REGRAS DE NEGÓCIO E FILTROS ---
                if hash_antiga != senha_db:
                    st.error("❌ A 'Senha Atual' está incorreta.")
                elif nova_senha != confirmar_senha:
                    st.error("❌ As novas senhas não coincidem.")
                elif len(nova_senha) < 4:
                    st.warning("⚠️ A nova senha deve ter pelo menos 4 caracteres.")
                else:
                    try:
                        # 3. ATUALIZAÇÃO: Se passar em todos os testes, gera o novo Hash e grava no Banco
                        novo_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
                        c.execute("UPDATE usuarios SET password = ? WHERE username = ?", (novo_hash, username))
                        conn.commit()
                        st.success("✅ Senha atualizada com sucesso!")
                        st.balloons() # Feedback visual positivo
                    except Exception as e:
                        st.error(f"Erro ao acessar o banco: {e}")
                
                conn.close()

# Ponto de execução da página
if __name__ == "__main__":
    renderizar_perfil()