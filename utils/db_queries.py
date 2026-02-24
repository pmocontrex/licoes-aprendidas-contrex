from utils.supabase_client import get_supabase
import streamlit as st
from typing import Optional, List, Dict
from datetime import date

# -------------------- CONTRATOS --------------------
def listar_contratos() -> List[Dict]:
    supabase = get_supabase()
    return supabase.table("contratos").select("*").execute().data

# -------------------- PARADAS --------------------
def listar_paradas(filtros: dict = None) -> List[Dict]:
    supabase = get_supabase()
    query = supabase.table("paradas").select("*, contratos(*)")
    if filtros:
        for k, v in filtros.items():
            if v is not None:
                query = query.eq(k, v)
    return query.execute().data

def criar_parada(dados: dict) -> dict:
    supabase = get_supabase()
    dados["criado_por"] = st.session_state["usuario"]["id"]
    return supabase.table("paradas").insert(dados).execute().data[0]

def atualizar_parada(parada_id: str, dados: dict):
    supabase = get_supabase()
    supabase.table("paradas").update(dados).eq("id", parada_id).execute()

# -------------------- OCORRÊNCIAS --------------------
def inserir_ocorrencias(ocorrencias: list) -> list:
    supabase = get_supabase()
    for occ in ocorrencias:
        occ["enviado_por"] = st.session_state["usuario"]["id"]
    return supabase.table("ocorrencias").insert(ocorrencias).execute().data

def listar_ocorrencias_por_parada(parada_id: str) -> List[Dict]:
    supabase = get_supabase()
    return supabase.table("ocorrencias").select("*").eq("parada_id", parada_id).execute().data

def classificar_ocorrencia(ocorrencia_id: str, dados: dict):
    supabase = get_supabase()
    supabase.table("ocorrencias").update(dados).eq("id", ocorrencia_id).execute()

# -------------------- AÇÕES --------------------
def criar_acao(dados: dict) -> dict:
    supabase = get_supabase()
    return supabase.table("acoes").insert(dados).execute().data[0]

def listar_acoes(filtros: dict = None) -> List[Dict]:
    supabase = get_supabase()
    query = supabase.table("acoes").select("*, ocorrencias(*), paradas(contratos(*))")
    if filtros:
        for k, v in filtros.items():
            if v is not None:
                query = query.eq(k, v)
    return query.execute().data

def atualizar_acao(acao_id: str, dados: dict):
    supabase = get_supabase()
    supabase.table("acoes").update(dados).eq("id", acao_id).execute()

# -------------------- USUÁRIOS --------------------
def listar_usuarios(perfil: Optional[str] = None) -> List[Dict]:
    supabase = get_supabase()
    query = supabase.table("perfis_usuarios").select("*")
    if perfil:
        query = query.eq("perfil", perfil)
    return query.execute().data

def criar_usuario_perfil(dados: dict):
    supabase = get_supabase()
    supabase.table("perfis_usuarios").insert(dados).execute()

def atualizar_usuario_perfil(user_id: str, dados: dict):
    supabase = get_supabase()
    supabase.table("perfis_usuarios").update(dados).eq("id", user_id).execute()
