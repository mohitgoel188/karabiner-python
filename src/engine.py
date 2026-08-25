# Keys that mark a dict as a Karabiner `to` entry rather than a nested sublayer map.
_ACTION_KEYS = frozenset(
    {"to", "key_code", "consumer_key_code", "shell_command", "set_variable", "pointing_button"}
)


def _is_action(value: dict) -> bool:
    """True when the value is a leaf action, not a map of subkey -> action."""
    return bool(_ACTION_KEYS & value.keys())


def _split_action(action: dict) -> tuple[list[dict], str | None]:
    """Return the `to` entries and optional description for one leaf action.

    Actions come in two shapes: a bare `to` entry (``{"shell_command": ...}``) or a
    manipulator fragment (``{"description": ..., "to": [...]}``). The fragment form must
    be unwrapped — nesting it inside another ``to`` list makes Karabiner reject the whole
    entry with ``unknown key 'to'``.
    """
    if "to" in action:
        return list(action["to"]), action.get("description")
    return [{k: v for k, v in action.items() if k != "description"}], action.get("description")


def _leaf_manipulator(key: str, action: dict, conditions: list, marker: str, fallback: str) -> dict:
    to_entries, description = _split_action(action)
    return {
        "conditions": conditions,
        "description": f"{marker}: {description}" if description else fallback,
        "from": {"key_code": key, "modifiers": {"optional": ["any"]}},
        "to": to_entries,
        "type": "basic",
    }


def create_hyper_sublayers(sublayers: dict, marker: str) -> list:
    """Expand human-readable hyper mappings into Karabiner rule objects.

    A value that is a map of subkey -> action becomes a sublayer (Hyper+key arms it,
    then the subkey fires). A value that is itself an action becomes a direct
    Hyper+key binding with no sublayer of its own.
    """
    rules = []
    sublayer_keys = [k for k, v in sublayers.items() if not _is_action(v)]
    direct_manipulators = []

    for key, mapping in sublayers.items():
        if _is_action(mapping):
            direct_manipulators.append(
                _leaf_manipulator(
                    key,
                    mapping,
                    [
                        {"name": "hyper", "type": "variable_if", "value": 1},
                        *[
                            {"name": f"hyper_sublayer_{k}", "type": "variable_if", "value": 0}
                            for k in sublayer_keys
                        ],
                    ],
                    marker,
                    f"{marker}: Hyper {key}",
                )
            )
            continue

        manipulators = [
            {
                "description": f"{marker}: Toggle Hyper sublayer {key}",
                "conditions": [
                    {"name": "hyper", "type": "variable_if", "value": 1},
                    *[
                        {"name": f"hyper_sublayer_{k}", "type": "variable_if", "value": 0}
                        for k in sublayer_keys
                        if k != key
                    ],
                ],
                "from": {"key_code": key, "modifiers": {"optional": ["any"]}},
                "to": [
                    {"set_variable": {"name": f"hyper_sublayer_{key}", "value": 1}}
                ],
                "to_after_key_up": [
                    {"set_variable": {"name": f"hyper_sublayer_{key}", "value": 0}}
                ],
                "type": "basic",
            }
        ]

        sublayer_condition = [
            {"name": f"hyper_sublayer_{key}", "type": "variable_if", "value": 1}
        ]
        for subkey, action in mapping.items():
            manipulators.append(
                _leaf_manipulator(
                    subkey, action, sublayer_condition, marker, f"{marker}: Hyper {key}+{subkey}"
                )
            )

        rules.append({"description": f"{marker}: Hyper Key sublayer '{key}'", "manipulators": manipulators})

    if direct_manipulators:
        rules.append(
            {
                "description": f"{marker}: Hyper direct keys",
                "manipulators": direct_manipulators,
            }
        )
    return rules
