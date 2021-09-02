
from typing import Dict
from common.provider import BaseAuthRuleProvider


class FirstLoginRuleProvider(BaseAuthRuleProvider):

    def create(self, auth_rule, data) -> Dict:
        return data

    def delete(self):
        return super().delete()

    def update(self):
        return super().update()

    def run(self, *args, **kwargs):
        return super().run(*args, **kwargs)