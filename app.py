import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import hashlib
import smtplib
import random
import string
import re
from datetime import datetime, date
from email.message import EmailMessage
from src.styles.custom_css import estilo 
from src.components.layout.menu_lateral import renderizar_sidebar

# --- CONFIGURAÇÃO DO SERVIDOR DE E-MAIL (Comunicação Externa) ---
# Esta parte configura a integração com o servidor SMTP do Google para envio de e-mails.
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_REMETENTE = "vitinjoao257@gmail.com"
EMAIL_PASSWORD = "iovp rkql wsef yhgs"

# --- FUNÇÕES DE SUPORTE (Lógica de Segurança) ---
def gerar_senha_aleatoria(tamanho=6):
    """Gera uma credencial temporária para o fluxo de recuperação."""
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choice(caracteres) for _ in range(tamanho))

def enviar_email_real(email_destino, nova_senha):
    """Integra o sistema com o protocolo SMTP para notificações externas."""
    msg = EmailMessage()
    msg.set_content(f"Sua nova senha temporária é: {nova_senha}")
    msg['Subject'] = '🔑 Redefinição de Senha - Sistema de Gestão de Demandas'
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = email_destino
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(EMAIL_REMETENTE, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.sidebar.error(f"Erro técnico no SMTP: {e}")
        return False

# --- FUNÇÕES DE PERSISTÊNCIA (Integração com Banco de Dados SQL) ---
# Esta seção gerencia toda a camada de dados (Model) do sistema usando SQLite3.
def criar_tabelas_sistema():
    """Define a arquitetura do banco de dados e garante a integridade das tabelas."""
    conn = sqlite3.connect('produtividade.db')
    c = conn.cursor()
    # Criação das tabelas de Entidades (Usuários) e Fatos (Tarefas, Jornada)
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT, email TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tarefas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  titulo TEXT, pontos INTEGER, status TEXT, usuario_id TEXT, 
                  num_processo TEXT, data_atribuicao TEXT, data_esperada TEXT, data_conclusao TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS registros_jornada 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  data TEXT, hora_inicio TEXT, hora_fim TEXT, intervalo REAL, 
                  horas_liquidas REAL, humor TEXT, usuario_id TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS configuracoes_metas 
                 (perfil TEXT PRIMARY KEY, valor_meta INTEGER)''')
    
    # Seed: População inicial de metas parametrizáveis
    c.execute("SELECT COUNT(*) FROM configuracoes_metas")
    if c.fetchone()[0] == 0:
        metas_iniciais = [
            ("Servidor Integral", 88), ("Servidor Híbrido", 84),
            ("Servidor Presencial", 80), ("Colaborador Presencial", 80)
        ]
        c.executemany("INSERT INTO configuracoes_metas VALUES (?, ?)", metas_iniciais)

    # Manutenção evolutiva do esquema do banco (Migrações)
    try: c.execute("ALTER TABLE tarefas ADD COLUMN data_atribuicao TEXT")
    except: pass
    try: c.execute("ALTER TABLE tarefas ADD COLUMN data_esperada TEXT")
    except: pass
    conn.commit()
    conn.close()

def buscar_metas_db():
    """Recupera as metas vigentes para alimentar a lógica de BI (Business Intelligence)."""
    conn = sqlite3.connect('produtividade.db')
    df = pd.read_sql_query("SELECT * FROM configuracoes_metas", conn)
    conn.close()
    return dict(zip(df['perfil'], df['valor_meta']))

def atualizar_meta_db(perfil, novo_valor):
    """Permite ao administrador alterar as regras de negócio em tempo real."""
    conn = sqlite3.connect('produtividade.db')
    c = conn.cursor()
    c.execute("UPDATE configuracoes_metas SET valor_meta = ? WHERE perfil = ?", (novo_valor, perfil))
    conn.commit()
    conn.close()

def redefinir_senha_banco(email, nova_senha):
    """Atualiza as credenciais no banco utilizando Hashing SHA-256 para segurança."""
    conn = sqlite3.connect('produtividade.db')
    c = conn.cursor()
    senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
    c.execute("UPDATE usuarios SET password = ? WHERE email = ?", (senha_hash, email))
    sucesso = c.rowcount > 0
    conn.commit()
    conn.close()
    return sucesso

def verificar_login(username, password):
    """Valida o acesso comparando o hash da senha informada com o banco."""
    conn = sqlite3.connect('produtividade.db')
    c = conn.cursor()
    senha_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT username, nome, perfil FROM usuarios WHERE username = ? AND password = ?", (username, senha_hash))
    user = c.fetchone()
    conn.close()
    return user

def cadastrar_usuario(username, password, nome, perfil, email):
    """Insere um novo nó de usuário na rede do sistema."""
    try:
        conn = sqlite3.connect('produtividade.db')
        c = conn.cursor()
        senha_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO usuarios (username, password, nome, perfil, email) VALUES (?, ?, ?, ?, ?)", 
                  (username, senha_hash, nome, perfil, email))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

# --- LÓGICA DE INTERFACE (Frontend com Streamlit) ---
st.set_page_config(page_title="Painel de Produtividade", layout="wide")
criar_tabelas_sistema()

def main():
    # Controle de Estado da Sessão (Session State)
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    # --- FLUXO 1: MÓDULO DE AUTENTICAÇÃO (TELA INICIAL) ---
    # Esta parte faz aparecer a tela de login, cadastro e recuperação.
    if not st.session_state['autenticado']:
        estilo() # Injeção de CSS personalizado
        st.markdown("<div style='text-align: center; padding: 20px;'>", unsafe_allow_html=True)
        st.title("⚖️ Sistema de Gestão de Demandas")
        st.caption("Controle de produtividade e monitoramento de metas")
        st.markdown("</div>", unsafe_allow_html=True)

        col_l, col_r = st.columns([1, 1])
        with col_l:
            tab_login, tab_cadastro = st.tabs(["Login", "Criar Conta"])
            
            # Sub-fluxo de Recuperação (Integração com E-mail)
            with tab_login:
                if st.session_state.get('recuperando'):
                    email_rec = st.text_input("E-mail Institucional")
                    if st.button("Enviar Nova Senha", use_container_width=True):
                        if not email_rec:
                            st.warning("Informe o e-mail.")
                        else:
                            nova_pass = gerar_senha_aleatoria()
                            if redefinir_senha_banco(email_rec, nova_pass):
                                if enviar_email_real(email_rec, nova_pass): st.success("E-mail enviado!")
                                else: st.warning(f"Erro no envio. Use a senha: {nova_pass}")
                            else: st.error("E-mail não localizado.")
                    if st.button("Voltar"): st.session_state['recuperando'] = False; st.rerun()
                
                # Interface de Entrada de Dados
                else:
                    with st.form("form_login"):
                        u = st.text_input("Usuário"); p = st.text_input("Senha", type="password")
                        if st.form_submit_button("Entrar", use_container_width=True):
                            valido = verificar_login(u, p)
                            if valido:
                                # Persistência de dados do usuário logado na sessão ativa
                                st.session_state.update({'autenticado': True, 'username_logado': valido[0], 'usuario_nome': valido[1], 'usuario_perfil': valido[2]})
                                st.rerun()
                            else: st.error("Credenciais inválidas.")
                    st.button("Recuperar minha senha", on_click=lambda: st.session_state.update({"recuperando": True}), type="secondary")
            
            # Módulo de Cadastro de novos usuários
            with tab_cadastro:
                with st.form("form_cadastro"):
                    n_nome = st.text_input("Nome Completo"); n_email = st.text_input("E-mail Institucional")
                    n_user = st.text_input("Nome de Usuário"); n_pass = st.text_input("Senha", type="password")
                    n_perfil = st.selectbox("Perfil", ["Servidor Integral", "Servidor Híbrido", "Servidor Presencial", "Colaborador Presencial"])
                    if st.form_submit_button("Cadastrar"):
                        if not all([n_user, n_pass, n_nome, n_email]): st.warning("Preencha todos os campos.")
                        elif cadastrar_usuario(n_user, n_pass, n_nome, n_perfil, n_email): st.success("Conta criada!")
                        else: st.error("Erro: Usuário já existe.")

    # --- FLUXO 2: DASHBOARD E MONITORAMENTO (ÁREA RESTRITA) ---
    # Esta parte faz aparecer a tela principal de BI e os gráficos.
    else:
        estilo() 
        renderizar_sidebar()

        # Data Wrangling: Carregamento e preparação dos dados para os gráficos
        conn = sqlite3.connect('produtividade.db')
        df_tarefas = pd.read_sql_query("SELECT * FROM tarefas", conn)
        df_usuarios = pd.read_sql_query("SELECT nome, perfil FROM usuarios", conn)
        conn.close()

        perfil = st.session_state['usuario_perfil']
        nome_user = st.session_state['usuario_nome']
        metas_ref = buscar_metas_db()
        data_hoje = date.today()
        
        # Filtro de Visibilidade por Nível de Acesso (Administrador vs Servidor)
        is_admin = "Administrador" in perfil
        df_view = df_tarefas if is_admin else df_tarefas[df_tarefas['usuario_id'] == nome_user]

        # Lógica de Auditoria Temporal (Verifica atrasos automaticamente)
        if not df_tarefas.empty:
            def definir_situacao(row):
                if row['status'] == 'CONCLUÍDO': return 'Concluída'
                try:
                    dt_limite = datetime.strptime(row['data_esperada'], '%Y-%m-%d').date()
                    return 'Atrasada' if data_hoje > dt_limite else 'Em Andamento'
                except: return 'Sem Prazo'
            df_tarefas['situacao_monitoramento'] = df_tarefas.apply(definir_situacao, axis=1)

        st.title("📊 Monitoramento de Demandas")
        st.markdown(f"Bem-vindo, **{nome_user}**.")

        # Módulo Administrativo: Parametrização de Metas
        if is_admin:
            with st.expander("⚙️ Configurações Administrativas"):
                st.write("Ajuste as metas de pontuação do sistema:")
                col_m1, col_m2 = st.columns(2)
                for i, (perfil_meta, valor) in enumerate(metas_ref.items()):
                    col_alvo = col_m1 if i % 2 == 0 else col_m2
                    with col_alvo:
                        novo_v = st.number_input(f"Meta: {perfil_meta}", value=int(valor), key=f"cfg_{perfil_meta}")
                        if novo_v != valor:
                            if st.button(f"Salvar Meta {i}", key=f"btn_{i}"):
                                atualizar_meta_db(perfil_meta, novo_v); st.rerun()

        # --- CARDS DE KPIS (Indicadores Chave de Desempenho) ---
        # Esta parte renderiza os cards coloridos no topo do dashboard.
        pts_c = df_view[df_view['status'] == 'CONCLUÍDO']['pontos'].sum() if not df_view.empty else 0
        pts_p = df_view[df_view['status'] == 'PENDENTE']['pontos'].sum() if not df_view.empty else 0
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><div class="metric-title">📋 TOTAL TAREFAS</div><div class="metric-value">{len(df_view)}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="metric-title">🏆 PONTOS CONCLUÍDOS</div><div class="metric-value">{pts_c}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><div class="metric-title">🚀 PONTOS PENDENTES</div><div class="metric-value">{pts_p}</div></div>', unsafe_allow_html=True)
        with c4:
            if not df_view.empty and 'data_esperada' in df_view.columns:
                pendentes = df_view[df_view['status'] == 'PENDENTE']
                if not pendentes.empty:
                    atrasadas = any(pd.to_datetime(pendentes['data_esperada']).dt.date < data_hoje)
                    status_txt = "ATENÇÃO" if atrasadas else "EM DIA"
                else: status_txt = "SEM PENDÊNCIAS"
            else: status_txt = "NENHUM DADO"
            st.markdown(f'<div class="metric-card"><div class="metric-title">✨ STATUS</div><div class="metric-value">{status_txt}</div></div>', unsafe_allow_html=True)

        st.write("---")

        # --- MÓDULO DE BI (Gráficos Analíticos) ---
        # Esta seção integra Plotly Express para visualização dinâmica dos dados.
        if not df_tarefas.empty:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("### 👥 Produtividade por Executor")
                df_stack = df_tarefas.groupby(['usuario_id', 'situacao_monitoramento']).size().reset_index(name='Total')
                fig_stack = px.bar(df_stack, x='usuario_id', y='Total', color='situacao_monitoramento', 
                                  barmode='stack', color_discrete_map={'Concluída': '#2EB086', 'Em Andamento': '#5D78FF', 'Atrasada': '#FF4B4B'})
                fig_stack.update_layout(plot_bgcolor='rgba(0,0,0,0)', height=350)
                st.plotly_chart(fig_stack, use_container_width=True)

            with col_g2:
                st.markdown("### 🎯 Desempenho vs Meta")
                df_prod = df_tarefas[df_tarefas['status'] == 'CONCLUÍDO'].groupby('usuario_id')['pontos'].sum().reset_index()
                def get_meta(user):
                    p = df_usuarios[df_usuarios['nome'] == user]['perfil'].values
                    return metas_ref.get(p[0], 80) if len(p) > 0 else 80
                df_prod['Meta'] = df_prod['usuario_id'].apply(get_meta)
                fig_meta = px.bar(df_prod, x='usuario_id', y='pontos', color_discrete_sequence=['#2EB086'], opacity=0.7)
                fig_meta.add_trace(go.Scatter(x=df_prod['usuario_id'], y=df_prod['Meta'], name="Meta", mode='lines', line=dict(color='#FF4B4B', dash='dot')))
                fig_meta.update_layout(plot_bgcolor='rgba(0,0,0,0)', height=350)
                st.plotly_chart(fig_meta, use_container_width=True)
        else:
            st.info("Aguardando lançamentos para gerar gráficos.")

if __name__ == "__main__":
    main()