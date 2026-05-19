import re
import unicodedata

def criar_url_pagina(nome_pagina: str) -> str:
    """
    Traduz createPageUrl (do seu código TS).
    Transforma "Registro de Trabalho" em "/registro-de-trabalho".
    """
    # Remove acentos para garantir URLs limpas
    nfkd_form = unicodedata.normalize('NFKD', nome_pagina)
    nome_sem_acento = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    # Substitui espaços por hífens e coloca em minúsculo
    url = nome_sem_acento.replace(" ", "-").lower()
    
    return f"/{url}"

def formatar_minutos_para_horas(minutos: int) -> str:
    """Função utilitária extra para facilitar nos seus relatórios"""
    horas = minutos // 60
    restante = minutos % 60
    return f"{horas:02d}:{restante:02d}h"