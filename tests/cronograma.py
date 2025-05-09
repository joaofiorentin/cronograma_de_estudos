import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ====== CONFIGURAÇÕES ======
st.set_page_config(page_title="Cronograma de Estudos", layout="centered")
st.markdown("<h1 style='text-align: center;'>Cronograma de estudos</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Disciplina é liberdade. Organização é poder.</p>", unsafe_allow_html=True)

# ====== ARQUIVO PARA SALVAR ======
ARQUIVO = "cronograma.csv"

# ====== DADOS INICIAIS ======
dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado/Domingo']
atividades = {
    'Segunda': 'Python - Funções Matemáticas (Cálculo, Derivadas, Integrais)',
    'Terça': 'Python - Vetores e Matrizes (Álgebra Linear)',
    'Quarta': 'Python - Distribuições Estatísticas (Normal, Binomial, etc.)',
    'Quinta': 'Python - Estatísticas Descritivas (Média, Desvio Padrão, etc.)',
    'Sexta': 'Revisão e Prática (Consolidação de conceitos)',
    'Sábado/Domingo': 'Projeto prático com Dados Reais (Análise e Automação)'
}

# ====== FUNÇÃO: CRIAR CRONOGRAMA PADRÃO ======
def criar_cronograma():
    semanas = []
    for semana in range(1, 5):
        for dia in dias_semana:
            semanas.append({
                'Semana': f'Semana {semana}',
                'Dia': dia,
                'Atividade': atividades[dia],
                'Status': 'Pendente'
            })
    return pd.DataFrame(semanas)

# ====== CARREGAR OU CRIAR ARQUIVO ======
if os.path.exists(ARQUIVO):
    df_cronograma = pd.read_csv(ARQUIVO)
else:
    df_cronograma = criar_cronograma()

# ====== MENU ======
aba1, aba2, aba3 = st.tabs(["📅 Cronograma", "✅ Progresso", "📊 Gráficos"])

# ====== ABA 1: CRONOGRAMA ======
with aba1:
    st.subheader("Cronograma semanal")
    st.dataframe(df_cronograma, use_container_width=True)

# ====== ABA 2: PROGRESSO ======
with aba2:
    st.subheader("Atualizar status")
    for i in range(len(df_cronograma)):
        atividade = df_cronograma.iloc[i]
        status = st.radio(
            f"{atividade['Semana']} - {atividade['Dia']}: {atividade['Atividade']}",
            ('Pendente', 'Concluído'),
            index=0 if atividade['Status'] == 'Pendente' else 1,
            key=f"{i}"
        )
        df_cronograma.loc[i, 'Status'] = status

    if st.button("💾 Salvar Alterações"):
        df_cronograma.to_csv(ARQUIVO, index=False)
        st.success("Progresso salvo com sucesso!")

# ====== ABA 3: GRÁFICOS ======
with aba3:
    st.subheader("Progresso por semana")

    progresso = df_cronograma['Status'].apply(lambda x: 1 if x == 'Concluído' else 0)
    progresso_por_semana = progresso.groupby(df_cronograma['Semana']).sum().reset_index()
    progresso_por_semana.columns = ['Semana', 'Tarefas Concluídas']

    fig_linha = px.line(
        progresso_por_semana,
        x='Semana',
        y='Tarefas Concluídas',
        markers=True,
        title="Evolução das tarefas concluídas por semana",
        line_shape="linear"
    )
    fig_linha.update_layout(xaxis_title="Semana", yaxis_title="Concluídas", title_x=0.5)
    st.plotly_chart(fig_linha, use_container_width=True)

    # Gráfico de Pizza
    total_concluidas = progresso.sum()
    total_pendentes = len(df_cronograma) - total_concluidas

    fig_pizza = go.Figure(data=[go.Pie(
        labels=['Concluídas', 'Pendentes'],
        values=[total_concluidas, total_pendentes],
        hole=0.4,
        marker=dict(colors=['#2ecc71', '#e74c3c']),
        textinfo='label+percent'
    )])
    fig_pizza.update_layout(title_text='Distribuição geral do progresso', title_x=0.5)
    st.plotly_chart(fig_pizza, use_container_width=True)

    # Barra de Progresso Geral
    percentual = (total_concluidas / len(df_cronograma)) * 100
    st.subheader("Progresso geral")
    st.metric("Tarefas concluídas", f"{percentual:.1f}%", delta=f"{total_concluidas}/{len(df_cronograma)}")
    st.progress(percentual / 100)
