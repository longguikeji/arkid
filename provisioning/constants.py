from enum import Enum


class ProvisioningMode(Enum):

    Automatic = 0


class ProvisioningStatus(Enum):

    Enabled = 0
    Disabled = 1

class ProvisioningType(Enum):

    upstream = 0
    downstream = 1

class AuthenticationType(Enum):

    basic = 0
    token = 1
