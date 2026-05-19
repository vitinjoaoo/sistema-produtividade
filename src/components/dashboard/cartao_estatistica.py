import streamlit as st

def renderizar_cartao_estatistica(titulo, valor, subtitulo=None, tendencia=None):
    """
    Traduz o StatCard.jsx para o Streamlit.
    Mostra um valor principal, um subtítulo e a variação percentual (tendência).
    """
    
    # No seu código original (linhas 22 a 28), o 'trend' define a cor.
    # O Streamlit faz isso automaticamente se passarmos o valor no parâmetro 'delta'.
    
    delta_label = None
    if tendencia is not None:
        # Formata o texto da tendência (ex: "↑ 10% vs semana anterior")
        seta = "↑" if tendencia > 0 else "↓"
        delta_label = f"{seta} {abs(tendencia)}% vs semana anterior"

    # Criamos o container visual (simula o bg-card rounded-2xl do print)
    with st.container():
        st.markdown(f"**{titulo.upper()}**") # Título em caixa alta (linha 12)
        
        # O componente metric do Streamlit lida com o valor e a tendência
        st.metric(
            label=subtitulo if subtitulo else "", 
            value=valor, 
            delta=delta_label,
            delta_color="normal" # Verde para positivo, Vermelho para negativo
        )
        
    st.markdown("---") # Divisor para separar os cartões