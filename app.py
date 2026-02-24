import streamlit as st
from utils.auth import login, logout, verificar_permissao, usuario_logado

st.set_page_config(page_title="Contrex - Lições Aprendidas", page_icon="📘", layout="wide")

# Estilo global
st.markdown("""
<style>
    .main-header { background: linear-gradient(135deg, #1B3A6B, #2D5AA0); color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; border-left: 5px solid #E87722; }
    .card { background: white; border-radius: 10px; padding: 1.5rem; border-top: 4px solid #E87722; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; }
    section[data-testid="stSidebar"] { background-color: #1B3A6B !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<div class='main-header'><h1>📘 Contrex Engenharia - Lições Aprendidas</h1></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                with st.spinner("Autenticando..."):
                    res = login(email, senha)
                    if res["sucesso"]:
                        st.success("Login efetuado!")
                        st.rerun()
                    else:
                        st.error(f"Falha: {res['erro']}")
    st.stop()

usuario = usuario_logado()
st.sidebar.image("https://via.placeholder.com/150x50?text=CONTREX")
st.sidebar.write(f"**{usuario['nome']}**")
st.sidebar.write(f"Perfil: **{usuario['perfil'].upper()}**")
st.sidebar.divider()

st.sidebar.page_link("app.py", label="🏠 Home")
st.sidebar.page_link("pages/1_📋_Formulario_Setor.py", label="📋 Formulário do Setor")
st.sidebar.page_link("pages/2_🔬_Classificacao_PMO.py", label="🔬 Classificação GUT")
st.sidebar.page_link("pages/3_📝_Plano_de_Acao.py", label="📝 Minhas Ações")
st.sidebar.page_link("pages/4_📊_Painel.py", label="📊 Painel")
if usuario['perfil'] == 'admin':
    st.sidebar.page_link("pages/5_⚙️_Admin.py", label="⚙️ Administração")

if st.sidebar.button("🚪 Sair"):
    logout()

st.markdown("<div class='main-header'><h1>🏠 Painel Inicial</h1></div>", unsafe_allow_html=True)
st.subheader(f"Bem-vindo, {usuario['nome']}!")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<div class='card'><h3>📋 Formulário</h3><p>Registrar ocorrências</p><a href='/Formulario_Setor' target='_self'>Acessar</a></div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='card'><h3>🔬 Classificar</h3><p>Classificação GUT</p><a href='/Classificacao_PMO' target='_self'>Acessar</a></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='card'><h3>📝 Ações</h3><p>Minhas ações</p><a href='/Plano_de_Acao' target='_self'>Acessar</a></div>", unsafe_allow_html=True)
with col4:
    st.markdown("<div class='card'><h3>📊 Painel</h3><p>Acompanhamento</p><a href='/Painel' target='_self'>Acessar</a></div>", unsafe_allow_html=True)
