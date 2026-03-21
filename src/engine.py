def create_hyper_sublayers(sublayers: dict, marker: str) -> list:
    """Expand human-readable hyper mappings into Karabiner rule objects."""
    rules = []
    all_sublayers = list(sublayers.keys())

    for key, mapping in sublayers.items():
        manipulators = [
            {
                "description": f"{marker}: Toggle Hyper sublayer {key}",
                "conditions": [
                    {"name": "hyper", "type": "variable_if", "value": 1},
                    *[
                        {"name": f"hyper_sublayer_{k}", "type": "variable_if", "value": 0}
                        for k in all_sublayers
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

        for subkey, action in mapping.items():
            manipulators.append(
                {
                    "conditions": [
                        {
                            "name": f"hyper_sublayer_{key}",
                            "type": "variable_if",
                            "value": 1,
                        }
                    ],
                    "description": f"{marker}: Hyper {key}+{subkey}",
                    "from": {
                        "key_code": subkey,
                        "modifiers": {"optional": ["any"]},
                    },
                    "to": [action],
                    "type": "basic",
                }
            )

        rules.append({"description": f"{marker}: Hyper Key sublayer '{key}'", "manipulators": manipulators})
    return rules
