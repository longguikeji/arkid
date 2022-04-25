#!/usr/bin/env python3
from pydantic import BaseModel


class FeatureBase(BaseModel):
    supported: bool
    # @property
    # def supported(self):
    #     return self._supported

    # @supported.setter
    # def supported(self, value):
    #     self._supported = value
