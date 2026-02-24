# pages/5_⚙️_Admin.py
import streamlit as st
import pandas as pd
from utils.auth import verificar_permissao, usuario_logado
from utils.db_queries import listar_contratos, listar_paradas, listar_usuarios
from utils.supabase_client import get_supabase
from datetime import date

verificar_permissao(["admin"])

st.set_page_config(layout="wide")
st.markdown("<div class='page-header'><h1>⚙️ Administração do Sistema</h1></div>", unsafe_allow_html=True)

supabase = get_supabase()

tab1, tab2, tab3 = st.tabs(["📋 Contratos", "🏗️ Paradas", "👥 Usuários"])

# ------------------------------------------------------------
# TAB 1: GERENCIAR CONTRATOS
# ------------------------------------------------------------
with tab1:
    st.subheader("Contratos")
    
    with st.expander("➕ Novo Contrato"):
        with st.form("novo_contrato"):
            codigo = st.text_input("Código do Contrato", placeholder="Ex: CON-2025-001")
            nome = st.text_input("Nome do Contrato", placeholder="Ex: Refinaria X - Parada Geral")
            responsavel = st.text_input("Responsável", placeholder="Nome do responsável")
            submitted = st.form_submit_button("Salvar")
            if submitted:
                if codigo and nome and responsavel:
                    try:
                        supabase.table("contratos").insert({
                            "codigo": codigo,
                            "nome": nome,
                            "responsavel": responsavel
                        }).execute()
                        st.success("Contrato criado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar contrato: {e}")
                else:
                    st.error("Preencha todos os campos.")
    
    contratos = listar_contratos()
    if contratos:
        df_contratos = pd.DataFrame(contratos)
        if 'criado_em' in df_contratos.columns:
            df_contratos = df_contratos.drop(columns=['criado_em'])
        st.dataframe(df_contratos, use_container_width=True)
        
        with st.expander("✏️ Editar / Excluir Contrato"):
            contrato_selecionado = st.selectbox(
                "Selecione o contrato",
                options=contratos,
                format_func=lambda c: f"{c['codigo']} - {c['nome']}"
            )
            if contrato_selecionado:
                col1, col2 = st.columns(2)
                with col1:
                    with st.form("editar_contrato"):
                        novo_codigo = st.text_input("Código", value=contrato_selecionado['codigo'])
                        novo_nome = st.text_input("Nome", value=contrato_selecionado['nome'])
                        novo_responsavel = st.text_input("Responsável", value=contrato_selecionado['responsavel'])
                        if st.form_submit_button("Atualizar"):
                            try:
                                supabase.table("contratos").update({
                                    "codigo": novo_codigo,
                                    "nome": novo_nome,
                                    "responsavel": novo_responsavel
                                }).eq("id", contrato_selecionado['id']).execute()
                                st.success("Contrato atualizado!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
                with col2:
                    if st.button("🗑️ Excluir Contrato", type="secondary"):
                        paradas_associadas = supabase.table("paradas").select("*").eq("contrato_id", contrato_selecionado['id']).execute()
                        if paradas_associadas.data:
                            st.warning("Não é possível excluir: existem paradas vinculadas a este contrato.")
                        else:
                            try:
                                supabase.table("contratos").delete().eq("id", contrato_selecionado['id']).execute()
                                st.success("Contrato excluído!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
    else:
        st.info("Nenhum contrato cadastrado.")

# ------------------------------------------------------------
# TAB 2: GERENCIAR PARADAS
# ------------------------------------------------------------
with tab2:
    st.subheader("Paradas")
    
    contratos_list = listar_contratos()
    if not contratos_list:
        st.warning("Cadastre um contrato antes de criar uma parada.")
    else:
        with st.expander("➕ Nova Parada"):
            with st.form("nova_parada"):
                contrato_id = st.selectbox(
                    "Contrato",
                    options=contratos_list,
                    format_func=lambda c: f"{c['codigo']} - {c['nome']}"
                )
                responsavel = st.text_input("Responsável pela Parada")
                data_inicio = st.date_input("Data de Início", value=date.today())
                data_fim = st.date_input("Data de Fim", value=date.today())
                status = st.selectbox(
                    "Status",
                    options=['coleta', 'classificacao', 'plano_acao', 'monitoramento', 'encerrada']
                )
                submitted = st.form_submit_button("Criar Parada")
                if submitted:
                    if responsavel and data_inicio and data_fim:
                        dados = {
                            "contrato_id": contrato_id['id'],
                            "responsavel": responsavel,
                            "data_inicio": data_inicio.isoformat(),
                            "data_fim": data_fim.isoformat(),
                            "status": status,
                            "criado_por": usuario_logado()['id']
                        }
                        try:
                            supabase.table("paradas").insert(dados).execute()
                            st.success("Parada criada com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                    else:
                        st.error("Preencha todos os campos obrigatórios.")
        
        paradas = listar_paradas()
        if paradas:
            for p in paradas:
                p['contrato_nome'] = next((c['codigo'] for c in contratos_list if c['id'] == p['contrato_id']), '')
            df_paradas = pd.DataFrame(paradas)
            colunas = ['contrato_nome', 'responsavel', 'data_inicio', 'data_fim', 'status', 'criado_em']
            df_paradas = df_paradas[[c for c in colunas if c in df_paradas.columns]]
            st.dataframe(df_paradas, use_container_width=True)
            
            with st.expander("✏️ Editar / Excluir Parada"):
                parada_selecionada = st.selectbox(
                    "Selecione a parada",
                    options=paradas,
                    format_func=lambda p: f"{p.get('contrato_nome', '')} - {p['responsavel']} ({p['data_inicio']} a {p['data_fim']})"
                )
                if parada_selecionada:
                    col1, col2 = st.columns(2)
                    with col1:
                        with st.form("editar_parada"):
                            novo_contrato_id = st.selectbox(
                                "Contrato",
                                options=contratos_list,
                                format_func=lambda c: f"{c['codigo']} - {c['nome']}",
                                index=next((i for i, c in enumerate(contratos_list) if c['id'] == parada_selecionada['contrato_id']), 0)
                            )
                            novo_responsavel = st.text_input("Responsável", value=parada_selecionada['responsavel'])
                            nova_data_inicio = st.date_input("Data Início", value=pd.to_datetime(parada_selecionada['data_inicio']).date())
                            nova_data_fim = st.date_input("Data Fim", value=pd.to_datetime(parada_selecionada['data_fim']).date())
                            novo_status = st.selectbox(
                                "Status",
                                options=['coleta', 'classificacao', 'plano_acao', 'monitoramento', 'encerrada'],
                                index=['coleta', 'classificacao', 'plano_acao', 'monitoramento', 'encerrada'].index(parada_selecionada['status'])
                            )
                            if st.form_submit_button("Atualizar"):
                                dados = {
                                    "contrato_id": novo_contrato_id['id'],
                                    "responsavel": novo_responsavel,
                                    "data_inicio": nova_data_inicio.isoformat(),
                                    "data_fim": nova_data_fim.isoformat(),
                                    "status": novo_status
                                }
                                try:
                                    supabase.table("paradas").update(dados).eq("id", parada_selecionada['id']).execute()
                                    st.success("Parada atualizada!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")
                    with col2:
                        if st.button("🗑️ Excluir Parada", type="secondary"):
                            ocorrencias = supabase.table("ocorrencias").select("*").eq("parada_id", parada_selecionada['id']).execute()
                            if ocorrencias.data:
                                st.warning("Não é possível excluir: existem ocorrências vinculadas a esta parada.")
                            else:
                                try:
                                    supabase.table("paradas").delete().eq("id", parada_selecionada['id']).execute()
                                    st.success("Parada excluída!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")
        else:
            st.info("Nenhuma parada cadastrada.")

# ------------------------------------------------------------
# TAB 3: GERENCIAR PERFIS DE USUÁRIOS
# ------------------------------------------------------------
with tab3:
    st.subheader("Perfis de Usuários")
    st.markdown("Aqui você pode visualizar e editar os perfis dos usuários. Para criar um novo usuário, primeiro crie-o no **Authentication** do Supabase e depois associe um perfil aqui.")
    
    perfis = listar_usuarios()
    if perfis:
        df_perfis = pd.DataFrame(perfis)
        st.dataframe(df_perfis[['nome', 'email', 'perfil', 'setor', 'ativo']], use_container_width=True)
        
        with st.expander("✏️ Editar Perfil de Usuário"):
            perfil_selecionado = st.selectbox(
                "Selecione o usuário",
                options=perfis,
                format_func=lambda u: f"{u['nome']} ({u['email']})"
            )
            if perfil_selecionado:
                with st.form("editar_perfil"):
                    nome = st.text_input("Nome", value=perfil_selecionado['nome'])
                    email = st.text_input("E-mail", value=perfil_selecionado['email'], disabled=True)
                    perfil = st.selectbox(
                        "Perfil",
                        options=['admin', 'pmo', 'setor', 'gestor'],
                        index=['admin', 'pmo', 'setor', 'gestor'].index(perfil_selecionado['perfil'])
                    )
                    setor = st.text_input("Setor (apenas para perfil setor)", value=perfil_selecionado.get('setor', ''))
                    ativo = st.checkbox("Ativo", value=perfil_selecionado.get('ativo', True))
                    submitted = st.form_submit_button("Atualizar Perfil")
                    if submitted:
                        dados = {
                            "nome": nome,
                            "perfil": perfil,
                            "setor": setor if perfil == 'setor' else None,
                            "ativo": ativo
                        }
                        try:
                            supabase.table("perfis_usuarios").update(dados).eq("id", perfil_selecionado['id']).execute()
                            st.success("Perfil atualizado!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
    else:
        st.info("Nenhum perfil de usuário cadastrado.")
    
    st.subheader("Associar Perfil a Novo Usuário (Auth)")
    st.markdown("Se você já criou um usuário no Authentication do Supabase e ele ainda não tem perfil, informe o ID do usuário e os dados abaixo.")
    with st.form("novo_perfil"):
        user_id = st.text_input("UUID do usuário (do Auth)", placeholder="Cole o UUID aqui")
        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail (deve ser o mesmo usado no Auth)")
        perfil = st.selectbox("Perfil", ['admin', 'pmo', 'setor', 'gestor'])
        setor = st.text_input("Setor (se perfil setor)", value="")
        ativo = st.checkbox("Ativo", value=True)
        submitted = st.form_submit_button("Criar Perfil")
        if submitted:
            if user_id and nome and email:
                existente = supabase.table("perfis_usuarios").select("*").eq("id", user_id).execute()
                if existente.data:
                    st.error("Já existe um perfil para este usuário.")
                else:
                    dados = {
                        "id": user_id,
                        "nome": nome,
                        "email": email,
                        "perfil": perfil,
                        "setor": setor if perfil == 'setor' else None,
                        "ativo": ativo
                    }
                    try:
                        supabase.table("perfis_usuarios").insert(dados).execute()
                        st.success("Perfil criado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
            else:
                st.error("Preencha UUID, nome e e-mail.")
