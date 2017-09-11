#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import logging
import os
import ovh
import smtplib

from argparse import ArgumentParser
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twilio.rest import Client as twilio_client

def run(domains):
    for domain in domains:
        # Create a new cart and assign to current user.
        cart_id = account.create_cart()
        # Add domain item to the cart.
        try:
            result = account.add_to_cart(domain, cart_id)
        except ovh.exceptions.APIError:
            continue
        if result.get('offerId'):
            # Generate a salesorder.
            salesorder = account.generate_salesorder(domain, cart_id)
            order_id = salesorder['orderId']

            # Send SMS notification
            if 'phone' in ntf:
                msg = ("{0} is available. Order #{1} ({2}) has been generated."
                       .format(domain, order_id, salesorder['prices']['withTax']['text']))
                sms.send(domain, msg)

            # Retrieve available payment means.
            payment_means = account.get_payment_means(domain, order_id)
            if not payment_means:
                msg = "Not registered payment means available. Can't pay this order automatically."
                error(domain, msg)
            if len(payment_means) > 1:
                for p in payment_means:
                    if p['paymentMean'] == conf['default']['payment']:
                        payment_mean = p['paymentMean']
            if payment_mean is None:
                payment_mean = payment_means[0]['paymentMean']

            # Pay with an already registered payment mean.
            payment_mean_id = account.get_payment_mean_id(domain, payment_mean)[0]
            account.pay(domain, order_id, payment_mean, payment_mean_id)

            # Remove purchased domain name from the list.
            f = open(domains_file, 'w')
            for dn in domains:
                if dn != domain:
                    f.write(dn+'\n')
            f.close()

def error(domain, msg):
    """
    Log errors to a file and send email notification.
    """
    msg = ("[{0}] domain={1}, message={2}"
           .format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), domain, msg))
    # Append the message to the log file.
    logging.basicConfig(filename=conf['default']['logs'], level=logging.ERROR)
    logging.error(msg)

    # Send email notification.
    if 'email' in ntf:
        msg = email.build(domain, "Exception Notification", msg)
        email.send(msg)
    exit(1)

class Account(object):
    def __init__(self, conf):
        self.client = ovh.Client(config_file=conf)

    def create_cart(self):
        """
        Create a new cart and assign to current user.
        """
        cart = self.client.post("/order/cart", ovhSubsidiary='FR', _need_auth=False)
        cart_id = cart.get('cartId')
        self.client.post("/order/cart/{0}/assign".format(cart_id))
        return cart_id

    def add_to_cart(self, domain, cart_id):
        """
        Add domain item to the cart.
        """
        return self.client.post("/order/cart/{0}/domain".format(cart_id), domain=domain)

    def generate_salesorder(self, domain, cart_id):
        """
        Generate a salesorder.
        """
        try:
            return self.client.post("/order/cart/{0}/checkout".format(cart_id))
        except ovh.exceptions.APIError as e:
            error(domain, "Unable to generate the order: %s" % str(e))

    def get_payment_means(self, domain, order_id):
        """
        Retrieve available payment means.
        """
        try:
            return self.client.get("/me/order/{0}/availableRegisteredPaymentMean".format(order_id))
        except ovh.exceptions.APIError as e:
            error(domain, "Unable to retrieve order payment means: %s" % str(e))

    def get_payment_mean_id(self, domain, payment_mean):
        try:
            return self.client.get("/me/paymentMean/{0}".format(payment_mean))
        except ovh.exceptions.APIError as e:
            error(domain, str(e))

    def pay(self, domain, order_id, payment_mean, payment_mean_id):
        """
        Pay with an already registered payment mean.
        """
        try:
            self.client.post("/me/order/{0}/payWithRegisteredPaymentMean"
                             .format(order_id),
                             paymentMean=payment_mean,
                             paymentMeanId=payment_mean_id)

            # Send SMS notification
            if 'phone' in ntf:
                msg = "Payment successful. Congratulations on purchasing your new domain name %s! " % domain
                sms.send(domain, msg)
        except ovh.exceptions.APIError as e:
            error(domain, "Payment of your order haven't been successful: %s" % str(e))

    def request_consumer_key(self):
        """
        Request a new consumer key.
        """
        ck = self.client.new_consumer_key_request()
        ck.add_recursive_rules(ovh.API_READ_WRITE, '/')
        validation = ck.request()

        print("1. Please visit %s to authenticate." % validation['validationUrl'])
        input("2. Press Enter to continue...\n")
        print("Welcome %s!" % self.client.get('/me')['firstname'])
        print("Your consumer key is '%s'" % validation['consumerKey'])

class Email(object):
    def __init__(self):
        self.smtp = conf['smtp']
        self.ntf = conf['notification']

    def build(self, domain, subject, body, email_type='plain', charset='utf-8'):
        """
        Create the container email message.
        """
        msg = MIMEMultipart()
        msg['From'] = self.smtp['username']
        msg['To'] = self.ntf['email']
        msg['Subject'] = "[BotOvh][{0}] {1}".format(domain, subject)
        msg.attach(MIMEText(body, email_type, charset))
        msg = msg.as_string()
        return msg

    def send(self, msg):
        """
        Send the email message using SMTP.
        """
        server = smtplib.SMTP(self.smtp['host'], self.smtp['port'])
        server.ehlo()
        server.starttls()
        server.login(self.smtp['username'], self.smtp['password'])
        server.sendmail(self.smtp['username'], self.ntf['email'], msg)
        server.quit()

class Twilio(object):
    def __init__(self):
        self.env = conf['twilio']['environment']

    def auth(self):
        twilio = conf['twilio.%s' % self.env]
        account_sid = twilio['account_sid']
        auth_token = twilio['auth_token']
        client = twilio_client(account_sid, auth_token)

        account = {
            'account_sid' : account_sid,
            'auth_token'  : auth_token,
            'client'      : client,
            'sender'      : twilio['sender']
        }

        return account

    def send(self, domain, body):
        """
        Send SMS message.
        """
        twilio = self.auth()
        client = twilio['client']
        sender = twilio['sender']

        message = client.messages.create(
            to=conf['notification']['phone'],
            from_=sender,
            body="BotOvh: {0}".format(body)
        )

        return message.sid

if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('-a', '--authenticate', action='store_true', help="Request a new consumer key.")
    auth = vars(p.parse_args())['authenticate']

    conf = configparser.RawConfigParser()
    conf.read('bot.conf')
    conf_ovh = conf['default']['ovh']
    domains_file = conf['default']['domains']
    ntf = conf['notification']
    email = Email()
    sms = Twilio()

    if conf_ovh is not None:
        account = Account(conf_ovh)
        if auth:
            account.request_consumer_key()
        elif domains_file is not None:
            with open(domains_file) as f:
                domains = f.read()
                f.close()
            run(domains.splitlines())
