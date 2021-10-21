#!/usr/bin/env python3
import uuid


def try_get_request_identifier():
    return str(uuid.uuid1())
