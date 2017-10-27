# BotOvh

BotOvh is a tiny bot I wrote for my personal needs. It checks whether a specific domain name is available for registration, and then automatically registers the domain using the [OVH API](https://github.com/ovh/python-ovh).

## Requirements

- [**OVH Account**](https://www.ovh.com/)
- **Python 3**

In addition to Python 3 itself, BotOvh uses the following modules:

- **ovh**: OVH API wrapper ([repo](https://github.com/ovh/python-ovh))
  - Installation: `pip install ovh`

- **docopt**: Command-line arguments parser ([repo](https://github.com/docopt/docopt))
  - Installation: `pip install docopt`

## Usage

**Basic usage:**

``$ python botovh.py example.com fakedomain.org``

**Specify a file containing the domain names you want:**

``$ python botovh.py -f /path/to/file.txt``

``$ python botovh.py --file /path/to/file.txt``

**Specify the location where you want to store the log file:**

Default: Current folder.

``$ python botovh.py -l /path/to/folder``

``$ python botovh.py --log /path/to/folder``

**Request a new OVH consumer key:**

``$ python botovh.py -k``

``$ python botovh.py --key``

**Specify your preferred payment method:**

Payment methods: bankAccount, creditCard, fidelityAccount, ovhAccount or paypal.

``$ python botovh.py -p paypal``

``$ python botovh.py --payment creditCard``

## Automate BotOvh

You can automate BotOvh to run daily using [cron jobs](https://help.ubuntu.com/community/CronHowto) or task scheduler depending on your system.

## License

This code is released under a free software [license](LICENSE) and you are welcome to fork it.