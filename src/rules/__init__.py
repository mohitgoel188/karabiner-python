from collections.abc import Callable
from typing import Final

from src.engine import create_hyper_sublayers
from src.helpers import swap_cmd_ctrl
from src.rules.sublayers import build_sublayers
from src.rules.hyper import build_hyper_base, build_double_shift_caps_lock
from src.rules.pycharm import build_pycharm_rules, build_pycharm_cmd_q_rule
from src.rules.linx import (
    build_volume_brightness_rule,
    build_workspace_switch_rule,
    build_iterm_shortcuts_rule,
    build_firefox_shortcuts_rule,
    build_swap_cmd_ctrl_rule,
    build_home_end_rule,
)
from src.rules.macx import build_globe_control_swap_rule

MARKER = "GenX"

POWEREDX: Final = "PoweredX"
LINX: Final = "LinX"
MACX: Final = "MacX"

# Every profile is rebuilt on each run; this is the one that gets selected by default.
DEFAULT_PROFILE: Final = MACX


def _open_iterm_shortcut() -> dict:
    # Generated in every profile but shipped with "enabled": false, so it appears as
    # an OFF toggle in Karabiner's Complex Modifications list. Flip it on there
    # anytime; build.py preserves the toggle state across rebuilds.
    return {
        "description": f"{MARKER}: Open iTerm with ⌘ + ⌥ + T",
        "enabled": False,
        "manipulators": [
            {
                "type": "basic",
                "from": {
                    "key_code": "t",
                    # ⌘+⌥ (not ⌘+⌃): in LinX the left_command<->left_control swap
                    # makes a ⌘+⌃ trigger ambiguous, so option drives this launcher.
                    "modifiers": {"mandatory": ["left_command", "left_option"]},
                },
                "to": [{"shell_command": "open -a iTerm.app"}],
            }
        ],
    }


def _genx_core() -> list[dict]:
    """Hyper Key base + sublayers + double-tap right Shift. Shared by every profile.

    Nothing here matches left_control or the globe key — the hyper layer is driven by a
    ``hyper`` variable off caps_lock, not by real modifiers — so it is unaffected by
    MacX's globe/Control swap.
    """
    return [
        build_hyper_base(MARKER).__dict__,
        *create_hyper_sublayers(build_sublayers(MARKER), MARKER),
        build_double_shift_caps_lock(MARKER),
    ]


def _poweredx_rules() -> list[dict]:
    """The original GenX rule set, in its original ordering."""
    return [
        *_genx_core(),
        *build_pycharm_rules(MARKER),
        swap_cmd_ctrl("d", MARKER),
        _open_iterm_shortcut(),
    ]


def _linx_rules() -> list[dict]:
    """GenX plus the Linux muscle-memory layer.

    Order matters: the Cmd+Ctrl / Ctrl+Alt chord rules must precede the Cmd<->Ctrl swap,
    or the swap rewrites their modifiers first. Drops the pieces that conflict with the
    swap (PyCharm cmd/ctrl swap, PyCharm Shift+Enter, global ⌘D swap).
    """
    return [
        build_volume_brightness_rule(MARKER),
        build_workspace_switch_rule(MARKER),
        build_iterm_shortcuts_rule(MARKER),
        build_firefox_shortcuts_rule(MARKER),
        _open_iterm_shortcut(),
        build_swap_cmd_ctrl_rule(MARKER),
        build_home_end_rule(MARKER),
        *_genx_core(),
    ]


def _macx_rules() -> list[dict]:
    """GenX with native macOS modifier semantics.

    No Cmd<->Ctrl swap of any kind, so the PyCharm swaps, the global ⌘D<->⌃D swap, and
    LinX's iTerm/Firefox compensations (which only existed to patch holes the swap left)
    are all omitted. The one PyCharm rule kept is the ⌘Q -> ⌃Q rewrite, which is a single
    chord rather than a modifier swap. The built-in-keyboard globe<->Control normaliser
    leads so the chord rules below it see the rewritten left_control.
    """
    return [
        build_globe_control_swap_rule(MARKER),
        build_pycharm_cmd_q_rule(MARKER),
        build_volume_brightness_rule(MARKER),
        build_workspace_switch_rule(MARKER),
        build_home_end_rule(MARKER),
        _open_iterm_shortcut(),
        *_genx_core(),
    ]


_PROFILE_RULES: dict[str, Callable[[], list[dict]]] = {
    POWEREDX: _poweredx_rules,
    LINX: _linx_rules,
    MACX: _macx_rules,
}

PROFILE_NAMES: Final[tuple[str, ...]] = (POWEREDX, LINX, MACX)


def generate_rules(profile: str = DEFAULT_PROFILE) -> list[dict]:
    """Generate the Karabiner rule list for one named profile.

    ``PoweredX`` is the original GenX set. ``LinX`` adds the Linux muscle-memory layer
    (Cmd<->Ctrl swap and friends). ``MacX`` keeps native macOS modifiers and adds only the
    built-in-keyboard globe<->Control normaliser.
    """
    try:
        builder = _PROFILE_RULES[profile]
    except KeyError:
        raise ValueError(
            f"Unknown profile {profile!r}; expected one of {', '.join(PROFILE_NAMES)}"
        ) from None
    return builder()
