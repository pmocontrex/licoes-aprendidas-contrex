# app.py
import streamlit as st
from utils.auth import login, logout, verificar_permissao, usuario_logado
from utils.supabase_client import get_supabase
import time

# Configuração da página
st.set_page_config(
    page_title="Contrex - Lições Aprendidas",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo global
st.markdown("""
<style>
    /* Cores da marca */
    :root {
        --primary: #1B3A6B;
        --accent: #E87722;
    }
    .main-header {
        background: linear-gradient(135deg, #1B3A6B, #2D5AA0);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 5px solid #E87722;
    }
    .card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        border-top: 4px solid var(--accent);
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    section[data-testid="stSidebar"] {
        background-color: #1B3A6B !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session_state
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# Se não estiver autenticado, mostra tela de login
if not st.session_state["autenticado"]:
    st.markdown("<div class='main-header'><h1>📘 Contrex Engenharia - Lições Aprendidas</h1></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            st.subheader("Acesso ao Sistema")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar", use_container_width=True)
            if submitted:
                with st.spinner("Autenticando..."):
                    resultado = login(email, senha)
                    if resultado["sucesso"]:
                        st.success("Login efetuado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Falha no login: {resultado['erro']}")
    st.stop()

# Se autenticado, mostra a home
usuario = usuario_logado()
st.sidebar.image("https://via.placeholder.com/150x50?text=CONTREX", use_container_width=True)  # Placeholder da logo
st.sidebar.write(f"**Olá, {usuario['nome']}**")
st.sidebar.write(f"Perfil: **{usuario['perfil'].upper()}**")
st.sidebar.divider()

# Navegação
st.sidebar.page_link("app.py", label="🏠 Home")
st.sidebar.page_link("pages/1_📋_Formulario_Setor.py", label="📋 Formulário do Setor")
st.sidebar.page_link("pages/2_🔬_Classificacao_PMO.py", label="🔬 Classificação GUT")
st.sidebar.page_link("pages/3_📝_Plano_de_Acao.py", label="📝 Plano de Ação")
st.sidebar.page_link("pages/4_📊_Painel.py", label="📊 Painel de Acompanhamento")

# Link para Admin apenas se perfil for admin
if usuario['perfil'] == 'admin':
    st.sidebar.page_link("pages/5_⚙️_Admin.py", label="⚙️ Administração")

if st.sidebar.button("🚪 Sair", use_container_width=True):
    logout()

# Conteúdo da Home
st.markdown("<div class='main-header'><h1>🏠 Painel Inicial</h1></div>", unsafe_allow_html=True)

st.subheader(f"Bem-vindo ao sistema de Lições Aprendidas, {usuario['nome']}!")

# Cards de acesso rápido
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<div class='card'><h3>📋 Formulário</h3><p>Registrar ocorrências</p><a href='/Formulario_Setor' target='_self'>Acessar</a></div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='card'><h3>🔬 Classificar</h3><p>Classificação GUT</p><a href='/Classificacao_PMO' target='_self'>Acessar</a></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='card'><h3>📝 Planos</h3><p>Criar ações</p><a href='/Plano_de_Acao' target='_self'>Acessar</a></div>", unsafe_allow_html=True)
with col4:
    st.markdown("<div class='card'><h3>📊 Painel</h3><p>Acompanhar ações</p><a href='/Painel' target='_self'>Acessar</a></div>", unsafe_allow_html=True)

# Exibir parada ativa (se houver)
from utils.db_queries import listar_paradas
paradas_ativas = listar_paradas(status='coleta') + listar_paradas(status='classificacao') + listar_paradas(status='plano_acao')
if paradas_ativas:
    st.info(f"🔔 Você possui {len(paradas_ativas)} parada(s) em andamento.")
