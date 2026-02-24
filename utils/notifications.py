import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_email(destinatario: str, assunto: str, corpo_html: str):
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
    assunto = f"[Contrex] Nova ação atribuída"
    corpo = f"""
    <h2>Olá {nome},</h2>
    <p>Você foi designado responsável por uma ação no projeto <strong>{projeto}</strong>:</p>
    <p><strong>Ação:</strong> {acao}</p>
    <p><strong>Prazo:</strong> {prazo}</p>
    <p>Acesse o sistema para mais detalhes e para marcar como executada.</p>
    """
    return enviar_email(email, assunto, corpo)

def notificar_pmo_nova_ocorrencia(emails_pmo: list, setor: str, projeto: str):
    assunto = f"[Contrex] Nova ocorrência enviada por {setor}"
    corpo = f"<p>O setor <strong>{setor}</strong> enviou uma nova ocorrência para o projeto <strong>{projeto}</strong>.</p>"
    for email in emails_pmo:
        enviar_email(email, assunto, corpo)
