# pages/3_📝_Plano_de_Acao.py
import streamlit as st
from utils.auth import verificar_permissao
from utils.db_queries import listar_paradas, listar_ocorrencias_por_parada, listar_usuarios, criar_acao, listar_acoes, atualizar_status_parada
from utils.gut_calculator import calcular_gut
from utils.notifications import notificar_responsavel_acao, notificar_plano_publicado
from datetime import date

verificar_permissao(["pmo", "admin"])

st.set_page_config(layout="wide")
st.markdown("<div class='page-header'><h1>📝 Plano de Ação - PMO</h1></div>", unsafe_allow_html=True)

paradas = listar_paradas(status='plano_acao')
if not paradas:
    st.warning("Nenhuma parada em fase de plano de ação.")
    st.stop()

parada_selecionada = st.selectbox(
    "Selecione a Parada",
    options=paradas,
    format_func=lambda p: f"{p['contratos']['codigo']} - {p['responsavel']}"
)

ocorrencias = listar_ocorrencias_por_parada(parada_selecionada["id"])
ocorrencias.sort(key=lambda x: (x['resultado_gut'] or 0), reverse=True)

usuarios = listar_usuarios()
opcoes_responsaveis = {u['id']: u['nome'] for u in usuarios}
email_responsaveis = {u['id']: u['email'] for u in usuarios}

st.subheader("Criação de Ações por Ocorrência")

for occ in ocorrencias:
    gut = calcular_gut(occ['gravidade'] or 3, occ['urgencia'] or 3, occ['tendencia'] or 3)
    with st.expander(f"{gut['cor']} {occ['ocorrencia'][:100]}... (GUT: {gut['resultado']} - {gut['label']})"):
        st.write(f"**Setor:** {occ['area_setor']} | **Fase:** {occ['fase']}")
        st.write(f"**Impacto:** {occ['impacto']}")
        st.write(f"**Lição:** {occ['licao_aprendida']}")
        
        with st.form(key=f"form_acao_{occ['id']}"):
            descricao = st.text_area("📌 Descrição da Ação", key=f"desc_{occ['id']}")
            prazo = st.date_input("📅 Prazo", min_value=date.today(), key=f"prazo_{occ['id']}")
            responsavel_id = st.selectbox(
                "👤 Responsável",
                options=list(opcoes_responsaveis.keys()),
                format_func=lambda x: opcoes_responsaveis[x],
                key=f"resp_{occ['id']}"
            )
            col1, col2 = st.columns([1,5])
            with col1:
                submitted = st.form_submit_button("➕ Adicionar")
                if submitted:
                    if descricao and prazo and responsavel_id:
                        nova_acao = {
                            "ocorrencia_id": occ["id"],
                            "parada_id": parada_selecionada["id"],
                            "descricao": descricao,
                            "prazo": prazo.isoformat(),
                            "responsavel_id": responsavel_id,
                            "responsavel_nome": opcoes_responsaveis[responsavel_id],
                            "status": "pendente"
                        }
                        acao_criada = criar_acao(nova_acao)
                        if acao_criada:
                            st.success("Ação adicionada!")
                            notificar_responsavel_acao(
                                email=email_responsaveis[responsavel_id],
                                nome=opcoes_responsaveis[responsavel_id],
                                acao=descricao,
                                prazo=prazo.strftime("%d/%m/%Y"),
                                projeto=parada_selecionada["contratos"]["codigo"]
                            )
                            st.rerun()
                    else:
                        st.error("Preencha todos os campos.")
        
        acoes_existentes = listar_acoes({"ocorrencia_id": occ["id"]})
        if acoes_existentes:
            st.write("**Ações já criadas:**")
            for acao in acoes_existentes:
                st.markdown(f"- {acao['descricao']} (Responsável: {acao['responsavel_nome']}, Prazo: {acao['prazo']}, Status: {acao['status']})")

if st.button("🚀 Publicar Plano de Ação", type="primary"):
    todas_acoes = listar_acoes({"parada_id": parada_selecionada["id"]})
    if not todas_acoes:
        st.error("Crie pelo menos uma ação antes de publicar.")
    else:
        atualizar_status_parada(parada_selecionada["id"], "monitoramento")
        emails_responsaveis = list(set([acao['responsavel_id'] for acao in todas_acoes if acao['responsavel_id']]))
        notificar_plano_publicado(emails_responsaveis, parada_selecionada["contratos"]["codigo"])
        st.success("Plano de Ação publicado com sucesso! A parada agora está em monitoramento.")
        st.rerun()
