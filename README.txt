BotOVH is a tiny bot I wrote for my personnal needs.

Is your domain name already taken? Tell BotOVH to grab it for you when it becomes available for registration.

------------
Requirements
------------

- OVH Account
- OVH API application
- Python 3.6+

------------
Installation
------------

1. Install BotOVH using pip

``pip install botovh``

BotOVH automatically installs the following dependencies:

- docopt
- python-ovh

2. Create an OVH API application

To interact with the OVH APIs, BotOVH needs to identify itself using an application_key and an application_secret. To get them, you need to register an OVH API application.

Once created, you will obtain an application key and an application secret.

3. Configure BotOVH

Create an ``botovh.conf`` configuration file at :

- Windows : ``C:\Users\<YOUR_WINDOWS_USERNAME>\.botovh\botovh.conf``

- Linux / Mac : ``/etc/botovh.conf``

Here is how the configuration file looks like :

OVH API
-------

```ini
[OVH]
ENDPOINT=ovh-eu
APPLICATION_KEY=<YOUR_APPLICATION_KEY>
APPLICATION_SECRET=<YOUR_APPLICATION_SECRET>
; Use 'botovh --key' to request your OVH consumer key.
CONSUMER_KEY=<YOUR__CONSUMER_KEY>
```

Email notification
------------------

```ini
[SMTP]
; Send email notification.
HOST=<SMTP_SERVER_ADDRESS>
PORT=465
USER=<YOUR_SMTP_USER>
PASSWORD=<YOUR_SMTP_PASSWORD>
SEND_FROM=<SEND_EMAIL_FROM>
SEND_TO=<SEND_EMAIL_TO>
```

-----
Usage
-----

Request a new OVH consumer key:

``$ botovh -k``

``$ botovh --key``

Basic usage:

``$ botovh example.com fakedomain.org``

Specify a file containing the domain names you want to check:

``$ botovh -f /path/to/file.txt``

``$ botovh --file /path/to/file.txt``

Specify your preferred payment method:

Payment methods: bankAccount, creditCard, fidelityAccount, ovhAccount or paypal.

``$ botovh -p paypal``

``$ botovh --payment creditCard``

Disable console logging using the ``--quiet`` argument:

``$ botovh example.com fakedomain.org --quiet``

Disable email notification using the ``--noemail`` argument:

``$ botovh example.com fakedomain.org --noemail``

---------------
Automate BotOVH
---------------

You can automate BotOVH to run daily using cron jobs or task scheduler depending on your system.

-------
License
-------

This code is released under a free software license and you are welcome to fork it.
