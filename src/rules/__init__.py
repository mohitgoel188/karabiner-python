from src.engine import create_hyper_sublayers
from src.helpers import swap_cmd_ctrl
from src.rules.sublayers import build_sublayers
from src.rules.hyper import build_hyper_base, build_double_shift_caps_lock
from src.rules.pycharm import build_pycharm_rules
from src.rules.linx import (
    build_volume_brightness_rule,
    build_swap_cmd_ctrl_rule,
    build_home_end_rule,
)

MARKER = "GenX"


def _open_iterm_shortcut() -> dict:
    return {
        "description": f"{MARKER}: Open iTerm with ⌘ + ⌃ + T",
        "manipulators": [
            {
                "type": "basic",
                "from": {
                    "key_code": "t",
                    "modifiers": {"mandatory": ["left_command", "left_control"]},
                },
                "to": [{"shell_command": "open -a iTerm.app"}],
            }
        ],
    }


def generate_rules(linx: bool = False) -> list:
    """Generate Karabiner rules.

    When ``linx`` is False (default) this returns the PoweredX (GenX) rule set,
    unchanged from the original ordering. When ``linx`` is True it returns the LinX
    variant: the same GenX features minus the pieces that conflict with the Linux
    muscle-memory swap (PyCharm cmd/ctrl swap, PyCharm Shift+Enter, global Cmd+D
    swap), plus the Linux layer (Volume/Brightness, Left Cmd<->Ctrl swap, Home/End).
    """
    base_rule = build_hyper_base(MARKER)
    sublayers = build_sublayers(MARKER)
    open_iterm_shortcut = _open_iterm_shortcut()

    if not linx:
        return [
            base_rule.__dict__,
            *create_hyper_sublayers(sublayers, MARKER),
            build_double_shift_caps_lock(MARKER),
            *build_pycharm_rules(MARKER),
            swap_cmd_ctrl("d", MARKER),
            open_iterm_shortcut,
        ]

    # LinX order matters: the Cmd+Ctrl chord rules (Volume/Brightness, iTerm) must
    # precede the Cmd<->Ctrl swap, or the swap rewrites their modifiers first.
    return [
        build_volume_brightness_rule(MARKER),
        open_iterm_shortcut,
        build_swap_cmd_ctrl_rule(MARKER),
        build_home_end_rule(MARKER),
        base_rule.__dict__,
        *create_hyper_sublayers(sublayers, MARKER),
        build_double_shift_caps_lock(MARKER),
    ]
