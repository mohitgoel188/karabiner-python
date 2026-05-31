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


def build_workspace_switch_rule(marker: str) -> dict:
    """Ctrl+Alt+Left/Right -> switch Mission Control space left/right.

    Matches the PHYSICAL Optimus keys (left_control + left_option) ahead of the
    Cmd<->Ctrl swap and emits macOS-native Control+Arrow. Requires more than one
    desktop/space and the 'Move left/right a space' shortcuts enabled under
    System Settings > Keyboard > Keyboard Shortcuts > Mission Control.
    """
    return {
        "description": (
            f"{marker} LinX: Ctrl+Alt+Arrow -> switch space left/right "
            "(physical Optimus keys; Mission Control)"
        ),
        "manipulators": [
            {
                "type": "basic",
                "from": {
                    "key_code": "left_arrow",
                    "modifiers": {"mandatory": ["left_control", "left_option"]},
                },
                "to": [{"key_code": "left_arrow", "modifiers": ["left_control"]}],
            },
            {
                "type": "basic",
                "from": {
                    "key_code": "right_arrow",
                    "modifiers": {"mandatory": ["left_control", "left_option"]},
                },
                "to": [{"key_code": "right_arrow", "modifiers": ["left_control"]}],
            },
        ],
    }


def build_screenshot_rule(marker: str) -> dict:
    """Ctrl+Cmd+P -> region screenshot to clipboard (Cmd+Ctrl+Shift+4).

    Matches the PHYSICAL Optimus keys (left_control + left_command) ahead of the
    Cmd<->Ctrl swap. Drag-select a region; the image goes to the clipboard.
    """
    return {
        "description": (
            f"{marker} LinX: Ctrl+Cmd+P -> region screenshot to clipboard "
            "(physical Optimus keys)"
        ),
        "manipulators": [
            {
                "type": "basic",
                "from": {
                    "key_code": "p",
                    "modifiers": {"mandatory": ["left_control", "left_command"]},
                },
                "to": [
                    {
                        "key_code": "4",
                        "modifiers": ["left_command", "left_control", "left_shift"],
                    }
                ],
            }
        ],
    }


def build_iterm_new_tab_rule(marker: str) -> dict:
    """In iTerm2, Ctrl+T opens a new tab (maps to Cmd+T).

    iTerm2 is excluded from the Cmd<->Ctrl swap, so its corner key stays real Ctrl;
    this lets Linux-style Ctrl+T open a tab while native Cmd+T still works. Plain
    Ctrl+T only (no Shift/Cmd), so Ctrl+Shift+T and the Cmd+Ctrl+T launcher are
    left untouched.
    """
    return {
        "description": f"{marker} LinX: iTerm2 Ctrl+T -> new tab (Cmd+T)",
        "manipulators": [
            {
                "type": "basic",
                "from": {
                    "key_code": "t",
                    "modifiers": {"mandatory": ["left_control"]},
                },
                "to": [{"key_code": "t", "modifiers": ["left_command"]}],
                "conditions": [
                    {
                        "type": "frontmost_application_if",
                        "bundle_identifiers": ["^com\\.googlecode\\.iterm2$"],
                    }
                ],
            }
        ],
    }


def build_linx_layer(marker: str) -> list[dict]:
    """Build the Linux muscle-memory layer rules in Karabiner evaluation order.

    The Cmd+Ctrl / Ctrl+Alt chord rules (Volume/Brightness, workspace switch,
    screenshot, iTerm new-tab) come first — they must precede the Cmd/Ctrl swap or
    it rewrites their modifiers — then the swap, then Home/End. The Cmd+Ctrl iTerm
    launcher is assembled ahead of the swap in generate_rules(), so it is not here.
    """
    return [
        build_volume_brightness_rule(marker),
        build_workspace_switch_rule(marker),
        build_screenshot_rule(marker),
        build_iterm_new_tab_rule(marker),
        build_swap_cmd_ctrl_rule(marker),
        build_home_end_rule(marker),
    ]
