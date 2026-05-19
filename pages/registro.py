import streamlit as st
import sqlite3
import pandas as pd
import smtplib
from email.message import EmailMessage
from datetime import date, datetime, time
from src.components.layout.menu_lateral import renderizar_sidebar
from src.styles.custom_css import estilo

# --- MÓDULO DE COMUNICAÇÃO (Protocolo SMTP) ---
# Esta seção implementa a integração com serviços de terceiros (Gmail)
# permitindo que o gestor atue sobre as demandas em tempo real.
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_REMETENTE = "vitinjoao257@gmail.com"
EMAIL_PASSWORD = "iovp rkql wsef yhgs" 

def enviar_email_real(email_destino, mensagem_corpo, nome_servidor):
    """
    Encapsula a lógica de envio de mensagens via SMTP_SSL.
    Garante que a comunicação administrativa chegue ao e-mail institucional do servidor.
    """
    msg = EmailMessage()
    conteudo = f"Olá, {nome_servidor}!\n\nMensagem da Administração:\n{mensagem_corpo}"
    msg.set_content(conteudo)
    msg['Subject'] = '✉️ Contato Administrativo - Sistema de Produtividade'
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = email_destino
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(EMAIL_REMETENTE, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception:
        return False

# --- CAMADA DE PERSISTÊNCIA E REGRAS DE NEGÓCIO ---

def salvar_registro_completo(data, inicio, fim, intervalo, humor, usuario):
    """
    Calcula a jornada líquida e persiste os dados no SQLite.
    Demonstra o tratamento de tipos de dados (Data/Hora) e aritmética de tempo.
    """
    conn = sqlite3.connect('produtividade.db')
    c = conn.cursor()
    
    # Processamento de Dados: Conversão de objetos time para strings comparáveis
    # Correção: Streamlit time_input usa H:M, ajustado para evitar erro de conversão
    h_ini_str = inicio.strftime('%H:%M')
    h_fim_str = fim.strftime('%H:%M')
    
    fmt = '%H:%M'
    t1 = datetime.strptime(h_ini_str, fmt)
    t2 = datetime.strptime(h_fim_str, fmt)
    
    # Cálculo da métrica de produtividade horária (Delta Time)
    delta = (t2 - t1).total_seconds() / 3600 
    horas_liquidas = delta - intervalo 
    
    c.execute("""INSERT INTO registros_jornada 
                  (data, hora_inicio, hora_fim, intervalo, horas_liquidas, humor, usuario_id) 
                  VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (data.strftime('%Y-%m-%d'), h_ini_str, h_fim_str, intervalo, round(horas_liquidas, 2), humor, usuario))
    conn.commit()
    conn.close()

def buscar_registros_jornada(usuario, perfil):
    """
    Implementa a Segurança de Dados e Níveis de Acesso (RBAC).
    Admins visualizam o ecossistema completo; usuários apenas seus últimos 10 dados.
    """
    conn = sqlite3.connect('produtividade.db')
    c = conn.cursor()
    if "Administrador" in perfil:
        c.execute("SELECT * FROM registros_jornada ORDER BY data DESC, hora_inicio DESC")
    else:
        c.execute("SELECT * FROM registros_jornada WHERE usuario_id = ? ORDER BY data DESC LIMIT 10", (usuario,))
    dados = c.fetchall()
    conn.close()
    return dados

def buscar_email_usuario(nome_usuario):
    """Resgata o e-mail do colaborador na tabela de usuários para permitir o contato."""
    conn = sqlite3.connect('produtividade.db')
    c = conn.cursor()
    c.execute("SELECT email FROM usuarios WHERE nome = ?", (nome_usuario,))
    resultado = c.fetchone()
    conn.close()
    return resultado[0] if resultado else None

# --- RENDERIZAÇÃO DA INTERFACE (UX/UI) ---

def renderizar_pagina_registro():
    estilo() 
    renderizar_sidebar()
    
    if 'usuario_nome' not in st.session_state:
        st.error("Acesso negado. Faça login no Painel Principal.")
        return

    usuario_atual = st.session_state['usuario_nome']
    perfil_atual = st.session_state.get('usuario_perfil', 'Colaborador')
    is_admin = "Administrador" in perfil_atual

    st.title("⏱️ Registro de Jornada")

    # 1. ENTRADA DE DADOS (Visão do Servidor/Colaborador)
    if not is_admin:
        with st.expander("📥 Lançar meu Expediente de Hoje", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                data_reg = st.date_input("Data", value=date.today())
                humor_opcoes = {"Exausto": "Regular", "Neutro": "Bom", "Produtivo": "Ótimo"}
                sentimento = st.select_slider("Como está seu foco?", options=list(humor_opcoes.keys()), value="Neutro")
            with c2:
                h_inicio = st.time_input("Início", value=time(9, 0))
                h_fim = st.time_input("Fim", value=time(18, 0))
            with c3:
                intervalo = st.number_input("Intervalo (h)", min_value=0.0, max_value=3.0, value=1.0, step=0.5)
                if st.button("Confirmar ✅", use_container_width=True):
                    if h_fim <= h_inicio:
                        st.error("Horário de fim inválido.")
                    else:
                        salvar_registro_completo(data_reg, h_inicio, h_fim, intervalo, humor_opcoes[sentimento], usuario_atual)
                        st.success("Jornada registrada!")
                        st.rerun()

    st.write("---")

    # 2. MONITORAMENTO E GESTÃO (Visão do Gestor/Mural)
    st.markdown("### 📋 Mural de Disponibilidade")
    dados_brutos = buscar_registros_jornada(usuario_atual, perfil_atual)
    
    if dados_brutos:
        df_jornada = pd.DataFrame(dados_brutos, columns=['id', 'data', 'inicio', 'fim', 'intervalo', 'liquidas', 'humor', 'usuario'])
        
        # Filtro de Auditoria para o Administrador (Gestão de Equipe)
        if is_admin:
            lista_usuarios = ["Todos"] + sorted(df_jornada['usuario'].unique().tolist())
            filtro_user = st.selectbox("Localizar Servidor", lista_usuarios)
            if filtro_user != "Todos":
                df_jornada = df_jornada[df_jornada['usuario'] == filtro_user]

        hoje = date.today()

        # Renderização dinâmica dos cards com lógica visual de cores (Gestão à Vista)
        for _, row in df_jornada.iterrows():
            dt_registro = datetime.strptime(row['data'], '%Y-%m-%d').date()
            
            # Lógica de cores: Vermelho para registros passados, Azul para o dia atual
            cor_status = "#FF4B4B" if dt_registro < hoje else "#5D78FF"
            
            with st.container():
                col_card, col_acao = st.columns([4, 1])
                with col_card:
                    # Injeção de HTML para cards personalizados com borda indicativa de status
                    st.markdown(f"""
                        <div style="padding:15px; border-radius:8px; background-color:white; border-left: 5px solid {cor_status}; margin-bottom:10px; box-shadow: 0px 2px 4px rgba(0,0,0,0.05);">
                            <span style="font-size:1rem;">👤 <b>{row['usuario']}</b> | 📅 {dt_registro.strftime('%d/%m/%Y')}</span><br>
                            <span style="color:{cor_status};"><b>Horário:</b> {row['inicio'][:5]} às {row['fim'][:5]}</span><br>
                            <small style="color:#666;">Carga Líquida: {row['liquidas']}h | Foco: {row['humor']}</small>
                        </div>
                    """, unsafe_allow_html=True)

                # Ação Administrativa: Módulo de contato via Popover (UX Otimizada)
                if is_admin:
                    with col_acao:
                        st.write("")
                        with st.popover("✉️ Contatar"):
                            email_dest = buscar_email_usuario(row['usuario'])
                            if email_dest:
                                msg_texto = st.text_area("Instruções:", key=f"txt_{row['id']}")
                                if st.button("Enviar 🚀", key=f"send_{row['id']}", use_container_width=True):
                                    if msg_texto:
                                        if enviar_email_real(email_dest, msg_texto, row['usuario']):
                                            st.success("Enviado!")
                                        else:
                                            st.error("Erro SMTP.")
                                    else:
                                        st.warning("Campo vazio.")
                            else:
                                st.error("E-mail não cadastrado.")
    else:
        st.info("Nenhum registro encontrado.")

if __name__ == "__main__":
    renderizar_pagina_registro()