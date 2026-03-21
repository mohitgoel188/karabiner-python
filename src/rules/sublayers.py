from src.helpers import app, open_url, window, tuple_dict
from src.raycast import raycast


def build_sublayers(marker: str) -> dict:
    """Define all hyper sublayer key mappings."""
    return {
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
                ("c", app("Visual Studio Code")),
                ("v", app("Zed")),
                ("s", app("Slack")),
                ("i", app("iterm")),
                ("f", app("Finder")),
                ("p", app("pycharm")),
                ("w", app("Whatsapp")),
                ("x", app("Firefox")),
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
