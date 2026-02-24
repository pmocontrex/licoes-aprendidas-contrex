import streamlit as st
import pandas as pd
from utils.auth import verificar_permissao, usuario_logado
from utils.db_queries import listar_contratos, listar_paradas, listar_usuarios, criar_parada, atualizar_parada
from utils.supabase_client import get_supabase
from datetime import date

verificar_permissao(["admin"])

st.markdown("<div class='page-header'><h1>⚙️ Administração</h1></div>", unsafe_allow_html=True)

supabase = get_supabase()

tab1, tab2, tab3, tab4 = st.tabs(["Contratos", "Projetos", "Usuários", "Perfis"])

# ---------- Contratos ----------
with tab1:
    st.subheader("Contratos")
    with st.expander("➕ Novo Contrato"):
        with st.form("novo_contrato"):
            cod = st.text_input("Código")
            nome = st.text_input("Nome")
            resp = st.text_input("Responsável")
            if st.form_submit_button("Salvar"):
                supabase.table("contratos").insert({"codigo": cod, "nome": nome, "responsavel": resp}).execute()
                st.success("Contrato criado!")
                st.rerun()
    contratos = listar_contratos()
    if contratos:
        df = pd.DataFrame(contratos)
        st.dataframe(df[['codigo', 'nome', 'responsavel']])

# ---------- Projetos ----------
with tab2:
    st.subheader("Projetos (Paradas)")
    contratos_list = listar_contratos()
    if not contratos_list:
        st.warning("Cadastre um contrato primeiro.")
    else:
        with st.expander("➕ Novo Projeto"):
            with st.form("novo_projeto"):
                contrato = st.selectbox("Contrato", contratos_list, format_func=lambda c: c['codigo'])
                resp = st.text_input("Responsável")
                inicio = st.date_input("Início")
                fim = st.date_input("Fim")
                aberto = st.checkbox("Coleta aberta?", value=True)
                if st.form_submit_button("Criar"):
                    dados = {
                        "contrato_id": contrato['id'],
                        "responsavel": resp,
                        "data_inicio": inicio.isoformat(),
                        "data_fim": fim.isoformat(),
                        "coleta_aberta": aberto,
                        "status": "coleta"
                    }
                    criar_parada(dados)
                    st.success("Projeto criado!")
                    st.rerun()

        projetos = listar_paradas()
        if projetos:
            df = pd.DataFrame(projetos)
            df['contrato'] = df['contratos'].apply(lambda x: x['codigo'] if x else '')
            st.dataframe(df[['contrato', 'responsavel', 'data_inicio', 'data_fim', 'coleta_aberta', 'status']])

            # Editar coleta_aberta
            st.subheader("Abrir/Fechar Coleta")
            proj = st.selectbox("Selecione o projeto", projetos, format_func=lambda p: f"{p['contratos']['codigo']} - {p['responsavel']}")
            nova_situacao = st.checkbox("Coleta aberta?", value=proj['coleta_aberta'])
            if st.button("Atualizar"):
                atualizar_parada(proj['id'], {"coleta_aberta": nova_situacao})
                st.success("Atualizado!")
                st.rerun()

# ---------- Usuários (Auth) ----------
with tab3:
    st.subheader("Criar usuário no Auth")
    st.markdown("Use o painel do Supabase para criar usuários. Após criar, associe o perfil na aba 'Perfis'.")

# ---------- Perfis ----------
with tab4:
    st.subheader("Gerenciar Perfis de Usuários")
    perfis = listar_usuarios()
    if perfis:
        df = pd.DataFrame(perfis)
        st.dataframe(df[['nome', 'email', 'perfil', 'setor', 'ativo']])

    st.subheader("Associar Perfil a um usuário existente")
    with st.form("novo_perfil"):
        user_id = st.text_input("UUID do usuário (do Auth)")
        nome = st.text_input("Nome")
        email = st.text_input("E-mail")
        perfil = st.selectbox("Perfil", ['admin', 'pmo', 'setor', 'gestor'])
        setor = st.text_input("Setor (se for setor)")
        ativo = st.checkbox("Ativo", value=True)
        if st.form_submit_button("Salvar"):
            dados = {
                "id": user_id,
                "nome": nome,
                "email": email,
                "perfil": perfil,
                "setor": setor if perfil == 'setor' else None,
                "ativo": ativo
            }
            supabase.table("perfis_usuarios").insert(dados).execute()
            st.success("Perfil criado!")
            st.rerun()
