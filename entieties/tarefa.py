import pandas as pd
from datetime import date, datetime

def criar_estrutura_tarefa():
    """
    Define as colunas e os valores permitidos para as tarefas,
    exatamente como nos seus prints, mas em Português.
    """
    
    # 1. Definição das Opções
    opcoes = {
        "status": ["pendente", "em_andamento", "concluida", "cancelada"],
        "prioridade": ["baixa", "media", "alta", "urgente"],
        "categoria": ["desenvolvimento", "reuniao", "documentacao", "pesquisa", "comunicacao", "outro"]
    }

    # 2. Estrutura das Colunas 
    colunas = [
        "titulo", "descricao", "status", "prioridade", "categoria",
        "pontuacao", "prazo_em_dias", "minutos_estimados", "minutos_reais",
        "data_entrega", "data_conclusao"
    ]
    
    return colunas, opcoes

def nova_tarefa_vazia():
    """Retorna um DataFrame do Pandas pronto para receber dados"""
    colunas, _ = criar_estrutura_tarefa()
    return pd.DataFrame(columns=colunas)

# Exemplo de como uma tarefa seria montada internamente:
def mapear_tarefa(dados):
    """
    Garante que os nomes sigam o padrão
    """
    tarefa = {
        "titulo": dados.get("title", ""),
        "descricao": dados.get("description", ""),
        "status": dados.get("status", "pendente"),
        "prioridade": dados.get("priority", "media"),
        "categoria": dados.get("category", "outro"),
        "pontuacao": dados.get("score", 0),
        "prazo_em_dias": dados.get("deadline_days", 0),
        "minutos_estimados": dados.get("estimated_minutes", 0),
        "minutos_reais": dados.get("actual_minutes", 0),
        "data_entrega": dados.get("due_date", None),
        "data_conclusao": dados.get("completed_date", None)
    }
    return tarefa