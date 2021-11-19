#!/usr/bin/env python3
class InMemoryStorage:
    def __init__(self):
        self.groups = {}
        self.users = {}

Instance = InMemoryStorage()