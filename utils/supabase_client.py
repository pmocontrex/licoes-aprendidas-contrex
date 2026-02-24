from supabase import create_client, Client
import streamlit as st
import re

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets.get("SUPABASE_URL", "").strip()
    key = st.secrets.get("SUPABASE_KEY", "").strip()

    if not url or not key:
        st.error("Credenciais do Supabase não configuradas. Verifique as secrets.")
        st.stop()

    if not re.match(r"^https?://", url):
        st.error(f"URL inválida: {url}")
        st.stop()

    return create_client(url, key)
