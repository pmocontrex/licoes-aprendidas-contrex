import streamlit as st
from utils.supabase_client import get_supabase
import time

def login(email: str, senha: str) -> dict:
    supabase = get_supabase()
    try:
        resposta = supabase.auth.sign_in_with_password({"email": email, "password": senha})
        perfil = supabase.table("perfis_usuarios").select("*").eq("id", resposta.user.id).execute()
        if not perfil.data:
            raise Exception("Perfil de usuário não encontrado. Contate o administrador.")
        usuario = perfil.data[0]
        st.session_state["usuario"] = usuario
        st.session_state["sessao"] = resposta
        st.session_state["autenticado"] = True
        return {"sucesso": True, "usuario": usuario}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

def logout():
    supabase = get_supabase()
    supabase.auth.sign_out()
    for key in ["usuario", "sessao", "autenticado"]:
        st.session_state.pop(key, None)
    st.rerun()

def get_perfil_atual() -> str:
    return st.session_state.get("usuario", {}).get("perfil")

def verificar_permissao(perfis_permitidos: list):
    if not st.session_state.get("autenticado"):
        st.warning("Você precisa estar logado.")
        st.stop()
    perfil = get_perfil_atual()
    if perfil not in perfis_permitidos:
        st.error(f"Acesso negado. Perfil '{perfil}' não autorizado.")
        st.stop()

def usuario_logado() -> dict:
    return st.session_state.get("usuario", {})
