# pages/4_📊_Painel.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from utils.auth import verificar_permissao, usuario_logado
from utils.db_queries import listar_acoes, listar_paradas, listar_usuarios, atualizar_acao
from utils.gut_calculator import calcular_gut

verificar_permissao(["setor", "pmo", "admin", "gestor"])

st.set_page_config(layout="wide")
st.markdown("<div class='page-header'><h1>📊 Painel de Acompanhamento</h1></div>", unsafe_allow_html=True)

acoes = listar_acoes()
if not acoes:
    st.info("Nenhuma ação cadastrada.")
    st.stop()

df = pd.DataFrame(acoes)
df['prazo'] = pd.to_datetime(df['prazo'])
df['criado_em'] = pd.to_datetime(df['criado_em'])
df['atualizado_em'] = pd.to_datetime(df['atualizado_em'])
df['data_conclusao'] = pd.to_datetime(df['data_conclusao'])

hoje = pd.Timestamp.now().normalize()
df['dias_restantes'] = (df['prazo'] - hoje).dt.days
df['vencido'] = (df['dias_restantes'] < 0) & (df['status'] != 'concluido')
df['prazo_proximo'] = (df['dias_restantes'] <= 3) & (df['dias_restantes'] >= 0) & (df['status'] != 'concluido')

usuario = usuario_logado()
# Se for setor, filtrar por setor (lógica simplificada: assume que setor só vê ações de suas ocorrências)
# Isso exigiria join com ocorrencias. Para simplificar, vamos pular este filtro.

st.sidebar.header("Filtros")

paradas_list = listar_paradas()
paradas_dict = {p['id']: f"{p.get('contratos',{}).get('codigo','')} - {p['responsavel']}" for p in paradas_list}
projetos_selecionados = st.sidebar.multiselect(
    "🏗️ Projeto/Parada",
    options=list(paradas_dict.keys()),
    format_func=lambda x: paradas_dict[x],
    default=list(paradas_dict.keys())
)

usuarios_list = listar_usuarios()
usuarios_dict = {u['id']: u['nome'] for u in usuarios_list}
responsaveis_selecionados = st.sidebar.multiselect(
    "👤 Responsável",
    options=list(usuarios_dict.keys()),
    format_func=lambda x: usuarios_dict[x],
    default=list(usuarios_dict.keys())
)

status_opcoes = ['pendente', 'em_andamento', 'concluido', 'cancelado']
status_selecionados = st.sidebar.multiselect(
    "📌 Status",
    options=status_opcoes,
    default=status_opcoes
)

niveis_gut = ['baixo', 'medio', 'alto']
niveis_selecionados = st.sidebar.multiselect(
    "⚡ Nível GUT",
    options=niveis_gut,
    default=niveis_gut
)

data_inicio = st.sidebar.date_input("Data início", value=date.today() - timedelta(days=30))
data_fim = st.sidebar.date_input("Data fim", value=date.today() + timedelta(days=90))

df_filtrado = df[
    df['parada_id'].isin(projetos_selecionados) &
    df['responsavel_id'].isin(responsaveis_selecionados) &
    df['status'].isin(status_selecionados) &
    (df['prazo'].dt.date >= data_inicio) &
    (df['prazo'].dt.date <= data_fim)
]

df_filtrado['classificacao'] = df_filtrado['ocorrencias'].apply(lambda x: x.get('classificacao') if x else None)
if niveis_selecionados:
    df_filtrado = df_filtrado[df_filtrado['classificacao'].isin(niveis_selecionados)]

total_acoes = len(df_filtrado)
pendentes = len(df_filtrado[df_filtrado['status'] == 'pendente'])
andamento = len(df_filtrado[df_filtrado['status'] == 'em_andamento'])
concluidas = len(df_filtrado[df_filtrado['status'] == 'concluido'])
vencidas = len(df_filtrado[df_filtrado['vencido'] == True])

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total de Ações", total_acoes)
with col2:
    st.metric("Pendentes", pendentes)
with col3:
    st.metric("Em Andamento", andamento)
with col4:
    st.metric("Concluídas", concluidas)
with col5:
    st.metric("Vencidas", vencidas)

col_graf1, col_graf2 = st.columns(2)
with col_graf1:
    status_counts = df_filtrado['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'quantidade']
    fig = px.pie(status_counts, values='quantidade', names='status', title='Distribuição por Status')
    st.plotly_chart(fig, use_container_width=True)

with col_graf2:
    projeto_counts = df_filtrado.groupby('parada_id').size().reset_index(name='quantidade')
    projeto_counts['projeto'] = projeto_counts['parada_id'].map(paradas_dict)
    fig = px.bar(projeto_counts, x='projeto', y='quantidade', title='Ações por Projeto')
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Detalhamento das Ações")

df_display = df_filtrado.copy()
df_display['projeto'] = df_display['parada_id'].map(paradas_dict)
df_display['responsavel'] = df_display['responsavel_id'].map(usuarios_dict)
df_display['prazo_str'] = df_display['prazo'].dt.strftime('%d/%m/%Y')
df_display['dias_restantes'] = df_display['dias_restantes'].fillna(0).astype(int)
df_display['ocorrencia_resumo'] = df_display['ocorrencias'].apply(lambda x: x['ocorrencia'][:50] + '...' if x and x['ocorrencia'] else '')
df_display['gut_nivel'] = df_display['ocorrencias'].apply(lambda x: calcular_gut(x['gravidade'] or 1, x['urgencia'] or 1, x['tendencia'] or 1)['label'] if x else '')

def highlight_rows(row):
    if row['vencido']:
        return ['background-color: #ffcccc'] * len(row)
    elif row['prazo_proximo']:
        return ['background-color: #fff3cd'] * len(row)
    else:
        return [''] * len(row)

colunas_exibir = ['projeto', 'ocorrencia_resumo', 'gut_nivel', 'descricao', 'responsavel', 'prazo_str', 'dias_restantes', 'status']
df_display = df_display[colunas_exibir].rename(columns={
    'projeto': 'Projeto',
    'ocorrencia_resumo': 'Ocorrência',
    'gut_nivel': 'GUT',
    'descricao': 'Ação',
    'responsavel': 'Responsável',
    'prazo_str': 'Prazo',
    'dias_restantes': 'Dias Restantes',
    'status': 'Status'
})

st.dataframe(
    df_display.style.apply(highlight_rows, axis=1),
    use_container_width=True,
    height=400
)

st.subheader("Atualizar Status de uma Ação")
acoes_ids = df_filtrado['id'].tolist()
if acoes_ids:
    acao_selecionada = st.selectbox(
        "Selecione a ação para atualizar",
        options=acoes_ids,
        format_func=lambda x: f"{df_filtrado[df_filtrado['id']==x]['descricao'].values[0][:50]}..."
    )
    novo_status = st.selectbox("Novo Status", ['pendente', 'em_andamento', 'concluido', 'cancelado'])
    comentario = st.text_area("Comentário (opcional)")
    if st.button("Atualizar"):
        atualizar_acao(acao_selecionada, novo_status, comentario)
        st.success("Status atualizado!")
        st.rerun()
