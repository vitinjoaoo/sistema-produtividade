import pandas as pd
from datetime import date

def criar_estrutura_registro():
    """
    Define a estrutura para o log de trabalho diário.
    Traduzido do esquema WorkLog original.
    """
    
    # 1. Opções de Humor 
    opcoes_humor = ["otimo", "bom", "regular", "ruim"]

    # 2. Colunas do Registro 
    colunas = [
        "data",                # date
        "hora_inicio",         # start_time
        "hora_fim",            # end_time
        "minutos_pausa",       # break_minutes
        "total_minutos",       # total_minutes
        "tarefas_concluidas",  # tasks_completed
        "humor",               # mood
        "observacoes"          # notes
    ]
    
    return colunas, opcoes_humor

def novo_registro_vazio():
    """Cria um DataFrame do Pandas para armazenar os logs do dia"""
    colunas, _ = criar_estrutura_registro()
    return pd.DataFrame(columns=colunas)

def mapear_registro(dados):
    """
    Transforma os dados brutos no formato de Registro de Trabalho.
    """
    registro = {
        "data": dados.get("date", date.today()),
        "hora_inicio": dados.get("start_time", "09:00"),
        "hora_fim": dados.get("end_time", "18:00"),
        "minutos_pausa": dados.get("break_minutes", 0),
        "total_minutos": dados.get("total_minutes", 0),
        "tarefas_concluidas": dados.get("tasks_completed", 0),
        "humor": dados.get("mood", "bom"),
        "observacoes": dados.get("notes", "")
    }
    return registro