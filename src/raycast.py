import shlex


def raycast(extension: str, command: str, background: bool = False) -> dict:
    """Build a Raycast command shell trigger."""
    url = f"raycast://extensions/{extension}/{command}"
    if background:
        url += "?launchType=background"
    return {"shell_command": f"open {shlex.quote(url)}"}
