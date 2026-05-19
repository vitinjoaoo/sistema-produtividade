import streamlit as st
from datetime import date, timedelta
from src.lib.regras_negocio import TABELA_PRODUTIVIDADE, obter_opcoes_tarefas

def renderizar_formulario_tarefa(tarefa_inicial=None, ao_salvar=None, ao_cancelar=None):
    with st.form("form_tarefa_stj"):
        st.subheader("📝 Registro de Demanda Administrativa")
        
        # Seleção baseada na planilha
        opcoes = obter_opcoes_tarefas()
        categoria = st.selectbox("Categoria - Tarefa/Demanda", options=opcoes)
        
        # Recupera as regras da planilha
        regra = TABELA_PRODUTIVIDADE[categoria]
        
        col1, col2 = st.columns(2)
        with col1:
            pontos = st.number_input("Pontuação Prevista", value=float(regra['pontos']), disabled=True)
        
        with col2:
            # Cálculo automático: Hoje + Prazo da Planilha
            prazo_sugerido = date.today() + timedelta(days=regra['prazo'])
            prazo_final = st.date_input("Prazo Final (Sugerido)", value=prazo_sugerido)

        notas = st.text_area("Observações (Ex: Nº do Processo SEI)", placeholder="00000.000000/2026-00")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.form_submit_button("Cancelar", use_container_width=True):
                ao_cancelar()
        
        with col_btn2:
            if st.form_submit_button("Registrar Tarefa", type="primary", use_container_width=True):
                dados = {
                    "titulo": categoria,
                    "categoria": categoria,
                    "pontuacao": pontos,
                    "prazo": prazo_final.isoformat(),
                    "notas": notas,
                    "status": "pendente"
                }
                ao_salvar(dados)