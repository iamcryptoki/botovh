#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tiny bot for registering specific domain names
when they become available for registration.

Usage:
    botovh.py [DOMAINS ...] [--file=f] [--help] [--key] [--log=l] [--payment=p] [--version]

Options:
    -f --file=f             Specify a file containing a list of domain names.
    -h --help               Show this message.
    -k --key                Request a new OVH consumer key.
    -l --log=l              Specify the location where you want to store the log file. [default: .]
    -p --payment=p          Specify your preferred payment method: 
                            bankAccount, creditCard, fidelityAccount, ovhAccount or paypal.
    -v --version            Show version.
"""

import configparser
import logging
import os
import sys
import ovh

from docopt import docopt

__version__ = '0.1.1'

def run(account, domains, payment_mean):
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

            logging.info("[%s] Available domain name. Order #%s (%s) has been generated.",
                         domain, order_id, salesorder['prices']['withTax']['text'])

            # Retrieve available payment means.
            payment_means = account.get_payment_means(domain, order_id)
            if not payment_means:
                logging.error("[%s] Not registered payment means available. "
                              "Can't pay this order automatically.", domain)
                sys.exit(1)
            if payment_mean is None or payment_mean not in payment_means:
                payment_mean = payment_means[0]['paymentMean']

            # Pay with an already registered payment mean.
            payment_mean_id = account.get_payment_mean_id(domain, payment_mean)[0]
            account.pay(domain, order_id, payment_mean, payment_mean_id)

class Account(object):
    def __init__(self):
        self.client = ovh.Client()

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
            logging.error("[%s] Unable to generate the order: %s", domain, str(e))
            sys.exit(1)

    def get_payment_means(self, domain, order_id):
        """
        Retrieve available payment means.
        """
        try:
            return self.client.get("/me/order/{0}/availableRegisteredPaymentMean".format(order_id))
        except ovh.exceptions.APIError as e:
            logging.error("[%s] Unable to retrieve order payment means: %s", domain, str(e))
            sys.exit(1)

    def get_payment_mean_id(self, domain, payment_mean):
        try:
            return self.client.get("/me/paymentMean/{0}".format(payment_mean))
        except ovh.exceptions.APIError as e:
            logging.error("[%s] %s", domain, str(e))
            sys.exit(1)

    def pay(self, domain, order_id, payment_mean, payment_mean_id):
        """
        Pay with an already registered payment mean.
        """
        try:
            self.client.post("/me/order/{0}/payWithRegisteredPaymentMean"
                             .format(order_id),
                             paymentMean=payment_mean,
                             paymentMeanId=payment_mean_id)
            logging.info("[%s] Payment successful. "
                         "Congratulations on purchasing a new domain name!", domain)
            """
            COMPLETED! You should receive a confirmation email from OVH
            confirming that you are the legal registrant! :)
            """
        except ovh.exceptions.APIError as e:
            logging.error("[%s] Payment of your order haven't been successful: %s", domain, str(e))
            sys.exit(1)

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

def configure_logging(path):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create console handler and set level to info.
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Create log file handler and set level to error.
    handler = logging.FileHandler(os.path.join(path, 'botovh.log'), 'w', encoding=None, delay='true')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def main():
    args = docopt(__doc__, version=__version__)

    log = args['--log']
    if not os.path.exists(log):
        os.makedirs(log)
    configure_logging(log)

    # Read the configuration file.
    conf = configparser.RawConfigParser()
    conf.read('ovh.conf')

    if args['--key']:
        Account().request_consumer_key()
        sys.exit(0)
    elif args['DOMAINS']:
        domains = args['DOMAINS']
    elif args['--file'] is not None:
        try:
            with open(args['--file']) as f:
                domains = f.read().splitlines()
        except FileNotFoundError:
            logging.error("File not found. Please input the path of an existing file.")
            sys.exit(1)

    run(Account(), domains, args['--payment'])

if __name__ == '__main__':
    main()
