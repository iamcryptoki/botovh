#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import ovh
import sys


class Account(object):
    def __init__(self, dispatch, conf):
        self.dispatch = dispatch
        self.endpoint = conf['ENDPOINT']
        self.app_key = conf['APPLICATION_KEY']
        self.app_secret = conf['APPLICATION_SECRET']
        self.consumer_key = conf['CONSUMER_KEY']

        # Create a client.
        self.client = ovh.Client(
            endpoint = self.endpoint,
            application_key=self.app_key,
            application_secret=self.app_secret,
            consumer_key=self.consumer_key)


    def create_cart(self):
        """Create a new cart and assign to current user."""
        cart = self.client.post("/order/cart", ovhSubsidiary='FR', _need_auth=False)
        cart_id = cart.get('cartId')
        self.client.post("/order/cart/{0}/assign".format(cart_id))
        return cart_id


    def add_to_cart(self, domain, cart_id):
        """Add domain item to the cart."""
        return self.client.post("/order/cart/{0}/domain".format(cart_id), domain=domain)


    def generate_salesorder(self, domain, cart_id):
        """Generate a salesorder."""
        try:
            return self.client.post("/order/cart/{0}/checkout".format(cart_id))
        except ovh.exceptions.APIError as e:
            message = f"{domain}: Unable to generate the order. Message = {str(e)}"
            dispatch.add("- %s" % message)
            logging.error(message)
            sys.exit(1)


    def get_payment_means(self, domain, order_id):
        """Retrieve available payment means."""
        try:
            return self.client.get("/me/order/{0}/availableRegisteredPaymentMean".format(order_id))
        except ovh.exceptions.APIError as e:
            message = f"{domain}: Unable to retrieve order payment means. Message: {str(e)}"
            dispatch.add("- %s" % message)
            logging.error(message)
            sys.exit(1)


    def get_payment_mean_id(self, domain, payment_mean):
        try:
            return self.client.get("/me/paymentMean/{0}".format(payment_mean))
        except ovh.exceptions.APIError as e:
            message = f"{domain}: {str(e)}"
            dispatch.add("- %s" % message)
            logging.error(message)
            sys.exit(1)


    def pay(self, domain, order_id, payment_mean, payment_mean_id):
        """Pay with an already registered payment mean."""
        try:
            self.client.post("/me/order/{0}/payWithRegisteredPaymentMean"
                             .format(order_id),
                             paymentMean=payment_mean,
                             paymentMeanId=payment_mean_id)
            message = ("%s: Payment successful. "
                       "Congratulations on purchasing a new domain name!", domain)
            dispatch.add("- %s" % message)
            logging.info(message)
            """
            COMPLETED! You should receive a confirmation email from OVH
            confirming that you are the legal registrant! :)
            """
        except ovh.exceptions.APIError as e:
            message = "{domain}: Payment of your order haven't been successful. Message = {str(e)}"
            dispatch.add("- %s" % message)
            logging.error(message)
            sys.exit(1)


    def request_consumer_key(self):
        """Request a new consumer key."""
        ck = self.client.new_consumer_key_request()
        ck.add_recursive_rules(ovh.API_READ_WRITE, '/')
        validation = ck.request()

        print("1. Please visit %s to authenticate." % validation['validationUrl'])
        input("2. Press Enter to continue...\n")
        print("Welcome %s!" % self.client.get('/me')['firstname'])
        print("Your consumer key is '%s'" % validation['consumerKey'])
