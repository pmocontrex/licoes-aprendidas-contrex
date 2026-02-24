# utils/supabase_client.py
from supabase import create_client, Client
import streamlit as st

@st.cache_resource
def get_supabase() -> Client:
    """Retorna o cliente Supabase configurado com as secrets do Streamlit."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)
