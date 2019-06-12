#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ssl

import smtplib
from email.mime.text import MIMEText


class Email(object):
    def __init__(self, host, port=465, user='', password=''):
        self.host = host
        self.port = port
        self.user = user
        self.password = password


    def send(self, send_from, send_to, body):
        """Create a secure connection to the server and send an email."""
        message = self.create_message(send_from, send_to, body)
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
            server.login(self.user, self.password)
            server.sendmail(
                from_addr=send_from,
                to_addrs=send_to.split(','),
                msg=message.as_string())


    def create_message(self, send_from, send_to, body):
        """Create the plain-text version of the message."""

        body = (
            f"\n{body}\n\n"
            "— BotOVH"
        )

        message = MIMEText(body, 'plain', _charset='utf-8')
        message['From'] = f"BotOVH <{send_from}>"
        message['To'] = send_to

        if "Congratulations" in body:
            subject = "Congratulations, you're the proud owner of a new domain name!"
        else:
            subject = "Notification"

        message['subject'] = subject

        return message
