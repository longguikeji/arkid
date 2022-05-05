#!/usr/bin/env python3
from scim_server.schemas.feature import Feature
from typing import Optional


class FilterFeature(Feature):
    maxResults: int