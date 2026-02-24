# pages/1_📋_Formulario_Setor.py
import streamlit as st
from utils.auth import verificar_permissao, usuario_logado
from utils.db_queries import listar_paradas, inserir_ocorrencias, listar_usuarios
from utils.notifications import notificar_pmo_nova_ocorrencia

verificar_permissao(["setor", "pmo", "admin"])

st.set_page_config(layout="wide")
st.markdown("<div class='page-header'><h1>📋 Formulário de Ocorrências</h1></div>", unsafe_allow_html=True)

# Listar paradas com coleta aberta
paradas = listar_paradas({"status": "coleta", "coleta_aberta": True})
if not paradas:
    st.warning("Não há projetos com coleta aberta no momento.")
    st.stop()

parada = st.selectbox(
    "Selecione o Projeto",
    options=paradas,
    format_func=lambda p: f"{p['contratos']['codigo']} - {p['responsavel']}"
)

st.info(f"Coleta aberta até {parada['data_fim']}")

if "linhas" not in st.session_state:
    st.session_state.linhas = [{"id": 0}]

def adicionar_linha():
    novo_id = max([l["id"] for l in st.session_state.linhas]) + 1
    st.session_state.linhas.append({"id": novo_id})

def remover_linha(linha_id):
    st.session_state.linhas = [l for l in st.session_state.linhas if l["id"] != linha_id]

with st.form("form_ocorrencias"):
    dados = []
    remover_ids = []
    for linha in st.session_state.linhas:
        cols = st.columns([2,2,3,3,3,1])
        with cols[0]:
            area = st.text_input("Área/Setor", key=f"area_{linha['id']}")
        with cols[1]:
            fase = st.text_input("Fase", key=f"fase_{linha['id']}")
        with cols[2]:
            occ = st.text_area("Ocorrência", key=f"occ_{linha['id']}", height=80)
        with cols[3]:
            imp = st.text_area("Impacto", key=f"imp_{linha['id']}", height=80)
        with cols[4]:
            licao = st.text_area("Lição Aprendida", key=f"licao_{linha['id']}", height=80)
        with cols[5]:
            if st.form_submit_button("🗑️", key=f"remove_{linha['id']}", type="secondary"):
                remover_ids.append(linha['id'])
        dados.append({
            "parada_id": parada["id"],
            "area_setor": area,
            "fase": fase,
            "ocorrencia": occ,
            "impacto": imp,
            "licao_aprendida": licao
        })

    col1, col2 = st.columns([1,5])
    with col1:
        add = st.form_submit_button("➕ Adicionar")
    with col2:
        enviar = st.form_submit_button("📤 Enviar para PMO", type="primary")

    if add:
        adicionar_linha()
        st.rerun()

    for rid in remover_ids:
        remover_linha(rid)
    if remover_ids:
        st.rerun()

    if enviar:
        validos = [o for o in dados if o["area_setor"] and o["fase"] and o["ocorrencia"] and o["impacto"] and o["licao_aprendida"]]
        if not validos:
            st.error("Preencha pelo menos uma ocorrência completa.")
        else:
            inseridas = inserir_ocorrencias(validos)
            st.success(f"{len(inseridas)} ocorrência(s) enviada(s)!")
            pmos = listar_usuarios(perfil="pmo")
            emails_pmo = [p["email"] for p in pmos if p.get("email")]
            notificar_pmo_nova_ocorrencia(emails_pmo, usuario_logado().get("setor", "Setor"), parada["contratos"]["codigo"])
            st.session_state.linhas = [{"id": 0}]
            st.rerun()
