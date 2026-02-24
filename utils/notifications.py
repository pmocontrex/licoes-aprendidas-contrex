# utils/notifications.py
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_email(destinatario: str, assunto: str, corpo_html: str):
    """Envia e-mail usando as configurações SMTP do secrets.toml."""
    try:
        smtp_config = st.secrets["smtp"]
        msg = MIMEMultipart()
        msg["From"] = smtp_config["from"]
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo_html, "html"))

        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            server.starttls()
            server.login(smtp_config["user"], smtp_config["password"])
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")
        return False

def notificar_responsavel_acao(email: str, nome: str, acao: str, prazo: str, projeto: str):
    assunto = f"[Contrex] Nova ação atribuída: {acao[:50]}..."
    corpo = f"""
    <html>
    <body>
        <h2>Olá {nome},</h2>
        <p>Você foi designado como responsável por uma ação no projeto <strong>{projeto}</strong>.</p>
        <p><strong>Ação:</strong> {acao}</p>
        <p><strong>Prazo:</strong> {prazo}</p>
        <p>Acesse o sistema para mais detalhes e para atualizar o status.</p>
        <br>
        <p>Atenciosamente,<br>Equipe PMO - Contrex Engenharia</p>
    </body>
    </html>
    """
    return enviar_email(email, assunto, corpo)

def notificar_pmo_envio_formulario(email_pmo: str, setor: str, parada: str):
    assunto = f"[Contrex] Novo formulário enviado por {setor}"
    corpo = f"""
    <html>
    <body>
        <h2>Novo envio de ocorrências</h2>
        <p>O setor <strong>{setor}</strong> enviou o formulário de lições aprendidas para a parada <strong>{parada}</strong>.</p>
        <p>Acesse o sistema para classificar as ocorrências.</p>
        <br>
        <p>Atenciosamente,<br>Sistema de Lições Aprendidas</p>
    </body>
    </html>
    """
    return enviar_email(email_pmo, assunto, corpo)

def notificar_plano_publicado(emails_responsaveis: list, parada: str):
    assunto = f"[Contrex] Plano de Ação publicado para a parada {parada}"
    corpo = f"""
    <html>
    <body>
        <h2>Plano de Ação publicado</h2>
        <p>O plano de ação da parada <strong>{parada}</strong> foi publicado.</p>
        <p>Verifique suas ações pendentes no sistema.</p>
        <br>
        <p>Atenciosamente,<br>Equipe PMO</p>
    </body>
    </html>
    """
    for email in emails_responsaveis:
        enviar_email(email, assunto, corpo)
