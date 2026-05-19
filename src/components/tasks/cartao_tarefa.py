import streamlit as st
import pandas as pd
from datetime import datetime

def renderizar_cartao_tarefa(tarefa, ao_editar, ao_excluir, ao_mudar_status):
    """
    Traduz o TaskCard.jsx para Streamlit.
    Mostra todos os detalhes da tarefa e oferece botões de ação.
    """
    
    # 1. Mapeamento de Rótulos e Cores (Linhas 9 a 13 do seu print)
    status_labels = {'pendente': 'Pendente', 'em_andamento': 'Em Andamento', 'concluida': 'Concluída', 'cancelada': 'Cancelada'}
    prioridade_labels = {'baixa': 'Baixa', 'media': 'Média', 'alta': 'Alta', 'urgente': 'Urgente'}
    categoria_labels = {'desenvolvimento': 'Dev', 'reuniao': 'Reunião', 'documentacao': 'Doc', 'pesquisa': 'Pesquisa', 'comunicacao': 'Comunicação', 'outro': 'Outro'}

    # Container principal (Simula o bg-card rounded-xl border p-4)
    with st.container(border=True):
        # Cabeçalho: Título e Menu de Ações (Linhas 18 a 50)
        col_txt, col_acoes = st.columns([4, 1])
        
        with col_txt:
            titulo = tarefa.get('titulo', 'Sem título')
            # Lógica de riscado se concluída (Linha 20)
            if tarefa.get('status') == 'concluida':
                st.markdown(f"### ~~{titulo}~~")
            else:
                st.markdown(f"### {titulo}")
            
            # Descrição (Linhas 23-25)
            if tarefa.get('descricao'):
                st.caption(tarefa['descricao'])

        with col_acoes:
            # No Streamlit, usamos um popover para simular o DropdownMenu (Linha 27)
            with st.popover("⚙️"):
                if st.button("📝 Editar", key=f"ed_{tarefa['id']}"):
                    ao_editar(tarefa)
                
                # Botões de mudança de status (Linhas 37-46)
                if tarefa['status'] != 'em_andamento':
                    if st.button("🚀 Iniciar", key=f"st_and_{tarefa['id']}"):
                        ao_mudar_status(tarefa, 'em_andamento')
                
                if tarefa['status'] != 'concluida':
                    if st.button("✅ Concluir", key=f"st_con_{tarefa['id']}"):
                        ao_mudar_status(tarefa, 'concluida')
                
                if st.button("🗑️ Excluir", key=f"exc_{tarefa['id']}", type="primary"):
                    ao_excluir(tarefa)

        # 2. Badges e Infos (Linhas 53 a 80)
        st.write("")
        c1, c2, c3, c4 = st.columns(4)
        
        # Badge de Status (Linha 55)
        st_label = status_labels.get(tarefa['status'], 'Pendente')
        c1.help(f"Status: {st_label}")
        c1.markdown(f"**{st_label}**")

        # Badge de Prioridade (Linha 58)
        prio_label = prioridade_labels.get(tarefa['prioridade'], 'Média')
        c2.markdown(f"Prio: **{prio_label}**")

        # Data de Entrega (Linhas 64-68)
        if tarefa.get('data_entrega'):
            dt = tarefa['data_entrega']
            c3.markdown(f"📅 {dt}")

        # Pontuação (Linhas 74-77)
        if tarefa.get('pontuacao') is not None:
            c4.markdown(f"⭐ **{tarefa['pontuacao']}** pts")

        # Minutos Estimados (Linha 79)
        if tarefa.get('minutos_estimados'):
            st.markdown(f"⏱️ Estimado: `{tarefa['minutos_estimados']}min`")