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

# Firefox families the Linux-style browser shortcuts apply to.
_FIREFOX_BUNDLE_IDS: list[str] = [
    "^org\\.mozilla\\.firefox$",
    "^org\\.mozilla\\.firefoxdeveloperedition$",
    "^org\\.mozilla\\.nightly$",
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


def build_iterm_shortcuts_rule(marker: str) -> dict:
    """In iTerm2, map Linux-style Ctrl shortcuts onto their Cmd equivalents.

    iTerm2 is intentionally excluded from the Cmd<->Ctrl swap so its corner key
    stays real Ctrl and Ctrl+C remains SIGINT (Linux terminal behavior). These
    targeted rules give back the conveniences without losing interrupt:

    - Ctrl+T -> Cmd+T   (new tab)
    - Ctrl+V -> Cmd+V   (paste)

    Plain Ctrl+<key> only (no Shift/Cmd), so Ctrl+Shift+* and Cmd chords are
    untouched, and Ctrl+C is left alone as interrupt.
    """
    iterm_if = [
        {
            "type": "frontmost_application_if",
            "bundle_identifiers": ["^com\\.googlecode\\.iterm2$"],
        }
    ]
    return {
        "description": (
            f"{marker} LinX: iTerm2 Ctrl+T -> new tab, Ctrl+V -> paste "
            "(corner key keeps Ctrl+C = SIGINT)"
        ),
        "manipulators": [
            {
                "type": "basic",
                "from": {
                    "key_code": "t",
                    "modifiers": {"mandatory": ["left_control"]},
                },
                "to": [{"key_code": "t", "modifiers": ["left_command"]}],
                "conditions": iterm_if,
            },
            {
                "type": "basic",
                "from": {
                    "key_code": "v",
                    "modifiers": {"mandatory": ["left_control"]},
                },
                "to": [{"key_code": "v", "modifiers": ["left_command"]}],
                "conditions": iterm_if,
            },
        ],
    }


def build_firefox_shortcuts_rule(marker: str) -> dict:
    """Restore Linux Firefox muscle-memory that the Cmd<->Ctrl swap can't cover.

    Firefox is NOT excluded from the swap, so corner-key Ctrl chords (new tab,
    close, address bar, reload, find, reopen tab, Ctrl+1..9) already reach Firefox
    as their Cmd equivalents. These extra mappings handle the cases the swap leaves
    broken, scoped to Firefox only:

    - Alt+Left / Alt+Right  -> Cmd+[ / Cmd+]   (back / forward; Option+arrow is
      otherwise inert in Mac Firefox). Trade-off: Option+arrow no longer does
      word-wise cursor motion inside Firefox text fields.
    - Ctrl+Shift+I -> Cmd+Opt+I   (toggle Developer Tools / inspector)
    - Ctrl+Shift+C -> Cmd+Opt+C   (element picker, the right-click "Inspect" tool)

    Sidebar collapse (Linux Ctrl+Alt+Z) needs no rule here: the swap already turns
    physical Ctrl+Alt+Z into Cmd+Alt+Z, so just bind the sidebar extension to
    ⌘⌥Z in about:addons > Manage Extension Shortcuts.

    Sits ABOVE the Cmd<->Ctrl swap and matches the PHYSICAL corner key
    (left_control), mirroring build_workspace_switch_rule.
    """
    firefox_if = [
        {
            "type": "frontmost_application_if",
            "bundle_identifiers": _FIREFOX_BUNDLE_IDS,
        }
    ]
    return {
        "description": (
            f"{marker} LinX: Firefox Linux keys — Alt+Arrow = back/forward, "
            "Ctrl+Shift+I/C = inspector/picker (corner key)"
        ),
        "manipulators": [
            {
                "type": "basic",
                "from": {
                    "key_code": "left_arrow",
                    "modifiers": {"mandatory": ["left_option"]},
                },
                "to": [{"key_code": "open_bracket", "modifiers": ["left_command"]}],
                "conditions": firefox_if,
            },
            {
                "type": "basic",
                "from": {
                    "key_code": "right_arrow",
                    "modifiers": {"mandatory": ["left_option"]},
                },
                "to": [{"key_code": "close_bracket", "modifiers": ["left_command"]}],
                "conditions": firefox_if,
            },
            {
                "type": "basic",
                "from": {
                    "key_code": "i",
                    "modifiers": {"mandatory": ["left_control", "shift"]},
                },
                "to": [{"key_code": "i", "modifiers": ["left_command", "left_option"]}],
                "conditions": firefox_if,
            },
            {
                "type": "basic",
                "from": {
                    "key_code": "c",
                    "modifiers": {"mandatory": ["left_control", "shift"]},
                },
                "to": [{"key_code": "c", "modifiers": ["left_command", "left_option"]}],
                "conditions": firefox_if,
            },
        ],
    }


def build_linx_layer(marker: str) -> list[dict]:
    """Build the Linux muscle-memory layer rules in Karabiner evaluation order.

    The Cmd+Ctrl / Ctrl+Alt chord rules (Volume/Brightness, workspace switch,
    iTerm new-tab, Firefox Linux keys) come first — they must precede the Cmd/Ctrl
    swap or it rewrites their modifiers — then the swap, then Home/End. The Cmd+Ctrl
    iTerm launcher is assembled ahead of the swap in generate_rules(), so it is not
    here.
    """
    return [
        build_volume_brightness_rule(marker),
        build_workspace_switch_rule(marker),
        build_iterm_shortcuts_rule(marker),
        build_firefox_shortcuts_rule(marker),
        build_swap_cmd_ctrl_rule(marker),
        build_home_end_rule(marker),
    ]
