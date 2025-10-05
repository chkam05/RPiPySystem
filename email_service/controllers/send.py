import smtplib
from email.message import EmailMessage
from flask import Blueprint, request, jsonify
from ..config import SMTP_HOST, SMTP_PORT, SMTP_FROM

send_bp = Blueprint('email_send', __name__, url_prefix='/api/email')

@send_bp.post('')
def send_mail():
    data = request.get_json(force=True)
    msg = EmailMessage()
    msg['From'] = SMTP_FROM
    msg['To'] = data['to']
    msg['Subject'] = data.get('subject', '(no subject)')
    msg.set_content(data.get('body', ''))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.send_message(msg)
    return jsonify({'ok': True})
