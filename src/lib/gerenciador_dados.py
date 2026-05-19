import streamlit as st

# No seu print (linhas 7-8), você configurou:
# refetchOnWindowFocus: false -> Não recarregar quando mudar de aba
# retry: 1 -> Se der erro na rede, tenta mais 1 vez

def configurar_cache(funcao):
    """
    Simula o comportamento do QueryClient do seu print.
    Usa o sistema de cache do Streamlit para otimizar o desempenho.
    """
    # ttl=600 significa que o dado fica guardado por 10 minutos (600 segundos)
    # show_spinner=False evita que fique aparecendo "Loading" toda hora (refetchOnWindowFocus: false)
    return st.cache_data(ttl=600, show_spinner=False)(funcao)

# Exemplo de como você usará isso nas suas páginas (Tasks, Dashboard, etc):
@configurar_cache
def buscar_dados_do_banco():
    """
    Aqui é onde a chamada real para o seu banco de dados aconteceria.
    O Streamlit vai lembrar o resultado e não vai rodar a função de novo 
    até que o tempo de cache expire.
    """
    # Simula o 'retry: 1'
    try:
        # Lógica de busca
        return {"status": "sucesso", "dados": []}
    except Exception:
        # Tenta de novo se falhar uma vez
        return {"status": "erro", "mensagem": "Falha na conexão"}