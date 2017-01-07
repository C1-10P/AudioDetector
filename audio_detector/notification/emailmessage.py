import smtplib
from email.mime.multipart import MIMEMultipart
import os
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import logging


class EmailMessage(object):
    def __init__(self, config):
        self._config = config

        self._msg = MIMEMultipart()
        self._msg["From"] = config.email.from_email
        self._msg["Subject"] = config.email.subject

    def contents(self, contents):
        

        text = MIMEText(contents, "plain")
        self._msg.attach(text)

    def attach(self, file_path):


        att = MIMEBase("application", "octet-stream")
        with open(file_path, "rb") as fp:
            att.set_payload(fp.read())

        att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))

        self._msg.attach(att)

    def send(self):
        logging.debug('EmailMessage->send')
        addresses = self._config.email.mail_list
        self._smtp = smtplib.SMTP(self._config.email.host, self._config.email.port)
        self._smtp.starttls()
        self._smtp.login(self._config.email.username, self._config.email.password)

        self._msg["To"] = ", ".join(addresses)

        try:
            self._smtp.sendmail(self._msg["From"],self._msg["To"], self._msg.as_string())
            self._smtp.quit()
        except Exception as error:
            print "Cannot send email: " + str(error)
