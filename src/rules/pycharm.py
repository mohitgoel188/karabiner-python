def build_pycharm_rules(marker: str) -> list[dict]:
    """Build PyCharm-specific key swap rules."""
    swap_cmd_ctrl_rule = {
        "description": f"{marker}: Swap Command and Control in PyCharm",
        "manipulators": [
            {
                "type": "basic",
                "from": {"key_code": "left_command"},
                "to": [{"key_code": "left_control"}],
                "conditions": [
                    {
                        "type": "frontmost_application_if",
                        "bundle_identifiers": [
                            "^com\\.jetbrains\\.pycharm$",
                        ],
                    }
                ],
            },
            {
                "type": "basic",
                "from": {"key_code": "left_control"},
                "to": [{"key_code": "left_command"}],
                "conditions": [
                    {
                        "type": "frontmost_application_if",
                        "bundle_identifiers": [
                            "^com\\.jetbrains\\.pycharm$",
                        ],
                    }
                ],
            },
        ],
    }

    swap_shift_enter_rule = {
        "description": f"{marker}: Swap Shift+Enter \u2194 Option+Enter in PyCharm",
        "manipulators": [
            {
                "type": "basic",
                "from": {
                    "key_code": "return_or_enter",
                    "modifiers": {"mandatory": ["left_shift"]},
                },
                "to": [
                    {
                        "key_code": "return_or_enter",
                        "modifiers": ["left_option"],
                    }
                ],
                "conditions": [
                    {
                        "type": "frontmost_application_if",
                        "bundle_identifiers": ["^com\\.jetbrains\\.pycharm$"],
                    }
                ],
            },
            {
                "type": "basic",
                "from": {
                    "key_code": "return_or_enter",
                    "modifiers": {"mandatory": ["left_option"]},
                },
                "to": [
                    {
                        "key_code": "return_or_enter",
                        "modifiers": ["left_shift"],
                    }
                ],
                "conditions": [
                    {
                        "type": "frontmost_application_if",
                        "bundle_identifiers": ["^com\\.jetbrains\\.pycharm$"],
                    }
                ],
            },
        ],
    }

    return [swap_cmd_ctrl_rule, swap_shift_enter_rule]
