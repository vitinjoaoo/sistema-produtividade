import streamlit as st
import sqlite3
import pandas as pd
import re
from datetime import datetime, date, timedelta
from src.styles.custom_css import estilo 
from src.components.layout.menu_lateral import renderizar_sidebar

# 1. INICIALIZAÇÃO DE INTERFACE
estilo() 
renderizar_sidebar()

# --- CATÁLOGO DE REGRAS DE NEGÓCIO ---
DEMANDAS = [
    {"tarefa": "Colaborador/Auxiliar na Pesquisa de preços – Dispensa", "pontos": 1, "prazo": 15},
    {"tarefa": "Colaborador/Auxiliar na Pesquisa de preços – Licitação (1-10 itens)", "pontos": 1, "prazo": 20},
    {"tarefa": "Colaborador/Auxiliar na Pesquisa de preços – Licitação (10-20 itens)", "pontos": 2, "prazo": 20},
    {"tarefa": "Colaborador/Auxiliar na Pesquisa de preços – Licitação (+20 itens)", "pontos": 3, "prazo": 20},
    {"tarefa": "Servidor/Pesquisa de preços – Dispensa (Até final)", "pontos": 4, "prazo": 15},
    {"tarefa": "Servidor/Pesquisa de preços – Licitação 1-10 itens", "pontos": 4, "prazo": 20},
    {"tarefa": "Servidor/Pesquisa de preços – Licitação 11-20 itens", "pontos": 6, "prazo": 20},
    {"tarefa": "Servidor/Pesquisa de preços – Licitação +20 itens", "pontos": 8, "prazo": 20},
    {"tarefa": "Servidor/Contratação de tradutor juramentado", "pontos": 4, "prazo": 60},
    {"tarefa": "Servidor/Concessão e Prestação de Contas (CARTÃO)", "pontos": 3, "prazo": 60},
    {"tarefa": "Participação em reuniões", "pontos": 1, "prazo": 1},
    {"tarefa": "Servidor/Adesão e Execução de Atas de Registro de Preços", "pontos": 4, "prazo": 5}
]

def calcular_data_util(data_inicial, dias_uteis):
    data_final = data_inicial
    while dias_uteis > 0:
        data_final += timedelta(days=1)
        if data_final.weekday() < 5: 
            dias_uteis -= 1
    return data_final

def renderizar_tarefas():
    conn = sqlite3.connect('produtividade.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tarefas 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   titulo TEXT, pontos INTEGER, status TEXT, usuario_id TEXT, 
                   num_processo TEXT, data_atribuicao TEXT, data_esperada TEXT, 
                   data_conclusao TEXT, observacao TEXT)''')
    try:
        c.execute("ALTER TABLE tarefas ADD COLUMN observacao TEXT")
    except:
        pass 
    conn.commit()
    conn.close()

    if 'usuario_nome' not in st.session_state:
        st.warning("Por favor, faça login no Painel Principal primeiro.")
        return

    usuario_atual = st.session_state['usuario_nome']
    perfil_atual = st.session_state.get('usuario_perfil', 'Colaborador')
    is_admin = "Administrador" in perfil_atual

    st.title("📝 Gestão de Demandas")

    # --- MÓDULO DE DELEGAÇÃO (Exclusivo para Gestores) ---
    if is_admin:
        st.markdown("### ⚖️ Delegar Novas Demandas")
        with st.expander("Formulário de Delegação", expanded=True):
            conn = sqlite3.connect('produtividade.db')
            df_users = pd.read_sql_query("SELECT nome FROM usuarios WHERE perfil NOT LIKE '%Administrador%'", conn)
            conn.close()
            
            col_task, col_proc, col_user, col_date = st.columns([3, 2, 2, 2])
            with col_task:
                tarefa_sel = st.selectbox("Tarefa", [d['tarefa'] for d in DEMANDAS])
            with col_proc:
                num_proc_input = st.text_input("Nº Processo", placeholder="00000000/0000", max_chars=13)
            with col_user:
                colaborador_sel = st.selectbox("Atribuir para", df_users['nome'].tolist() if not df_users.empty else ["Nenhum"])
            with col_date:
                prazo_dias = next(d['prazo'] for d in DEMANDAS if d['tarefa'] == tarefa_sel)
                data_sugerida = calcular_data_util(date.today(), prazo_dias)
                data_entrega = st.date_input("Prazo de Conclusão", value=data_sugerida, format="DD/MM/YYYY")
            
            obs_inicial = st.text_area("Instruções ao Servidor", placeholder="Digite orientações extras...")

            if st.button("Delegar Tarefa 🚀") and colaborador_sel != "Nenhum":
                if re.match(r"^\d{8}/\d{4}$", num_proc_input):
                    pontos = next(d['pontos'] for d in DEMANDAS if d['tarefa'] == tarefa_sel)
                    hoje = date.today().strftime('%Y-%m-%d')
                    prazo_str = data_entrega.strftime('%Y-%m-%d')
                    
                    conn = sqlite3.connect('produtividade.db')
                    c = conn.cursor()
                    c.execute("""INSERT INTO tarefas (titulo, pontos, status, usuario_id, num_processo, data_atribuicao, data_esperada, observacao) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                              (tarefa_sel, pontos, "PENDENTE", colaborador_sel, num_proc_input, hoje, prazo_str, obs_inicial))
                    conn.commit()
                    conn.close()
                    
                    # AVISO DE SUCESSO PERSISTENTE
                    st.success(f"✅ Tarefa delegada com sucesso para {colaborador_sel}!")
                else:
                    st.error("❌ Formato de processo inválido.")

    st.write("---")
    
    st.markdown("### 🕒 Mural de Acompanhamento")
    
    conn = sqlite3.connect('produtividade.db')
    query = "SELECT * FROM tarefas" if is_admin else f"SELECT * FROM tarefas WHERE usuario_id = '{usuario_atual}'"
    df_mural = pd.read_sql_query(query, conn)
    conn.close()

    if not df_mural.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            if is_admin:
                opcoes_nome = ["Todos"] + sorted(df_mural['usuario_id'].unique().tolist())
                filtro_nome = st.selectbox("Filtrar por Executor", opcoes_nome)
            else:
                filtro_nome = "Todos"
        with col_f2:
            opcoes_situacao = ["Todos", "Atrasada", "Vence Hoje", "No Prazo", "Concluída"]
            filtro_situacao = st.selectbox("Filtrar por Situação", opcoes_situacao)

        data_hoje = date.today()
        def definir_situacao(row):
            if row['status'] == 'CONCLUÍDO': return "Concluída"
            dt_limite = datetime.strptime(row['data_esperada'], '%Y-%m-%d').date()
            atraso = (data_hoje - dt_limite).days
            if atraso > 0: return "Atrasada"
            if atraso == 0: return "Vence Hoje"
            return "No Prazo"

        df_mural['situacao_real'] = df_mural.apply(definir_situacao, axis=1)

        if filtro_nome != "Todos":
            df_mural = df_mural[df_mural['usuario_id'] == filtro_nome]
        if filtro_situacao != "Todos":
            df_mural = df_mural[df_mural['situacao_real'] == filtro_situacao]

        if df_mural.empty:
            st.info("Nenhuma demanda encontrada.")
        else:
            for _, row in df_mural.sort_values(by='id', ascending=False).iterrows():
                situacao = row['situacao_real']
                dt_atrib_br = datetime.strptime(row['data_atribuicao'], '%Y-%m-%d').strftime('%d/%m/%Y')
                dt_esp_br = datetime.strptime(row['data_esperada'], '%Y-%m-%d').strftime('%d/%m/%Y')
                dt_limite = datetime.strptime(row['data_esperada'], '%Y-%m-%d').date()
                
                if situacao == "Concluída":
                    icon, status_txt, cor_borda = "✔️", "Concluída", "#2EB086"
                elif situacao == "Atrasada":
                    atraso = (data_hoje - dt_limite).days
                    icon, status_txt, cor_borda = "🚨", f"Atrasada ({atraso} dias)", "#FF4B4B"
                elif situacao == "Vence Hoje":
                    icon, status_txt, cor_borda = "⚠️", "Vence Hoje", "#FFA500"
                else:
                    faltam = (dt_limite - data_hoje).days
                    icon, status_txt, cor_borda = "⏳", f"No Prazo (Faltam {faltam} dias)", "#5D78FF"

                with st.container():
                    st.markdown(f"""
                        <div style="border-left: 6px solid {cor_borda}; padding: 15px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                            <div style="display: flex; justify-content: space-between;">
                                <span><b>{icon} {row['titulo']}</b></span>
                                <span style="color: {cor_borda}; font-weight: bold;">{status_txt}</span>
                            </div>
                            <div style="font-size: 0.85rem; color: #666; margin-top: 5px;">
                                📄 Processo: {row['num_processo']} | 👤 Executor: {row['usuario_id']} | 🏆 Pontos: {row['pontos']}<br>
                                📅 Delegação: {dt_atrib_br} | 🏁 Prazo Final: {dt_esp_br}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander(f"💬 Notas e Gestão", expanded=False):
                        obs_atual = row['observacao'] if row['observacao'] else ""
                        nova_obs = st.text_area("Notas / Dúvidas:", value=obs_atual, key=f"obs_input_{row['id']}")
                        
                        c_btns1, c_btns2, c_btns3 = st.columns([1,1,1])
                        with c_btns1:
                            if st.button("Salvar Nota 💾", key=f"save_obs_{row['id']}"):
                                conn = sqlite3.connect('produtividade.db')
                                c = conn.cursor()
                                c.execute("UPDATE tarefas SET observacao = ? WHERE id = ?", (nova_obs, row['id']))
                                conn.commit()
                                conn.close()
                                st.success("Nota salva!")
                                st.rerun()
                        
                        with c_btns2:
                            if row['status'] == 'PENDENTE' and row['usuario_id'] == usuario_atual:
                                if st.button("Concluir ✅", key=f"btn_done_{row['id']}"):
                                    conn = sqlite3.connect('produtividade.db')
                                    c = conn.cursor()
                                    c.execute("UPDATE tarefas SET status = 'CONCLUÍDO', data_conclusao = ? WHERE id = ?", 
                                              (date.today().strftime('%Y-%m-%d'), row['id']))
                                    conn.commit()
                                    conn.close()
                                    st.rerun()

                        #EXCLUIR DELEGAÇÃO (Exclusivo Admin)
                        with c_btns3:
                            if is_admin:
                                if st.button("Excluir 🗑️", key=f"del_task_{row['id']}"):
                                    conn = sqlite3.connect('produtividade.db')
                                    c = conn.cursor()
                                    c.execute("DELETE FROM tarefas WHERE id = ?", (row['id'],))
                                    conn.commit()
                                    conn.close()
                                    st.warning("Delegação removida.")
                                    st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Nenhuma demanda registrada.")

if __name__ == "__main__":
    renderizar_tarefas()