# pages/1_📋_Formulario_Setor.py
import streamlit as st
from utils.auth import verificar_permissao, usuario_logado
from utils.db_queries import listar_paradas, inserir_ocorrencias
from utils.notifications import notificar_pmo_envio_formulario

verificar_permissao(["setor", "pmo", "admin"])

st.set_page_config(layout="wide")
st.markdown("<div class='page-header'><h1>📋 Formulário de Lições Aprendidas - Setor</h1></div>", unsafe_allow_html=True)

# Selecionar parada ativa
paradas = listar_paradas(status='coleta')
if not paradas:
    st.warning("Não há paradas em fase de coleta no momento.")
    st.stop()

parada_selecionada = st.selectbox(
    "Selecione a Parada Ativa",
    options=paradas,
    format_func=lambda p: f"{p['contratos']['codigo']} - {p['responsavel']} ({p['data_inicio']} a {p['data_fim']})"
)

# Exibir dados da parada (bloqueados)
col1, col2, col3 = st.columns(3)
with col1:
    st.text_input("Contrato", value=parada_selecionada['contratos']['codigo'], disabled=True)
with col2:
    st.text_input("Responsável da Parada", value=parada_selecionada['responsavel'], disabled=True)
with col3:
    st.text_input("Período", value=f"{parada_selecionada['data_inicio']} a {parada_selecionada['data_fim']}", disabled=True)

st.divider()

# Gerenciar linhas dinâmicas com session_state
if "linhas" not in st.session_state:
    st.session_state.linhas = [{"id": 0}]

def adicionar_linha():
    novo_id = max([l["id"] for l in st.session_state.linhas] + [0]) + 1
    st.session_state.linhas.append({"id": novo_id})

def remover_linha(linha_id):
    st.session_state.linhas = [l for l in st.session_state.linhas if l["id"] != linha_id]

# Formulário
with st.form(key="form_ocorrencias"):
    ocorrencias_data = []
    indices_para_remover = []
    
    for i, linha in enumerate(st.session_state.linhas):
        cols = st.columns([2,2,3,3,3,1])
        with cols[0]:
            area_setor = st.text_input("Área/Setor", key=f"area_{linha['id']}", placeholder="Ex: Caldeiraria")
        with cols[1]:
            fase = st.text_input("Fase", key=f"fase_{linha['id']}", placeholder="Ex: Montagem")
        with cols[2]:
            ocorrencia = st.text_area("Ocorrência", key=f"occ_{linha['id']}", height=80, placeholder="Descreva a ocorrência")
        with cols[3]:
            impacto = st.text_area("Impacto", key=f"imp_{linha['id']}", height=80, placeholder="Impacto observado")
        with cols[4]:
            licao = st.text_area("Lição Aprendida", key=f"licao_{linha['id']}", height=80, placeholder="O que aprendemos?")
        with cols[5]:
            if st.form_submit_button("🗑️", type="secondary"):
                indices_para_remover.append(linha['id'])
        
        ocorrencias_data.append({
            "parada_id": parada_selecionada["id"],
            "area_setor": area_setor,
            "fase": fase,
            "ocorrencia": ocorrencia,
            "impacto": impacto,
            "licao_aprendida": licao
        })
    
    col_btn1, col_btn2, col_btn3 = st.columns([1,1,2])
    with col_btn1:
        adicionar = st.form_submit_button("➕ Adicionar Ocorrência")
    with col_btn2:
        salvar_rascunho = st.form_submit_button("💾 Salvar Rascunho")
    with col_btn3:
        enviar = st.form_submit_button("✅ Enviar para PMO", type="primary")
    
    if adicionar:
        adicionar_linha()
        st.rerun()
    
    for rid in indices_para_remover:
        remover_linha(rid)
    if indices_para_remover:
        st.rerun()
    
    if salvar_rascunho or enviar:
        dados_validos = [occ for occ in ocorrencias_data if occ["area_setor"] and occ["fase"] and occ["ocorrencia"] and occ["impacto"] and occ["licao_aprendida"]]
        if not dados_validos:
            st.error("Preencha pelo menos uma ocorrência completa.")
        else:
            inseridas = inserir_ocorrencias(dados_validos)
            st.success(f"{len(inseridas)} ocorrência(s) salva(s) com sucesso!")
            if enviar:
                from utils.db_queries import listar_usuarios
                pmo_users = listar_usuarios(perfil="pmo")
                for pmo in pmo_users:
                    notificar_pmo_envio_formulario(
                        pmo["email"],
                        usuario_logado().get("setor", "Setor"),
                        parada_selecionada["contratos"]["codigo"]
                    )
                st.info("Notificação enviada ao PMO.")
