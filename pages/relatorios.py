import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import io
from datetime import datetime, date
from fpdf import FPDF 
from src.styles.custom_css import estilo 
from src.components.layout.menu_lateral import renderizar_sidebar

# 1. CONFIGURAÇÕES DE AMBIENTE E UI
st.set_page_config(page_title="Relatórios Estratégicos", layout="wide")
estilo() 
renderizar_sidebar()

# --- MÓDULO DE GERAÇÃO DE DOCUMENTOS (Interoperabilidade PDF) ---
def gerar_pdf(df, usuario, total_pts, meta_valor):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Relatorio de Produtividade Individual", ln=True, align="C")
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 10, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
    
    user_name = str(usuario).encode('ascii', 'ignore').decode('ascii')
    pdf.cell(190, 10, f"Responsavel: {user_name}", ln=True)
    pdf.cell(190, 10, f"Meta Institutional: {meta_valor} pontos", ln=True)
    pdf.cell(190, 10, f"Total alcancado: {total_pts} pontos", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 8)
    pdf.set_fill_color(200, 220, 255) 
    pdf.cell(35, 10, "Conclusao", border=1, fill=True) 
    pdf.cell(35, 10, "Num. Processo", border=1, fill=True)
    pdf.cell(55, 10, "Atividade", border=1, fill=True)
    pdf.cell(15, 10, "Pts", border=1, fill=True)
    pdf.cell(50, 10, "Observacoes", border=1, fill=True)
    pdf.ln()
    
    pdf.set_font("Arial", "", 7)
    for index, row in df.iterrows():
        data_text = str(row['Conclusão']).encode('latin-1', 'ignore').decode('latin-1')
        proc_text = str(row['Nº Processo']).encode('latin-1', 'ignore').decode('latin-1')
        ativid_text = str(row['Atividade'])[:30].encode('latin-1', 'ignore').decode('latin-1')
        obs_text = str(row['Observação'] if row['Observação'] else "-")[:40].encode('latin-1', 'ignore').decode('latin-1')
        
        pdf.cell(35, 8, data_text, border=1)
        pdf.cell(35, 8, proc_text, border=1)
        pdf.cell(55, 8, ativid_text, border=1)
        pdf.cell(15, 8, str(row['Pontos']), border=1)
        pdf.cell(50, 8, obs_text, border=1)
        pdf.ln()
        
    # --- CORREÇÃO DO ERRO AQUI ---
    # Extrai o buffer de bytes brutos de forma segura independente da versão da biblioteca
    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, str):
        return pdf_output.encode('latin-1', errors='replace')
    return bytes(pdf_output)

def renderizar_pagina_relatorios():
    if 'usuario_nome' not in st.session_state:
        st.error("Acesso negado. Por favor, realize o login.")
        return

    usuario_atual = st.session_state['usuario_nome']
    perfil_atual = st.session_state.get('usuario_perfil', 'Colaborador')
    is_admin = "Administrador" in perfil_atual

    METAS = {
        "Servidor Integral": 88, "Servidor Híbrido": 84, "Servidor Presencial": 80,
        "Colaborador Presencial": 80, "Administrador Presencial": 80
    }

    st.title("📈 Relatórios de Produtividade")
    
    conn = sqlite3.connect('produtividade.db')
    if is_admin:
        df_base = pd.read_sql_query("SELECT * FROM tarefas WHERE status = 'CONCLUÍDO'", conn)
        df_perfis = pd.read_sql_query("SELECT nome, perfil FROM usuarios", conn)
    else:
        df_base = pd.read_sql_query(f"SELECT * FROM tarefas WHERE status = 'CONCLUÍDO' AND usuario_id = '{usuario_atual}'", conn)
    conn.close()

    with st.expander("🔍 Filtros de Auditoria e Seleção Temporal", expanded=True):
        c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
        with c1:
            data_inicio = st.date_input("Início do Período", value=date(2026, 1, 1), format="DD/MM/YYYY")
        with c2:
            data_fim = st.date_input("Fim do Período", value=date.today(), format="DD/MM/YYYY")
        with c3:
            if is_admin:
                lista_funcs = ["Todos"] + sorted(df_base['usuario_id'].unique().tolist())
                filtro_user = st.selectbox("Colaborador", lista_funcs)
            else:
                filtro_user = usuario_atual
                st.info(f"Usuário: {usuario_atual}")
        with c4:
            filtro_proc = st.text_input("Localizar Nº Processo", placeholder="00000000/0000")

    df_filtrado = df_base.copy()
    
    if is_admin and filtro_user != "Todos":
        df_filtrado = df_filtrado[df_filtrado['usuario_id'] == filtro_user]
    
    if filtro_proc:
        df_filtrado = df_filtrado[df_filtrado['num_processo'].str.contains(filtro_proc, na=False)]
    
    if 'data_conclusao' in df_filtrado.columns and not df_filtrado.empty:
        df_filtrado['data_conclusao_dt'] = pd.to_datetime(df_filtrado['data_conclusao']).dt.date
        df_filtrado = df_filtrado[(df_filtrado['data_conclusao_dt'] >= data_inicio) & (df_filtrado['data_conclusao_dt'] <= data_fim)]

    if not is_admin or (is_admin and filtro_user != "Todos"):
        p_ref = perfil_atual if not is_admin else df_perfis[df_perfis['nome'] == filtro_user]['perfil'].values[0]
        meta_valor = METAS.get(p_ref, 80)
    else:
        meta_valor = 80 

    total_pts = df_filtrado['pontos'].sum() if not df_filtrado.empty else 0
    total_procs = len(df_filtrado)
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">🏆 TOTAL DE PONTOS</div><div class="metric-value">{total_pts}</div></div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">📄 PROCESSOS CONCLUÍDOS</div><div class="metric-value">{total_procs}</div></div>', unsafe_allow_html=True)
    with col_m3:
        atingimento = min((total_pts / meta_valor) * 100, 100.0) if meta_valor > 0 else 0
        st.markdown(f'<div class="metric-card"><div class="metric-title">🎯 ATINGIMENTO META</div><div class="metric-value">{atingimento:.1f}%</div></div>', unsafe_allow_html=True)

    st.write("---")

    tab_graf, tab_detalhes = st.tabs(["📊 Gráficos de BI", "📋 Tabela de Auditoria"])

    with tab_graf:
        if not df_filtrado.empty:
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                fig_pie = px.pie(df_filtrado, names='titulo', values='pontos', hole=0.4, title="Distribuição de Pontos")
                st.plotly_chart(fig_pie, use_container_width=True)
            with c_g2:
                df_meta = pd.DataFrame({'Categoria': ['Realizado', 'Meta'], 'Pontos': [total_pts, meta_valor]})
                fig_meta = px.bar(df_meta, x='Categoria', y='Pontos', color='Categoria', title="Produtividade vs Meta")
                st.plotly_chart(fig_meta, use_container_width=True)
        else:
            st.info("Aguardando dados para geração de gráficos.")

    with tab_detalhes:
        if not df_filtrado.empty:
            df_filtrado['data_formatada'] = pd.to_datetime(df_filtrado['data_conclusao']).dt.strftime('%d/%m/%Y')
            
            df_exibicao = df_filtrado[['data_formatada', 'num_processo', 'titulo', 'pontos', 'usuario_id', 'observacao']].copy()
            df_exibicao.columns = ['Conclusão', 'Nº Processo', 'Atividade', 'Pontos', 'Responsável', 'Observação']
            
            st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
            
            col_exp1, col_exp2 = st.columns(2)
            data_hoje_br = date.today().strftime('%d-%m-%Y')
            
            with col_exp1:
                output_excel = io.BytesIO()
                with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                    df_exibicao.to_excel(writer, index=False, sheet_name='Auditoria')
                st.download_button(label="📥 Baixar Excel", data=output_excel.getvalue(), 
                                   file_name=f"auditoria_{filtro_user}_{data_hoje_br}.xlsx", use_container_width=True)
            
            with col_exp2:
                try:
                    pdf_data = gerar_pdf(df_exibicao, filtro_user, total_pts, meta_valor)
                    st.download_button(label="📄 Baixar Relatório PDF", data=pdf_data, 
                                       file_name=f"relatorio_{filtro_user}_{data_hoje_br}.pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"Erro na geração do PDF: {e}")
        else:
            st.warning("Sem dados para exportação.")

if __name__ == "__main__":
    renderizar_pagina_relatorios()