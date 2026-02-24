import streamlit as st
from utils.auth import verificar_permissao
from utils.db_queries import listar_paradas, listar_ocorrencias_por_parada, classificar_ocorrencia, criar_acao, listar_usuarios
from utils.gut_calculator import calcular_gut, get_descricao_gravidade, get_descricao_urgencia, get_descricao_tendencia
from utils.notifications import notificar_responsavel_acao

verificar_permissao(["pmo", "admin"])

st.markdown("<div class='page-header'><h1>🔬 Classificação GUT</h1></div>", unsafe_allow_html=True)

paradas = listar_paradas({"status": "coleta"})  # Mostra todas em coleta, independente de aberta
if not paradas:
    st.warning("Nenhum projeto em fase de coleta.")
    st.stop()

parada = st.selectbox(
    "Selecione o Projeto",
    options=paradas,
    format_func=lambda p: f"{p['contratos']['codigo']} - {p['responsavel']}"
)

ocorrencias = listar_ocorrencias_por_parada(parada["id"])
ocorrencias_nao_classificadas = [o for o in ocorrencias if o["gravidade"] is None]

if not ocorrencias_nao_classificadas:
    st.info("Todas as ocorrências já foram classificadas.")
    st.stop()

st.subheader("Classifique as ocorrências pendentes")

usuarios = listar_usuarios()
opcoes_resp = {u["id"]: u["nome"] for u in usuarios if u["perfil"] in ("setor", "pmo", "admin")}

for occ in ocorrencias_nao_classificadas:
    with st.expander(f"📌 {occ['ocorrencia'][:80]}..."):
        st.write(f"**Setor:** {occ['area_setor']} | **Fase:** {occ['fase']}")
        st.write(f"**Ocorrência:** {occ['ocorrencia']}")
        st.write(f"**Impacto:** {occ['impacto']}")
        st.write(f"**Lição:** {occ['licao_aprendida']}")

        with st.form(key=f"class_{occ['id']}"):
            g = st.selectbox("Gravidade", [1,2,3,4,5], index=2, help=get_descricao_gravidade)
            u = st.selectbox("Urgência", [1,2,3,4,5], index=2, help=get_descricao_urgencia)
            t = st.selectbox("Tendência", [1,2,3,4,5], index=2, help=get_descricao_tendencia)
            gut = calcular_gut(g, u, t)
            st.markdown(f"**Resultado:** {gut['cor']} {gut['resultado']} - {gut['label']}")

            gerar_acao = st.checkbox("Gerar ação para esta ocorrência", value=True)

            resp_id = None
            prazo = None
            desc_acao = None
            if gerar_acao:
                desc_acao = st.text_area("Descrição da ação", key=f"desc_{occ['id']}")
                prazo = st.date_input("Prazo", key=f"prazo_{occ['id']}")
                resp_id = st.selectbox(
                    "Responsável",
                    options=list(opcoes_resp.keys()),
                    format_func=lambda x: opcoes_resp[x],
                    key=f"resp_{occ['id']}"
                )

            if st.form_submit_button("Salvar Classificação"):
                # Salvar classificação
                dados_class = {
                    "gravidade": g,
                    "urgencia": u,
                    "tendencia": t,
                    "classificacao": gut["nivel"],
                    "gerar_acao": gerar_acao
                }
                classificar_ocorrencia(occ["id"], dados_class)

                if gerar_acao and desc_acao and prazo and resp_id:
                    acao = {
                        "ocorrencia_id": occ["id"],
                        "parada_id": parada["id"],
                        "descricao": desc_acao,
                        "prazo": prazo.isoformat(),
                        "responsavel_id": resp_id,
                        "responsavel_nome": opcoes_resp[resp_id],
                        "status": "pendente"
                    }
                    nova_acao = criar_acao(acao)
                    # Notificar responsável
                    email_resp = next((u["email"] for u in usuarios if u["id"] == resp_id), None)
                    if email_resp:
                        notificar_responsavel_acao(
                            email_resp,
                            opcoes_resp[resp_id],
                            desc_acao,
                            prazo.strftime("%d/%m/%Y"),
                            parada["contratos"]["codigo"]
                        )
                    st.success("Classificação e ação salvas!")
                else:
                    st.success("Classificação salva (sem ação).")
                st.rerun()
