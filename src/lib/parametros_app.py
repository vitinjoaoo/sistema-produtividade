import streamlit as st
import re

def para_snake_case(texto):
    """Traduz toSnakeCase (Linha 5)"""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', texto).lower()

def obter_valor_parametro(nome_param, valor_padrao=None):
    """
    Traduz getAppParamValue (Linha 9).
    Busca primeiro na URL do navegador, depois nos segredos do sistema.
    """
    # 1. Tenta buscar na URL (Equivalente ao URLSearchParams da linha 14)
    parametros_url = st.query_params
    if nome_param in parametros_url:
        return parametros_url[nome_param]
    
    # 2. Se não estiver na URL, busca nos Secrets ou retorna o padrão
    # (Equivalente ao import.meta.env das linhas 43-47)
    return st.secrets.get(nome_param.upper(), valor_padrao)

def obter_parametros_app():
    """
    Traduz getAppParams (Linha 37).
    Monta o dicionário final de configuração.
    """
    return {
        "appId": obter_valor_parametro("app_id", "ID_PADRAO"),
        "token": obter_valor_parametro("access_token"),
        "origem_url": obter_valor_parametro("from_url"),
        "versao_funcoes": obter_valor_parametro("functions_version", "1.0.0"),
        "url_base_app": obter_valor_parametro("app_base_url", "http://localhost:8501")
    }

# Exporta a variável para ser usada no projeto todo (Linha 52)
parametros_app = obter_parametros_app()