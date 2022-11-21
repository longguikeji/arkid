from typing import List


def transports_to_ui_string(transports: List[str]) -> str:
    """
    Generate a human-readable string of transports

    input: `["internal", "usb"]`
    output: `'["internal", "usb"]'`
    """
    joined = ", ".join([f'"{transport}"' for transport in transports])
    return f"[{joined}]"


def truncate_credential_id_to_ui_string(id: str) -> str:
    """
    Truncate long credential IDs

    input: "ENBgSinv7tVrLREki5ShWg"
    output: "ENBgSinv...Eki5ShWg"
    """
    divider = "..."
    truncation_length = 8

    if len(id) <= (len(divider) + (truncation_length * 2)):
        # Return the entire ID if there's nothing to truncate
        return id

    return f"{id[0:truncation_length]}...{id[(0-truncation_length):]}"
