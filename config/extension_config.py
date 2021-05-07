class ExtensionConfig:

    root: str
    config: dict

    def __init__(self, root) -> None:
        self.root = root
        self.config = {}

    def __str__(self) -> str:
        return f'Extension: {self.root}'

    def load_from_db(self, key):
        from extension.models import Extension
        extension = Extension.valid_objects.filter(
            type=key
        ).first()
        if extension:
            return extension.data
        else:
            return ''
