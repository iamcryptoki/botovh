#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 
              ~ B O T O V H ~

                  v0.2.0

     Is your domain name already taken?
         Tell me to grab it for you
 when it becomes available for registration

 ==========================================

Usage:
    botovh.py [DOMAINS ...] [--file=f] [--help] [--key] [--noemail] [--payment=p] [--quiet] [--version]

Options:
    -f --file=f             Specify a file containing a list of domain names.
    -h --help               Show this message.
    -k --key                Request a new OVH consumer key.
    -n --noemail            Disable email notification.
    -p --payment=p          Specify your preferred payment method: 
                            bankAccount, creditCard, fidelityAccount, ovhAccount or paypal.
    -q --quiet              Disable console logging.
    -v --version            Show version.
"""

import logging
import sys

import ovh
from docopt import docopt

from . import __version__
from . import account as acc
from . import dispatch as disp
from . import email_client
from . import utils


def run(dispatch, account, domains, payment_mean, noemail, smtp):
    """Start checking domain names."""
    logging.info("Start")

    for domain in domains:
        logging.info("Checking %s", domain)

        # Create a new cart and assign to current user.
        cart_id = account.create_cart()
        # Add domain item to the cart.
        try:
            result = account.add_to_cart(domain, cart_id)
        except ovh.exceptions.APIError:
            continue
        if len(result) and ('create' in result['settings'].get('planCode')):
            # Generate a salesorder.
            salesorder = account.generate_salesorder(domain, cart_id)
            order_id = salesorder['orderId']

            logging.info("%s : Available domain name. Order #%s (%s) has been generated.",
                         domain, order_id, salesorder['prices']['withTax']['text'])

            # Retrieve available payment means.
            payment_means = account.get_payment_means(domain, order_id)
            if not payment_means:
                message = ("[%s] Not registered payment means available. "
                           "Can't pay this order automatically.", domain)
                dispatch.add("- %s" % message)
                logging.error(message)
                sys.exit(1)
            if payment_mean is None or payment_mean not in payment_means:
                payment_mean = payment_means[0]['paymentMean']

            # Pay with an already registered payment mean.
            payment_mean_id = account.get_payment_mean_id(domain, payment_mean)[0]
            account.pay(domain, order_id, payment_mean, payment_mean_id)

    if not noemail and len(dispatch.messages):
        # Create an SMTP instance.
        mail = email_client.Email(
            host = smtp['HOST'],
            user = smtp['USER'],
            password = smtp['PASSWORD']
        )

        # Send email notification.
        messages = sorted(dispatch.messages)
        mail.send(
            smtp['SEND_FROM'],
            smtp['SEND_TO'],
            '\n'.join(messages))

    logging.info("Finished")


def main():
    args = docopt(__doc__, version=__version__)

    # Configure logging.
    utils.configure_logging(args['--quiet'])
    # Read the configuration file.
    conf = utils.read_configuration()
    # Check SMTP configuration.
    if not args['--noemail'] and not conf.has_section('SMTP'):
        logging.error("SMTP configuration not found. "
                      "Please configure SMTP or use the '--noemail' flag.")
        sys.exit(1)

    # Create a Dispatch instance.
    dispatch = disp.Dispatch()
    # Create an Account instance.
    account = acc.Account(dispatch, conf['OVH'])

    if args['--key']:
        # Request a new consumer key from the OVH API.
        account.request_consumer_key()
        sys.exit(0)

    # Get domain names you want to check.
    if args['DOMAINS']:
        domains = args['DOMAINS']
    elif args['--file'] is not None:
        try:
            with open(args['--file']) as f:
                domains = f.read().splitlines()
        except FileNotFoundError:
            logging.error("File not found. Please input the path of an existing file.")
            sys.exit(1)
    else:
        logging.error("Please input at least 1 domain name.")
        sys.exit(1)

    # Start checking domain names.
    run(dispatch,
        account,
        domains,
        args['--payment'],
        args['--noemail'],
        conf['SMTP'])


if __name__ == '__main__':
    main()
