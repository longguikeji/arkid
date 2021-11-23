#!/usr/bin/env python3


class FeatureBase:
    @property
    def supported(self):
        return self._supported

    @supported.setter
    def supported(self, value):
        self._supported = value
