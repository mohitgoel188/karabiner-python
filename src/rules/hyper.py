from src.models import Rule


def build_hyper_base(marker: str) -> Rule:
    """Build the base Hyper Key rule (Caps Lock -> Ctrl+Opt+Shift+Cmd)."""
    return Rule(
        description=f"{marker}: Hyper Key (\u2303\u2325\u21e7\u2318)",
        manipulators=[
            {
                "description": f"{marker}: Caps Lock -> Hyper Key",
                "from": {"key_code": "caps_lock", "modifiers": {"optional": ["any"]}},
                "to": [{"set_variable": {"name": "hyper", "value": 1}}],
                "to_after_key_up": [{"set_variable": {"name": "hyper", "value": 0}}],
                "to_if_alone": [{"key_code": "escape"}],
                "type": "basic",
            }
        ],
    )


def build_double_shift_caps_lock(marker: str) -> dict:
    """Build the double-tap right Shift -> Caps Lock rule."""
    return {
        "description": f"{marker}: Change double tap right \u21e7 key to caps lock",
        "manipulators": [
            {
                "conditions": [
                    {
                        "name": "right_shift pressed",
                        "type": "variable_if",
                        "value": 1,
                    }
                ],
                "from": {
                    "key_code": "right_shift",
                    "modifiers": {"optional": ["any"]},
                },
                "to": [{"key_code": "caps_lock"}],
                "type": "basic",
            },
            {
                "from": {
                    "key_code": "right_shift",
                    "modifiers": {"optional": ["any"]},
                },
                "to": [
                    {
                        "set_variable": {
                            "name": "right_shift pressed",
                            "value": 1,
                        }
                    },
                    {"key_code": "right_shift"},
                ],
                "to_delayed_action": {
                    "to_if_canceled": [
                        {
                            "set_variable": {
                                "name": "right_shift pressed",
                                "value": 0,
                            }
                        }
                    ],
                    "to_if_invoked": [
                        {
                            "set_variable": {
                                "name": "right_shift pressed",
                                "value": 0,
                            }
                        }
                    ],
                },
                "type": "basic",
            },
        ],
    }
