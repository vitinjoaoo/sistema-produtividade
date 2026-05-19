# Tabela de Produtividade baseada na sua planilha Excel
TABELA_PRODUTIVIDADE = {
    "Colaborador/Auxiliar na Pesquisa de preços – Dispensa de Licitação": {"pontos": 1.0, "prazo": 15},
    "Colaborador/Auxiliar na Pesquisa de preços – Licitação - 1 a 10 itens": {"pontos": 1.0, "prazo": 20},
    "Colaborador/Auxiliar na Pesquisa de preços – Licitação - De 10 a 20 itens": {"pontos": 2.0, "prazo": 20},
    "Servidor/Pesquisa de preços – Dispensa de Licitação (TODOS OS PROCEDIMENTOS)": {"pontos": 4.0, "prazo": 15},
    "Servidor/Contratação de tradutor juramentado": {"pontos": 4.0, "prazo": 60},
    "Servidor/Concessão e Prestação de Contas Suprimento de Fundos (CARTAO)": {"pontos": 3.0, "prazo": 60},
    "Participação em reuniões": {"pontos": 1.0, "prazo": 1},
}

def obter_opcoes_tarefas():
    return list(TABELA_PRODUTIVIDADE.keys())