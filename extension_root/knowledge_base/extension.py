from runtime import Runtime
from common.extension import InMemExtension


class KnowledgeBaseExtension(InMemExtension):
    """
    认证规则插件
    """

    def start(self, runtime: Runtime, *args, **kwargs):

        return super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):  # pylint: disable=unused-argument

        return super().teardown(runtime=runtime, *args, **kwargs)
