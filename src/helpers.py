import shlex


def tuple_dict(pairs: list[tuple[str, dict]]) -> dict:
    """Convert list of (key, action) tuples to dict and detect duplicates."""
    seen = {}
    duplicates = []
    for key, action in pairs:
        if key in seen:
            duplicates.append(key)
        seen[key] = action
    if duplicates:
        print(f"\u26a0\ufe0f Duplicate key(s) detected: {', '.join(duplicates)}")
    return seen


def app(app_name: str) -> dict:
    name = app_name.removesuffix(".app")
    return {"shell_command": f"open -a {shlex.quote(name + '.app')}"}


def open_url(url: str) -> dict:
    return {"shell_command": f"open {shlex.quote(url)}"}


def window(action: str) -> dict:
    url = f"rectangle://execute-action?name={action}"
    return {"shell_command": f"open -g {shlex.quote(url)}"}


def swap_cmd_ctrl(key: str, marker: str) -> dict:
    """Create a rule that swaps Cmd+key and Ctrl+key globally."""
    return {
        "description": f"{marker}: Swap \u2318+{key.upper()} \u2194 \u2303+{key.upper()} (Global)",
        "manipulators": [
            {
                "type": "basic",
                "from": {"key_code": key, "modifiers": {"mandatory": ["left_command"], "optional": ["any"]}},
                "to": [{"key_code": key, "modifiers": ["left_control"]}],
            },
            {
                "type": "basic",
                "from": {"key_code": key, "modifiers": {"mandatory": ["left_control"], "optional": ["any"]}},
                "to": [{"key_code": key, "modifiers": ["left_command"]}],
            },
        ],
    }
