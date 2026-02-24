from supabase import create_client, Client
import streamlit as st
import re

@st.cache_resource
def get_supabase() -> Client:
    # Obter valores das secrets e remover espaços extras
    url = st.secrets.get("SUPABASE_URL", "").strip()
    key = st.secrets.get("SUPABASE_KEY", "").strip()

    # DEBUG: exibir os valores (a chave é parcialmente ocultada)
    st.write(f"🔍 DEBUG - URL lida: '{url}'")
    st.write(f"🔍 DEBUG - Chave (início): {key[:10] if key else 'None'}...")

    if not url:
        st.error("❌ A variável SUPABASE_URL não foi configurada nas secrets.")
        st.stop()

    if not key:
        st.error("❌ A variável SUPABASE_KEY não foi configurada nas secrets.")
        st.stop()

    # Validar formato da URL
    if not re.match(r"^https?://", url):
        st.error(f"❌ A URL '{url}' não é válida. Deve começar com http:// ou https://.")
        st.stop()

    try:
        client = create_client(url, key)
        st.success("✅ Cliente Supabase criado com sucesso!")
        return client
    except Exception as e:
        st.error(f"❌ Erro ao criar cliente Supabase: {e}")
        st.stop()
