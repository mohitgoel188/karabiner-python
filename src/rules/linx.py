# FILE: src/rules/linx.py
"""Linux muscle-memory layer for the LinX profile.

Ported from the migration kit (mac-keyboard-migration/karabiner.json). These rules
make the corner key (physical Left Ctrl) drive macOS shortcuts like Linux Ctrl, while
keeping real Ctrl in standalone terminals for SIGINT. Used only when build.py is run
with --linx; PoweredX never carries these.
"""

# Standalone terminals keep real Ctrl on the corner key (so Ctrl+C = SIGINT).
_TERMINAL_BUNDLE_IDS: list[str] = [
    "^com\\.apple\\.Terminal$",
    "^com\\.googlecode\\.iterm2$",
    "^com\\.github\\.wez\\.wezterm$",
    "^net\\.kovidgoyal\\.kitty$",
    "^org\\.alacritty$",
    "^io\\.alacritty$",
    "^dev\\.warp\\.Warp-Stable$",
]

# PyCharm binds Home/End in its own keymap, so the system-level rule skips it.
_PYCHARM_BUNDLE_IDS: list[str] = [
    "^com\\.jetbrains\\.pycharm$",
    "^com\\.jetbrains\\.pycharm\\.ce$",
]


def build_volume_brightness_rule(marker: str) -> dict:
    """Cmd+Ctrl+Arrows -> volume/brightness (mirrors Linux Ctrl+Super+Arrows).

    MUST sit above the Cmd/Ctrl swap rule, or the swap rewrites the modifiers first.
    """
    return {
        "description": (
            f"{marker} LinX: Volume & Brightness via Cmd+Ctrl+Arrows "
            "(mirrors Linux Ctrl+Super+Arrows). Keep above the Cmd/Ctrl swap rule."
        ),
        "manipulators": [
            {
                "type": "basic",
                "from": {
                    "key_code": "up_arrow",
                    "modifiers": {"mandatory": ["left_command", "left_control"]},
                },
                "to": [{"consumer_key_code": "volume_increment"}],
            },
            {
                "type": "basic",
                "from": {
                    "key_code": "down_arrow",
                    "modifiers": {"mandatory": ["left_command", "left_control"]},
                },
                "to": [{"consumer_key_code": "volume_decrement"}],
            },
            {
                "type": "basic",
                "from": {
                    "key_code": "right_arrow",
                    "modifiers": {"mandatory": ["left_command", "left_control"]},
                },
                "to": [{"key_code": "display_brightness_increment"}],
            },
            {
                "type": "basic",
                "from": {
                    "key_code": "left_arrow",
                    "modifiers": {"mandatory": ["left_command", "left_control"]},
                },
                "to": [{"key_code": "display_brightness_decrement"}],
            },
        ],
    }


def build_swap_cmd_ctrl_rule(marker: str) -> dict:
    """Swap Left Cmd <-> Left Ctrl everywhere except standalone terminals.

    PyCharm is intentionally NOT excluded, so it matches its macOS ($default) keymap.
    """
    unless = [
        {
            "type": "frontmost_application_unless",
            "bundle_identifiers": _TERMINAL_BUNDLE_IDS,
        }
    ]
    return {
        "description": (
            f"{marker} LinX: Swap Left Command <-> Left Control everywhere EXCEPT "
            "terminals (corner pinky key drives macOS shortcuts like Linux Ctrl). "
            "PyCharm IS swapped. Terminals keep real Ctrl for SIGINT."
        ),
        "manipulators": [
            {
                "type": "basic",
                "from": {
                    "key_code": "left_command",
                    "modifiers": {"optional": ["any"]},
                },
                "to": [{"key_code": "left_control"}],
                "conditions": unless,
            },
            {
                "type": "basic",
                "from": {
                    "key_code": "left_control",
                    "modifiers": {"optional": ["any"]},
                },
                "to": [{"key_code": "left_command"}],
                "conditions": unless,
            },
        ],
    }


def build_home_end_rule(marker: str) -> dict:
    """PC-style Home/End -> line start/end (except terminals and PyCharm)."""
    unless = [
        {
            "type": "frontmost_application_unless",
            "bundle_identifiers": _TERMINAL_BUNDLE_IDS + _PYCHARM_BUNDLE_IDS,
        }
    ]
    return {
        "description": (
            f"{marker} LinX: PC-style Home / End = line start / end "
            "(except terminals and PyCharm, which bind these in their own keymap)."
        ),
        "manipulators": [
            {
                "type": "basic",
                "from": {"key_code": "home", "modifiers": {"optional": ["any"]}},
                "to": [{"key_code": "left_arrow", "modifiers": ["left_command"]}],
                "conditions": unless,
            },
            {
                "type": "basic",
                "from": {"key_code": "end", "modifiers": {"optional": ["any"]}},
                "to": [{"key_code": "right_arrow", "modifiers": ["left_command"]}],
                "conditions": unless,
            },
        ],
    }


def build_linx_layer(marker: str) -> list[dict]:
    """Build the Linux muscle-memory layer rules in Karabiner evaluation order.

    Volume/Brightness first (it must precede the Cmd/Ctrl swap); then the swap; then
    Home/End. The iTerm Cmd+Ctrl chord is assembled ahead of the swap in
    generate_rules(), so it is not included here.
    """
    return [
        build_volume_brightness_rule(marker),
        build_swap_cmd_ctrl_rule(marker),
        build_home_end_rule(marker),
    ]
