import streamlit as st
import pandas as pd

def renderizar_tarefas_recentes(tarefas):
    """
    Exibe a lista de tarefas recentes com cores de prioridade.
    """
    st.write("### 🕒 Tarefas Recentes")
    
    # Dicionário que estava faltando (Causa do seu NameError)
    priority_colors = {
        'baixa': '🔵 Baixa',
        'media': '🟡 Média',
        'alta': '🟠 Alta',
        'urgente': '🔴 Urgente'
    }

    if not tarefas:
        st.info("Nenhuma tarefa recente encontrada.")
        return

    # Criamos um container com borda para a lista
    with st.container(border=True):
        # Cabeçalho da tabela simples
        col_tit, col_prio, col_status = st.columns([3, 1, 1])
        col_tit.caption("TÍTULO")
        col_prio.caption("PRIORIDADE")
        col_status.caption("STATUS")
        
        st.divider()

        # Listamos as tarefas
        for tarefa in tarefas[:5]:  # Mostra apenas as 5 últimas
            c_t, c_p, c_s = st.columns([3, 1, 1])
            
            # Título
            c_t.write(tarefa.get('titulo', 'Sem título'))
            
            # Prioridade com cor
            prio = tarefa.get('prioridade', 'media')
            c_p.write(priority_colors.get(prio, '⚪ Desconhecida'))
            
            # Status
            status = tarefa.get('status', 'pendente').replace('_', ' ').title()
            c_s.write(f"`{status}`")
            st.markdown("---")