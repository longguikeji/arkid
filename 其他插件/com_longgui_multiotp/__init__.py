from arkid.core.extension import Extension


class MultiotpExtension(Extension):
    def load(self):
        super().load()


extension = MultiotpExtension()
