import streamlit as st
import time
from datetime import timedelta

def renderizar_cronometro():
    """
    Traduz o WorkTimer.jsx para Python/Streamlit.
    Gerencia o estado do cronômetro (rodando, pausado, parado).
    """
    st.markdown("### ⏱️ Cronômetro de Trabalho")

    # 1. Inicialização do Estado (Equivalente às linhas 6-8 do print)
    if 'segundos' not in st.session_state:
        st.session_state.segundos = 0
    if 'rodando' not in st.session_state:
        st.session_state.rodando = False
    if 'ultimo_check' not in st.session_state:
        st.session_state.ultimo_check = None

    # 2. Lógica do Timer (Equivalente ao useEffect das linhas 10-17)
    if st.session_state.rodando:
        agora = time.time()
        if st.session_state.ultimo_check is not None:
            decorrido = agora - st.session_state.ultimo_check
            st.session_state.segundos += int(decorrido)
        st.session_state.ultimo_check = agora
        time.sleep(1) # Espera 1 segundo para atualizar
        st.rerun()

    # 3. Formatação do Tempo (Equivalente às linhas 19-24)
    tempo_formatado = str(timedelta(seconds=st.session_state.segundos))

    # Interface Visual (Linhas 35-40)
    st.markdown(f"""
        <div style="text-align: center; background-color: #f0f2f6; padding: 20px; border-radius: 15px;">
            <p style="font-size: 14px; color: gray; margin-bottom: 5px;">Tempo de Foco</p>
            <h1 style="font-family: monospace; font-size: 48px; margin: 0;">{tempo_formatado}</h1>
        </div>
    """, unsafe_allow_html=True)

    st.write("") # Espaçamento

    # 4. Botões de Controle (Linhas 41-66)
    col1, col2, col3 = st.columns(3)

    # Botão Iniciar (Linha 43)
    if not st.session_state.rodando:
        if col1.button("▶️ Iniciar", use_container_width=True):
            st.session_state.rodando = True
            st.session_state.ultimo_check = time.time()
            st.rerun()
    else:
        # Botão Pausar (Linha 52)
        if col1.button("⏸️ Pausar", use_container_width=True):
            st.session_state.rodando = False
            st.session_state.ultimo_check = None
            st.rerun()

    # Botão Parar/Resetar (Linha 58 - handleStop)
    if col3.button("⏹️ Parar", use_container_width=True, type="primary"):
        minutos_totais = round(st.session_state.segundos / 60)
        
        # Simula o callback onStop (Linha 30)
        if minutos_totais > 0:
            st.success(f"Sessão finalizada: {minutos_totais} minutos registrados!")
        
        # Reset (Linha 31)
        st.session_state.segundos = 0
        st.session_state.rodando = False
        st.session_state.ultimo_check = None
        st.rerun()