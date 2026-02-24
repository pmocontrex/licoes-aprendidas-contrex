import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import verificar_permissao
from utils.db_queries import listar_acoes, listar_paradas, listar_usuarios
from datetime import date

verificar_permissao(["pmo", "admin", "gestor"])

st.markdown("<div class='page-header'><h1>📊 Painel de Acompanhamento</h1></div>", unsafe_allow_html=True)

acoes = listar_acoes()
if not acoes:
    st.info("Nenhuma ação cadastrada.")
    st.stop()

df = pd.DataFrame(acoes)
df['prazo'] = pd.to_datetime(df['prazo'])
hoje = pd.Timestamp.now().normalize()
df['dias_restantes'] = (df['prazo'] - hoje).dt.days
df['vencido'] = (df['dias_restantes'] < 0) & (df['status'] != 'executado')
df['projeto'] = df['paradas'].apply(lambda x: x['contratos'][0]['codigo'] if x and x['contratos'] else '')

# Filtros
st.sidebar.header("Filtros")
projetos = st.sidebar.multiselect("Projeto", df['projeto'].unique(), default=df['projeto'].unique())
status = st.sidebar.multiselect("Status", df['status'].unique(), default=df['status'].unique())
df_filtrado = df[df['projeto'].isin(projetos) & df['status'].isin(status)]

# Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Ações", len(df_filtrado))
col2.metric("Pendentes", len(df_filtrado[df_filtrado['status'] == 'pendente']))
col3.metric("Executadas", len(df_filtrado[df_filtrado['status'] == 'executado']))
col4.metric("Vencidas", len(df_filtrado[df_filtrado['vencido']]))

# Gráficos
col_graf1, col_graf2 = st.columns(2)
with col_graf1:
    fig = px.pie(df_filtrado, names='status', title='Status das Ações')
    st.plotly_chart(fig, use_container_width=True)
with col_graf2:
    fig = px.bar(df_filtrado.groupby('projeto').size().reset_index(name='count'), x='projeto', y='count', title='Ações por Projeto')
    st.plotly_chart(fig, use_container_width=True)

# Tabela
st.subheader("Detalhamento")
df_display = df_filtrado[['projeto', 'descricao', 'responsavel_nome', 'prazo', 'status']].copy()
df_display['prazo'] = df_display['prazo'].dt.strftime('%d/%m/%Y')
st.dataframe(df_display, use_container_width=True)
