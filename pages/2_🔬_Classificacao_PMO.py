# pages/2_🔬_Classificacao_PMO.py
import streamlit as st
from utils.auth import verificar_permissao
from utils.db_queries import listar_paradas, listar_ocorrencias_por_parada, classificar_ocorrencias_bulk, atualizar_status_parada
from utils.gut_calculator import calcular_gut, get_descricao_gravidade, get_descricao_urgencia, get_descricao_tendencia

verificar_permissao(["pmo", "admin"])

st.set_page_config(layout="wide")
st.markdown("<div class='page-header'><h1>🔬 Classificação GUT - PMO</h1></div>", unsafe_allow_html=True)

with st.expander("ℹ️ Guia de Classificação GUT (passe o mouse sobre os números para ver a descrição)"):
    st.markdown("""
    - **Gravidade**: 1=Sem gravidade ... 5=Extremamente grave
    - **Urgência**: 1=Pode esperar ... 5=Urgentíssimo e inadiável
    - **Tendência**: 1=Manterá estabilidade ... 5=Piora imediata
    """)

paradas = listar_paradas(status='classificacao')
if not paradas:
    st.warning("Nenhuma parada em fase de classificação no momento.")
    st.stop()

parada_selecionada = st.selectbox(
    "Selecione a Parada",
    options=paradas,
    format_func=lambda p: f"{p['contratos']['codigo']} - {p['responsavel']}"
)

ocorrencias = listar_ocorrencias_por_parada(parada_selecionada["id"])
if not ocorrencias:
    st.info("Esta parada não possui ocorrências cadastradas.")
    st.stop()

st.subheader("Classifique as ocorrências abaixo:")

with st.form("classificacao_form"):
    classificacoes = []
    for occ in ocorrencias:
        with st.expander(f"📌 {occ['ocorrencia'][:100]}..."):
            st.write(f"**Setor:** {occ['area_setor']} | **Fase:** {occ['fase']}")
            st.write(f"**Ocorrência:** {occ['ocorrencia']}")
            st.write(f"**Impacto:** {occ['impacto']}")
            st.write(f"**Lição Aprendida:** {occ['licao_aprendida']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                g = st.selectbox(
                    "Gravidade",
                    options=[1,2,3,4,5],
                    index=2,
                    key=f"g_{occ['id']}",
                    help=get_descricao_gravidade
                )
            with col2:
                u = st.selectbox(
                    "Urgência",
                    options=[1,2,3,4,5],
                    index=2,
                    key=f"u_{occ['id']}",
                    help=get_descricao_urgencia
                )
            with col3:
                t = st.selectbox(
                    "Tendência",
                    options=[1,2,3,4,5],
                    index=2,
                    key=f"t_{occ['id']}",
                    help=get_descricao_tendencia
                )
            
            gut = calcular_gut(g, u, t)
            st.markdown(f"**Resultado GUT:** {gut['cor']} {gut['resultado']} - {gut['label']}")
            
            classificacoes.append({
                "id": occ["id"],
                "gravidade": g,
                "urgencia": u,
                "tendencia": t,
                "classificacao": gut["nivel"]
            })
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        salvar = st.form_submit_button("💾 Salvar Classificações", type="primary")
    with col_btn2:
        avancar = st.form_submit_button("▶️ Avançar para Plano de Ação")
    
    if salvar:
        classificar_ocorrencias_bulk(classificacoes)
        st.success("Classificações salvas com sucesso!")
    
    if avancar:
        classificar_ocorrencias_bulk(classificacoes)
        atualizar_status_parada(parada_selecionada["id"], "plano_acao")
        st.success("Parada avançada para a fase de Plano de Ação!")
        st.rerun()
