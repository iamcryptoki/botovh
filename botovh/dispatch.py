#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Dispatch(object):
    def __init__(self):
        self.messages = []

    def add(self, message):
        self.messages.append(message)
