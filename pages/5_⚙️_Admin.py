import streamlit as st
import pandas as pd
from utils.auth import verificar_permissao, usuario_logado, criar_usuario_auth
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

# ---------- Usuários (criação completa) ----------
with tab3:
    st.subheader("Criar Novo Usuário (Auth + Perfil)")
    with st.form("novo_usuario"):
        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        perfil = st.selectbox("Perfil", ['admin', 'pmo', 'setor', 'gestor'])
        setor = st.text_input("Setor (apenas para perfil setor)")
        if st.form_submit_button("Criar Usuário"):
            if not nome or not email or not senha:
                st.error("Preencha nome, e-mail e senha.")
            else:
                try:
                    # 1. Criar no Auth
                    user = criar_usuario_auth(email, senha, {"nome": nome})
                    user_id = user['id']
                    # 2. Inserir perfil
                    dados_perfil = {
                        "id": user_id,
                        "nome": nome,
                        "email": email,
                        "perfil": perfil,
                        "setor": setor if perfil == 'setor' else None,
                        "ativo": True
                    }
                    supabase.table("perfis_usuarios").insert(dados_perfil).execute()
                    st.success(f"Usuário {nome} criado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

# ---------- Perfis (visualização e edição) ----------
with tab4:
    st.subheader("Gerenciar Perfis de Usuários")
    perfis = listar_usuarios()
    if perfis:
        df = pd.DataFrame(perfis)
        st.dataframe(df[['nome', 'email', 'perfil', 'setor', 'ativo']])

        st.subheader("Editar Perfil")
        user_selected = st.selectbox("Selecione o usuário", perfis, format_func=lambda u: u['nome'])
        if user_selected:
            with st.form("editar_perfil"):
                novo_nome = st.text_input("Nome", value=user_selected['nome'])
                novo_perfil = st.selectbox("Perfil", ['admin', 'pmo', 'setor', 'gestor'], index=['admin','pmo','setor','gestor'].index(user_selected['perfil']))
                novo_setor = st.text_input("Setor", value=user_selected.get('setor', ''))
                ativo = st.checkbox("Ativo", value=user_selected['ativo'])
                if st.form_submit_button("Atualizar"):
                    dados = {
                        "nome": novo_nome,
                        "perfil": novo_perfil,
                        "setor": novo_setor if novo_perfil == 'setor' else None,
                        "ativo": ativo
                    }
                    supabase.table("perfis_usuarios").update(dados).eq("id", user_selected['id']).execute()
                    st.success("Perfil atualizado!")
                    st.rerun()
    else:
        st.info("Nenhum perfil cadastrado.")
