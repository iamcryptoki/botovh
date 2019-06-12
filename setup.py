#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import botovh

from setuptools import setup

setup(
    name='botovh',
    version=botovh.__version__,
    description='Is your domain name already taken? Tell BotOVH to grab it for you when it becomes available for registration.',
    long_description=open('README.txt').read(),
    author='Gael Gentil',
    url='https://github.com/iamcryptoki/botovh',
    license='MIT',
    keywords='api, bot, domain, names, ovh, payment, registrar, registration',
    packages=['botovh'],
    install_requires=['docopt', 'ovh'],
    entry_points={
        'console_scripts': [
            'botovh=botovh.cli:main',
        ]
    }
)