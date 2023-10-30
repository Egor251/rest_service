# Модули для формирования письма
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import time
from dotenv import load_dotenv
import os


class Email_send:

    load_dotenv()

    my_mail = os.environ.get("SMTP_LOGIN")
    my_password = os.environ.get("PASSWORD")
    SMTP_server = os.environ.get("SMTP_SERVER")
    SMTP_port = os.environ.get("SMTP_PORT")

    def send_email(self, adr, subject, body):
        print('Sending email')
        smtpobj = smtplib.SMTP_SSL(self.SMTP_server, int(self.SMTP_port))
        smtpobj.login(self.my_mail, self.my_password)

        sender_email = os.environ.get("SMTP_EMAIL")

        # Создание составного сообщения и установка заголовка
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = adr
        message["Subject"] = subject
        # message["Bcc"] = receiver_email   Если у вас несколько получателей

        # Внесение тела письма
        message.attach(MIMEText(body, "plain"))
        text = message.as_string()

        smtpobj.sendmail(sender_email, adr, text)
