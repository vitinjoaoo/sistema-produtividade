import streamlit as st
import pandas as pd
from datetime import date, timedelta

def renderizar_grafico_semanal(df_worklogs):
    """
    Traduz o WeeklyChart.jsx para Python.
    Gera um gráfico de barras das horas trabalhadas nos últimos 7 dias.
    """
    st.markdown("### 📊 Horas Trabalhadas (Última Semana)")

    # 1. Configuração dos dias (Linhas 5 a 6 do seu print)
    dias_semana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
    hoje = date.today()
    
    # 2. Lógica para montar os dados dos últimos 7 dias (Linhas 8 a 17)
    dados_grafico = []
    
    for i in range(6, -1, -1):  # De 6 dias atrás até hoje
        data_alvo = hoje - timedelta(days=i)
        data_str = data_alvo.isoformat()
        
        # Procura o log no DataFrame (Equivalente ao .find da linha 12)
        if not df_worklogs.empty and 'data' in df_worklogs.columns:
            log_dia = df_worklogs[df_worklogs['data'] == data_str]
        else:
            log_dia = pd.DataFrame()

        # Converte minutos para horas (Linha 15: / 60)
        if not log_dia.empty:
            minutos = log_dia.iloc[0]['total_minutos']
            horas = round(minutos / 60, 1)
        else:
            horas = 0.0
            
        dados_grafico.append({
            "Dia": dias_semana[data_alvo.weekday()], # Pega o nome do dia (Linha 14)
            "Horas": horas
        })

    # 3. Transforma em DataFrame para o Streamlit ler
    df_plot = pd.DataFrame(dados_grafico)

    # 4. Renderização do Gráfico de Barras (Linhas 23 a 39)
    # O bar_chart do Streamlit é simples e limpo como o Recharts
    st.bar_chart(
        df_plot, 
        x="Dia", 
        y="Horas", 
        color="#3b82f6", # Cor azul primária do seu código original
        use_container_width=True
    )

    st.caption("Eixo Y: Horas trabalhadas por dia")