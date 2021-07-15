class EmailConfig:

    host: str
    port: int
    user: str
    password: str
    nickname: str

    def __init__(self, host, port, user, password, nickname) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.nickname = nickname

    def __str__(self) -> str:
        return f'Email: {self.host}, {self.port}'
