#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import getpass
import logging
import os
import sys

# _dir = os.path.dirname(os.path.abspath(__file__))
# _pardir = os.path.abspath(os.path.join(_dir, os.pardir))


def get_appdata_path(win_dir, unix_dir, filename):
    dist = os.name
    if (dist == 'nt'): # Windows
        path_dir = win_dir
    elif (dist == 'posix'): # Unix
        path_dir = unix_dir
    else:
        logging.error("Operating System not supported.")
        sys.exit(1)

    if not os.path.exists(path_dir):
        os.makedirs(path_dir)
    path = f"{path_dir}/{filename}"

    return path


def configure_logging(quiet):
    """Configure logging."""
    user = getpass.getuser()
    logfile = get_appdata_path(
        win_dir = f"C:/Users/{user}/.botovh",
        unix_dir = "/var/log/botovh",
        filename = "botovh.log")

    logging.basicConfig(
        level = logging.DEBUG,
        format = "%(asctime)s - %(levelname)s - %(message)s",
        filename = logfile)

    if not quiet:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        # Create formatter.
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        console.setFormatter(formatter)
        # Add handler to the root logger.
        logging.getLogger().addHandler(console)


def read_configuration():
    """Read the configuration file."""
    try:
        user = getpass.getuser()
        path = get_appdata_path(
            win_dir = f"C:/Users/{user}/.botovh",
            unix_dir = "/etc/",
            filename = "botovh.conf")

        conf = configparser.ConfigParser()
        conf.read(path)

        return conf

    except (configparser.Error, Exception) as e:
        logging.error("Error while reading configuration file: %s", e)
        sys.exit(1)
