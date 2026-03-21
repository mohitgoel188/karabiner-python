from src.engine import create_hyper_sublayers
from src.helpers import swap_cmd_ctrl
from src.rules.sublayers import build_sublayers
from src.rules.hyper import build_hyper_base, build_double_shift_caps_lock
from src.rules.pycharm import build_pycharm_rules

MARKER = "GenX"


def generate_rules() -> list:
    """Generate PoweredX Karabiner rules with proper descriptions."""
    base_rule = build_hyper_base(MARKER)
    sublayers = build_sublayers(MARKER)

    open_iterm_shortcut = {
        "description": f"{MARKER}: Open iTerm with \u2318 + \u2303 + T",
        "manipulators": [
            {
                "type": "basic",
                "from": {
                    "key_code": "t",
                    "modifiers": {"mandatory": ["left_command", "left_control"]},
                },
                "to": [
                    {
                        "shell_command": "open -a iTerm.app"
                    }
                ],
            }
        ],
    }

    return [
        base_rule.__dict__,
        *create_hyper_sublayers(sublayers, MARKER),
        build_double_shift_caps_lock(MARKER),
        *build_pycharm_rules(MARKER),
        swap_cmd_ctrl("d", MARKER),
        open_iterm_shortcut,
    ]
