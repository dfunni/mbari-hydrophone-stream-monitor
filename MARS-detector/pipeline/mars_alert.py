import smtplib, ssl
from email.mime.text import MIMEText
import os
from getpass import getpass

def send_email(subject, body,
         sender='devfunni@gmail.com',
         receiver='devfunni@gmail.com'):

    password = os.environ.get('MAIL_PASSWORD')
    port = 465 # for SSL
    smtp_server = "smtp.gmail.com"

    msg = MIMEText(body)
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject 

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())