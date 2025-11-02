# FILE: rules.py
from models import Rule
from utils import app, open_url, window, create_hyper_sublayers
from raycast_utils import raycast

MARKER = "PoweredX"


def tuple_dict(pairs: list[tuple[str, dict]]) -> dict:
    """Convert list of (key, action) tuples to dict and detect duplicates."""
    seen = {}
    duplicates = []
    for key, action in pairs:
        if key in seen:
            duplicates.append(key)
        seen[key] = action
    if duplicates:
        print(
            f"⚠️  Duplicate key(s) detected in sublayer definition: {', '.join(duplicates)}"
        )
    return seen


def generate_rules() -> list:
    """Generate full PoweredX Karabiner rules equivalent to original upload."""
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
        # Spacebar
        "spacebar": raycast("stellate/mxstbr-commands", "create-notion-todo"),
        # Browse
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
        # Open apps
        "o": tuple_dict(
            [
                ("1", app("1Password")),
                ("g", app("Google Chrome")),
                ("c", app("Notion Calendar")),
                ("v", app("Zed")),
                ("d", app("Discord")),
                ("s", app("Slack")),
                ("e", app("Superhuman")),
                ("n", app("Notion")),
                ("t", app("Terminal")),
                ("h", open_url("notion://www.notion.so/stellatehq/7b33b924746647499d906c55f89d5026")),
                ("z", app("zoom.us")),
                ("m", app("Reflect")),
                ("r", app("Reflect")),
                ("f", app("Finder")),
                ("i", app("Texts")),
                ("p", app("Spotify")),
                ("a", app("iA Presenter")),
                ("w", open_url("Texts")),
                ("l", raycast("stellate/mxstbr-commands", "open-mxs-is-shortlink")),
            ]
        ),
        # Window management
        "w": tuple_dict(
            [
                ("semicolon", {"to": [{"key_code": "h", "modifiers": ["right_command"]}]}),
                ("y", window("previous-display")),
                ("o", window("next-display")),
                ("k", window("top-half")),
                ("j", window("bottom-half")),
                ("h", window("left-half")),
                ("l", window("right-half")),
                ("f", window("maximize")),
                ("u", {"to": [{"key_code": "tab", "modifiers": ["right_control", "right_shift"]}]}),
                ("i", {"to": [{"key_code": "tab", "modifiers": ["right_control"]}]}),
                ("n", {"to": [{"key_code": "grave_accent_and_tilde", "modifiers": ["right_command"]}]}),
                ("b", {"to": [{"key_code": "open_bracket", "modifiers": ["right_command"]}]}),
                ("m", {"to": [{"key_code": "close_bracket", "modifiers": ["right_command"]}]}),
                ("d", {"to": [{"key_code": "right_arrow", "modifiers": ["right_control", "right_option", "right_command"]}]}),
            ]
        ),
        # System
        "s": tuple_dict(
            [
                ("u", {"to": [{"key_code": "volume_increment"}]}),
                ("j", {"to": [{"key_code": "volume_decrement"}]}),
                ("i", {"to": [{"key_code": "display_brightness_increment"}]}),
                ("k", {"to": [{"key_code": "display_brightness_decrement"}]}),
                ("p", {"to": [{"key_code": "play_or_pause"}]}),
                ("semicolon", {"to": [{"key_code": "fastforward"}]}),
                ("e", raycast("thomas/elgato-key-light", "toggle", background=True)),
                ("d", raycast("yakitrak/do-not-disturb", "toggle", background=True)),
                ("t", raycast("raycast/system", "toggle-system-appearance")),
                ("c", raycast("raycast/system", "open-camera")),
                ("v", {"to": [{"key_code": "spacebar", "modifiers": ["left_option"]}]}),
            ]
        ),
        # Vim
        "v": tuple_dict(
            [
                ("h", {"to": [{"key_code": "left_arrow"}]}),
                ("j", {"to": [{"key_code": "down_arrow"}]}),
                ("k", {"to": [{"key_code": "up_arrow"}]}),
                ("l", {"to": [{"key_code": "right_arrow"}]}),
                ("u", {"to": [{"key_code": "page_down"}]}),
                ("i", {"to": [{"key_code": "page_up"}]}),
            ]
        ),
        # Control Media
        "c": tuple_dict(
            [
                ("p", {"to": [{"key_code": "play_or_pause"}]}),
                ("n", {"to": [{"key_code": "fastforward"}]}),
                ("b", {"to": [{"key_code": "rewind"}]}),
            ]
        ),
        # Raycast
        "r": tuple_dict(
            [
                ("1", raycast("VladCuciureanu/toothpick", "connect-favorite-device-1")),
                ("2", raycast("VladCuciureanu/toothpick", "connect-favorite-device-2")),
                ("c", raycast("thomas/color-picker", "pick-color")),
                ("n", open_url("raycast://script-commands/dismiss-notifications")),
                ("l", raycast("stellate/mxstbr-commands", "create-mxs-is-shortlink")),
                ("e", raycast("raycast/emoji-symbols", "search-emoji-symbols")),
                ("p", raycast("raycast/raycast", "confetti")),
                ("a", raycast("raycast/raycast-ai", "ai-chat")),
                ("s", raycast("peduarte/silent-mention", "index")),
                ("h", raycast("raycast/clipboard-history", "clipboard-history")),
            ]
        ),
    }

    return [base_rule.__dict__] + create_hyper_sublayers(sublayers, MARKER)
