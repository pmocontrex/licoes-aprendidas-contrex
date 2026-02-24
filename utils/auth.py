# utils/auth.py
import streamlit as st
from utils.supabase_client import get_supabase
import time

def login(email: str, senha: str) -> dict:
    """
    Autentica o usuário via Supabase Auth.
    Retorna um dicionário com session e dados do perfil, ou lança exceção.
    """
    supabase = get_supabase()
    try:
        # Autenticar
        resposta = supabase.auth.sign_in_with_password({"email": email, "password": senha})
        # Buscar perfil do usuário na tabela perfis_usuarios
        perfil = supabase.table("perfis_usuarios").select("*").eq("id", resposta.user.id).execute()
        if not perfil.data:
            raise Exception("Perfil de usuário não encontrado. Contate o administrador.")
        usuario = perfil.data[0]
        # Armazenar na session_state
        st.session_state["usuario"] = usuario
        st.session_state["sessao"] = resposta
        st.session_state["autenticado"] = True
        return {"sucesso": True, "usuario": usuario}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

def logout():
    """Limpa a sessão e redireciona para a tela de login."""
    supabase = get_supabase()
    supabase.auth.sign_out()
    for key in ["usuario", "sessao", "autenticado"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def get_perfil_atual() -> str:
    """Retorna o perfil do usuário logado."""
    if "usuario" in st.session_state:
        return st.session_state["usuario"]["perfil"]
    return None

def verificar_permissao(perfis_permitidos: list) -> bool:
    """
    Verifica se o usuário atual tem permissão para acessar a página.
    Se não tiver, exibe mensagem e interrompe a execução.
    """
    if not st.session_state.get("autenticado", False):
        st.warning("Você precisa estar logado para acessar esta página.")
        st.stop()
        return False

    perfil = get_perfil_atual()
    if perfil not in perfis_permitidos:
        st.error(f"Acesso negado. Seu perfil '{perfil}' não tem permissão para acessar esta página.")
        st.stop()
        return False
    return True

def usuario_logado() -> dict:
    """Retorna os dados completos do usuário logado."""
    return st.session_state.get("usuario", {})
