# FILE: rules.py
from models import Rule
from utils import app, open_url, window, create_hyper_sublayers
from raycast_utils import raycast

MARKER = "GenX"


def tuple_dict(pairs: list[tuple[str, dict]]) -> dict:
    """Convert list of (key, action) tuples to dict and detect duplicates."""
    seen = {}
    duplicates = []
    for key, action in pairs:
        if key in seen:
            duplicates.append(key)
        seen[key] = action
    if duplicates:
        print(f"⚠️ Duplicate key(s) detected: {', '.join(duplicates)}")
    return seen


def generate_rules() -> list:
    """Generate PoweredX Karabiner rules with proper descriptions."""
    base_rule = Rule(
        description=f"{MARKER}: Hyper Key (⌃⌥⇧⌘)",
        manipulators=[
            {
                "description": f"{MARKER}: Caps Lock -> Hyper Key",
                "from": {"key_code": "caps_lock", "modifiers": {"optional": ["any"]}},
                "to": [{"set_variable": {"name": "hyper", "value": 1}}],
                "to_after_key_up": [{"set_variable": {"name": "hyper", "value": 0}}],
                "to_if_alone": [{"key_code": "escape"}],
                "type": "basic",
            }
        ],
    )

    sublayers = {
        "spacebar": raycast("stellate/mxstbr-commands", "create-notion-todo"),
        "b": tuple_dict(
            [
                ("t", open_url("https://twitter.com")),
                ("p", open_url("https://mxstbr.com/cal")),
                ("y", open_url("https://news.ycombinator.com")),
                ("f", open_url("https://facebook.com")),
                ("r", open_url("https://reddit.com")),
                ("h", open_url("https://hashnode.com/draft")),
            ]
        ),
        "o": tuple_dict(
            [
                # ("1", app("1Password")),
                # ("g", app("Google Chrome")),
                ("c", app("Visual Studio Code.app")),
                ("v", app("Zed")),
                ("s", app("Slack")),
                # ("e", app("Superhuman")),
                ("t", app("iterm")),
                # ("h", open_url("notion://www.notion.so/stellatehq/7b33b924746647499d906c55f89d5026")),
                # ("z", app("zoom.us")),
                # ("m", app("Reflect")),
                # ("r", app("Reflect")),
                ("f", app("Finder")),
                # ("i", app("Texts")),
                # ("p", app("Spotify")),
                # ("a", app("iA Presenter")),
                ("p", app("pycharm.app")),
                ("w", app("Whatsapp")),
                # ("l", raycast("stellate/mxstbr-commands", "open-mxs-is-shortlink")),
                ("x", app("Firefox"))
            ]
        ),
        "w": tuple_dict(
            [
                ("semicolon", {"description": "Window: Hide", "to": [{"key_code": "h", "modifiers": ["right_command"]}]}),
                ("y", window("previous-display")),
                ("o", window("next-display")),
                ("k", window("top-half")),
                ("j", window("bottom-half")),
                ("h", window("left-half")),
                ("l", window("right-half")),
                ("f", window("maximize")),
                ("u", {"description": "Window: Previous Tab", "to": [{"key_code": "tab", "modifiers": ["right_control", "right_shift"]}]}),
                ("i", {"description": "Window: Next Tab", "to": [{"key_code": "tab", "modifiers": ["right_control"]}]}),
                ("n", {"description": "Window: Next Window", "to": [{"key_code": "grave_accent_and_tilde", "modifiers": ["right_command"]}]}),
                ("b", {"description": "Window: Back", "to": [{"key_code": "open_bracket", "modifiers": ["right_command"]}]}),
                ("m", {"description": "Window: Forward", "to": [{"key_code": "close_bracket", "modifiers": ["right_command"]}]}),
            ]
        ),
        "s": tuple_dict(
            [
                ("u", {"description": "System: Volume Up", "to": [{"key_code": "volume_increment"}]}),
                ("j", {"description": "System: Volume Down", "to": [{"key_code": "volume_decrement"}]}),
                ("i", {"description": "System: Brightness Up", "to": [{"key_code": "display_brightness_increment"}]}),
                ("k", {"description": "System: Brightness Down", "to": [{"key_code": "display_brightness_decrement"}]}),
                ("l", {"description": "System: Quit App", "to": [{"key_code": "q", "modifiers": ["right_control", "right_command"]}]}),
                ("p", {"description": "System: Play/Pause", "to": [{"key_code": "play_or_pause"}]}),
                ("semicolon", {"description": "System: Next Track", "to": [{"key_code": "fastforward"}]}),
                ("e", raycast("thomas/elgato-key-light", "toggle", background=True)),
                ("d", raycast("yakitrak/do-not-disturb", "toggle", background=True)),
                ("t", raycast("raycast/system", "toggle-system-appearance")),
                ("c", raycast("raycast/system", "open-camera")),
                ("v", {"description": "System: Voice", "to": [{"key_code": "spacebar", "modifiers": ["left_option"]}]}),
            ]
        ),
        "v": tuple_dict(
            [
                ("h", {"to": [{"key_code": "left_arrow"}]}),
                ("j", {"to": [{"key_code": "down_arrow"}]}),
                ("k", {"to": [{"key_code": "up_arrow"}]}),
                ("l", {"to": [{"key_code": "right_arrow"}]}),
                ("m", {"description": "Move: Magicmove (Homerow)", "to": [{"key_code": "f", "modifiers": ["right_control"]}]}),
                ("s", {"description": "Move: Scroll Mode (Homerow)", "to": [{"key_code": "j", "modifiers": ["right_control"]}]}),
                ("d", {"description": "Move: Vim Easymotion", "to": [{"key_code": "d", "modifiers": ["right_shift", "right_command"]}]}),
                ("u", {"to": [{"key_code": "page_down"}]}),
                ("i", {"to": [{"key_code": "page_up"}]}),
            ]
        ),
        "c": tuple_dict(
            [
                ("p", {"description": "Music: Play/Pause", "to": [{"key_code": "play_or_pause"}]}),
                ("n", {"description": "Music: Next Track", "to": [{"key_code": "fastforward"}]}),
                ("b", {"description": "Music: Previous Track", "to": [{"key_code": "rewind"}]}),
            ]
        ),
        "r": tuple_dict(
            [
                ("c", raycast("thomas/color-picker", "pick-color")),
                ("n", open_url("raycast://script-commands/dismiss-notifications")),
                ("l", raycast("stellate/mxstbr-commands", "create-mxs-is-shortlink")),
                ("e", raycast("raycast/emoji-symbols", "search-emoji-symbols")),
                ("p", raycast("raycast/raycast", "confetti")),
                ("a", raycast("raycast/raycast-ai", "ai-chat")),
                ("s", raycast("peduarte/silent-mention", "index")),
                ("h", raycast("raycast/clipboard-history", "clipboard-history")),
                ("1", raycast("VladCuciureanu/toothpick", "toggle-favorite-device-1")),
                ("2", raycast("VladCuciureanu/toothpick", "toggle-favorite-device-2")),
            ]
        ),
    }

    # Add double-tap right Shift -> Caps Lock
    double_shift_caps_lock = {
        "description": f"{MARKER}: Change double tap right ⇧ key to caps lock",
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

    swap_cmd_ctrl_rule = {
        "description": f"{MARKER}: Swap Command and Control in PyCharm",
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
                            # "^com\\.microsoft\\.VSCode$",
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
                            # "^com\\.microsoft\\.VSCode$",
                        ],
                    }
                ],
            },
        ],
    }

    # Return all rules in final configuration
    return [
        base_rule.__dict__,
        *create_hyper_sublayers(sublayers, MARKER),
        double_shift_caps_lock,
        swap_cmd_ctrl_rule
    ]
