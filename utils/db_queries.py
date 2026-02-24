# utils/db_queries.py
from utils.supabase_client import get_supabase
import streamlit as st
from typing import Optional, List, Dict
from datetime import date

# -------------------- PARADAS --------------------
def listar_paradas(status: Optional[str] = None) -> List[Dict]:
    supabase = get_supabase()
    query = supabase.table("paradas").select("*, contratos(*)")
    if status:
        query = query.eq("status", status)
    resposta = query.execute()
    return resposta.data

def criar_parada(dados: dict) -> dict:
    supabase = get_supabase()
    dados["criado_por"] = st.session_state["usuario"]["id"]
    resposta = supabase.table("paradas").insert(dados).execute()
    return resposta.data[0] if resposta.data else None

def atualizar_status_parada(parada_id: str, novo_status: str):
    supabase = get_supabase()
    supabase.table("paradas").update({"status": novo_status}).eq("id", parada_id).execute()

# -------------------- OCORRÊNCIAS --------------------
def inserir_ocorrencias(ocorrencias: list) -> list:
    supabase = get_supabase()
    # Adicionar enviado_por
    for occ in ocorrencias:
        occ["enviado_por"] = st.session_state["usuario"]["id"]
    resposta = supabase.table("ocorrencias").insert(ocorrencias).execute()
    return resposta.data

def listar_ocorrencias_por_parada(parada_id: str) -> List[Dict]:
    supabase = get_supabase()
    resposta = supabase.table("ocorrencias").select("*").eq("parada_id", parada_id).execute()
    return resposta.data

def classificar_ocorrencia(ocorrencia_id: str, g: int, u: int, t: int):
    supabase = get_supabase()
    from utils.gut_calculator import calcular_gut
    gut = calcular_gut(g, u, t)
    data = {
        "gravidade": g,
        "urgencia": u,
        "tendencia": t,
        "classificacao": gut["nivel"]
    }
    supabase.table("ocorrencias").update(data).eq("id", ocorrencia_id).execute()

def classificar_ocorrencias_bulk(ocorrencias: List[Dict]):
    supabase = get_supabase()
    for occ in ocorrencias:
        supabase.table("ocorrencias").update(occ).eq("id", occ["id"]).execute()

# -------------------- AÇÕES --------------------
def criar_acao(dados: dict) -> dict:
    supabase = get_supabase()
    resposta = supabase.table("acoes").insert(dados).execute()
    return resposta.data[0] if resposta.data else None

def listar_acoes(filtros: dict = None) -> List[Dict]:
    supabase = get_supabase()
    query = supabase.table("acoes").select("*, ocorrencias(*), paradas(*), usuarios:responsavel_id(*)")
    if filtros:
        for chave, valor in filtros.items():
            if valor is not None:
                query = query.eq(chave, valor)
    resposta = query.execute()
    return resposta.data

def atualizar_acao(acao_id: str, status: str, comentario: str = None):
    supabase = get_supabase()
    data = {"status": status}
    if comentario:
        data["comentarios"] = comentario
    if status == "concluido":
        data["data_conclusao"] = date.today().isoformat()
    resposta = supabase.table("acoes").update(data).eq("id", acao_id).execute()
    return resposta.data

def listar_acoes_vencidas() -> List[Dict]:
    supabase = get_supabase()
    hoje = date.today().isoformat()
    resposta = supabase.table("acoes").select("*").lt("prazo", hoje).neq("status", "concluido").execute()
    return resposta.data

# -------------------- USUÁRIOS --------------------
def listar_usuarios(perfil: Optional[str] = None) -> List[Dict]:
    supabase = get_supabase()
    query = supabase.table("perfis_usuarios").select("*")
    if perfil:
        query = query.eq("perfil", perfil)
    resposta = query.execute()
    return resposta.data

def get_usuario(user_id: str) -> dict:
    supabase = get_supabase()
    resposta = supabase.table("perfis_usuarios").select("*").eq("id", user_id).execute()
    return resposta.data[0] if resposta.data else None

# -------------------- CONTRATOS --------------------
def listar_contratos() -> List[Dict]:
    supabase = get_supabase()
    resposta = supabase.table("contratos").select("*").execute()
    return resposta.data
