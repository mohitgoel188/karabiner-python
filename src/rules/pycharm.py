# Professional is `com.jetbrains.pycharm`; Community Edition appends `.ce`. Kept in the
# same two-entry shape as linx.py's list so both files stay greppable and in sync.
_PYCHARM_BUNDLE_IDS: list[str] = [
    "^com\\.jetbrains\\.pycharm$",
    "^com\\.jetbrains\\.pycharm\\.ce$",
]


def _pycharm_frontmost_if() -> list[dict]:
    """frontmost_application_if condition matching PyCharm (Professional or CE)."""
    return [
        {
            "type": "frontmost_application_if",
            "bundle_identifiers": list(_PYCHARM_BUNDLE_IDS),
        }
    ]


def build_pycharm_cmd_q_rule(marker: str) -> dict:
    """Turn ⌘Q into ⌃Q inside PyCharm (quick documentation, not Quit).

    Profile-neutral: it rewrites only the ⌘Q chord, so it is safe in MacX where no
    global Cmd<->Ctrl swap exists. ``command`` (rather than ``left_command``) is
    mandatory so the right Command key cannot slip through and quit the IDE, and no
    ``optional: any`` is used so ⌘⇧Q and friends keep their native behaviour.
    """
    return {
        "description": f"{marker}: PyCharm ⌘Q -> ⌃Q (quick docs instead of Quit)",
        "manipulators": [
            {
                "type": "basic",
                "from": {
                    "key_code": "q",
                    "modifiers": {"mandatory": ["command"]},
                },
                "to": [{"key_code": "q", "modifiers": ["left_control"]}],
                "conditions": _pycharm_frontmost_if(),
            }
        ],
    }


def build_pycharm_rules(marker: str) -> list[dict]:
    """Build PyCharm-specific key swap rules."""
    swap_cmd_ctrl_rule = {
        "description": f"{marker}: Swap Command and Control in PyCharm",
        "manipulators": [
            {
                "type": "basic",
                "from": {"key_code": "left_command"},
                "to": [{"key_code": "left_control"}],
                "conditions": _pycharm_frontmost_if(),
            },
            {
                "type": "basic",
                "from": {"key_code": "left_control"},
                "to": [{"key_code": "left_command"}],
                "conditions": _pycharm_frontmost_if(),
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
                "conditions": _pycharm_frontmost_if(),
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
                "conditions": _pycharm_frontmost_if(),
            },
        ],
    }

    return [swap_cmd_ctrl_rule, swap_shift_enter_rule]
