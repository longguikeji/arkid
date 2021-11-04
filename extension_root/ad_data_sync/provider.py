from common.provider import DataSyncProvider


class AdDataSyncProvider(DataSyncProvider):
    def __init__(self) -> None:
        super().__init__()

    def create(self, tenant_uuid, data):
        host = data.get("host")
        port = data.get("port")
        bind_dn = data.get("bind_dn")
        bind_password = data.get("bind_password")
        use_tls = data.get("use_tls")

        return {
            "host": host,
            "port": port,
            "bind_dn": bind_dn,
            "bind_password": bind_password,
            "use_tls": use_tls,
        }

    def update(self, tenant_uuid, data):
        host = data.get("host")
        port = data.get("port")
        bind_dn = data.get("bind_dn")
        bind_password = data.get("bind_password")
        use_tls = data.get("use_tls")

        return {
            "host": host,
            "port": port,
            "bind_dn": bind_dn,
            "bind_password": bind_password,
            "use_tls": use_tls,
        }
