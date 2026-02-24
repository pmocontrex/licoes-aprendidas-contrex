import streamlit as st
from utils.auth import verificar_permissao, usuario_logado
from utils.db_queries import listar_acoes, atualizar_acao
from datetime import date

verificar_permissao(["setor", "pmo", "admin", "gestor"])

st.markdown("<div class='page-header'><h1>📝 Minhas Ações</h1></div>", unsafe_allow_html=True)

usuario = usuario_logado()
if usuario["perfil"] in ("pmo", "admin", "gestor"):
    acoes = listar_acoes()
else:
    acoes = listar_acoes({"responsavel_id": usuario["id"]})

if not acoes:
    st.info("Nenhuma ação atribuída a você.")
    st.stop()

for acao in acoes:
    with st.container():
        st.markdown(f"### {acao['descricao']}")
        cols = st.columns(4)
        # Extrai o nome do projeto de forma segura
        projeto = acao.get('paradas', {}).get('contratos', {}).get('codigo', 'N/A')
        cols[0].write(f"**Projeto:** {projeto}")
        cols[1].write(f"**Prazo:** {acao['prazo']}")
        cols[2].write(f"**Status:** {acao['status']}")
        if acao['status'] == 'pendente':
            if st.button(f"✅ Marcar como executada", key=f"exec_{acao['id']}"):
                atualizar_acao(acao["id"], {
                    "status": "executado",
                    "data_execucao": date.today().isoformat()
                })
                st.success("Ação marcada como executada!")
                st.rerun()
        st.divider()
