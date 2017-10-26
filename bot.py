#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import logging
import os
import sys
import ovh

from argparse import ArgumentParser

REGISTERED = []

def run(conf, account, domains):
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
            if len(payment_means) > 1:
                for p in payment_means:
                    if p['paymentMean'] == conf['default']['payment']:
                        payment_mean = p['paymentMean']
            if payment_mean is None:
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
            REGISTERED.append(domain)
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

def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create console handler and set level to info.
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Create log file handler and set level to error.
    handler = logging.FileHandler(os.path.join('.', "bot.log"), 'w', encoding=None, delay='true')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def main():
    p = ArgumentParser()
    p.add_argument('-a', '--authenticate', action='store_true', help="Request a new consumer key.")
    auth = vars(p.parse_args())['authenticate']

    # Read the configuration file.
    conf = configparser.RawConfigParser()
    conf.read('ovh.conf')
    domains_path = conf['default']['domains']

    # Configure logging.
    configure_logging()

    if auth:
        Account().request_consumer_key()
    elif domains_path is not None:
        f = open(domains_path)
        domains = f.read().splitlines()
        run(conf, Account(), domains)
        f.close()

    """
    Stop tracking domain name availability 
    after successfully completing the order process.
    """
    if REGISTERED:
        f = open(domains_path, 'w')
        for domain in domains:
            if domain not in REGISTERED:
                f.write(domain+'\n')
        f.close()

if __name__ == '__main__':
    main()
