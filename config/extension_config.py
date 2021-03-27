class ExtensionConfig:

    root: str
    config: dict

    def __init__(self, root) -> None:
        self.root = root
        self.config = {}

    def __str__(self) -> str:
        return f'Extension: {self.root}'
