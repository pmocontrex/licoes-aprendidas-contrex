from supabase import create_client, Client
import streamlit as st

@st.cache_resource
def get_supabase() -> Client:
    """Retorna o cliente Supabase configurado com as secrets do Streamlit."""
    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY")
    if not url or not key:
        st.error("Credenciais do Supabase não configuradas. Verifique as secrets.")
        st.stop()
    return create_client(url, key)
