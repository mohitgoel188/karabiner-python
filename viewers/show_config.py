# FILE: show_config.py
import argparse

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

from src.rules import DEFAULT_PROFILE, PROFILE_NAMES, generate_rules

MODIFIER_SYMBOLS = {
    "left_command": "\u2318",
    "right_command": "\u2318",
    "left_control": "\u2303",
    "right_control": "\u2303",
    "left_option": "\u2325",
    "right_option": "\u2325",
    "left_shift": "\u21e7",
    "right_shift": "\u21e7",
}

KEY_LABELS = {
    "grave_accent_and_tilde": "`",
    "hyphen": "-",
    "equal_sign": "=",
    "open_bracket": "[",
    "close_bracket": "]",
    "backslash": "\\",
    "semicolon": ";",
    "quote": "'",
    "comma": ",",
    "period": ".",
    "slash": "/",
    "spacebar": "Space",
    "return_or_enter": "Enter",
    "caps_lock": "Caps",
    "escape": "Esc",
    "tab": "Tab",
    "delete_or_backspace": "Del",
    "left_arrow": "\u2190",
    "right_arrow": "\u2192",
    "up_arrow": "\u2191",
    "down_arrow": "\u2193",
    "page_up": "PgUp",
    "page_down": "PgDn",
    "volume_increment": "Vol+",
    "volume_decrement": "Vol-",
    "display_brightness_increment": "Bri+",
    "display_brightness_decrement": "Bri-",
    "play_or_pause": "\u23ef Play",
    "fastforward": "\u23ed Next",
    "rewind": "\u23ee Prev",
}

LAYER_INFO = {
    "b": ("Bookmarks", "blue"),
    "o": ("Open Apps", "magenta"),
    "w": ("Window Mgmt", "yellow"),
    "s": ("System", "green"),
    "v": ("Vim Nav", "red"),
    "c": ("Music", "cyan"),
    "r": ("Raycast", "bright_yellow"),
    "spacebar": ("Quick Action", "bright_magenta"),
}

CAT_STYLES = {
    "App": "bold magenta",
    "URL": "bold blue",
    "Raycast": "bold yellow",
    "Window": "bold bright_yellow",
    "Shell": "bold green",
    "Key": "bold red",
}


def _friendly_key(key_code: str) -> str:
    if key_code in KEY_LABELS:
        return KEY_LABELS[key_code]
    return key_code.upper() if len(key_code) == 1 else key_code


def _friendly_mods(mods: list[str]) -> str:
    return "".join(MODIFIER_SYMBOLS.get(m, m) for m in mods)


def _describe_action(action) -> str:
    if isinstance(action, str):
        return action[:60]
    if not isinstance(action, dict):
        return str(action)[:60]
    if "shell_command" in action:
        cmd = action["shell_command"]
        if cmd.startswith("open -a"):
            name = cmd.split("open -a ")[-1].replace(".app", "").strip("'")
            return f"App: {name}"
        if cmd.startswith("open http"):
            return f"URL: {cmd.replace('open ', '').strip(chr(39))}"
        if "raycast://" in cmd:
            parts = cmd.strip("'").split("/")
            ext = parts[-2] if len(parts) >= 2 else ""
            command = parts[-1].split("?")[0] if parts else ""
            return f"Raycast: {ext}/{command}"
        if "rectangle://" in cmd:
            name = cmd.split("name=")[-1].strip("'") if "name=" in cmd else cmd
            return f"Window: {name}"
        return f"Shell: {cmd[:50]}"
    if "key_code" in action:
        mods = action.get("modifiers", [])
        mod_str = _friendly_mods(mods) if mods else ""
        return f"Key: {mod_str}{_friendly_key(action['key_code'])}"
    if "set_variable" in action:
        return "Toggle sublayer"
    # Nested dict with only "to" (no description) — e.g. {"to": [{"key_code": "left_arrow"}]}
    if "to" in action and "description" not in action:
        to_list = action.get("to", [])
        if to_list and isinstance(to_list[0], dict):
            return _describe_action(to_list[0])
    desc = action.get("description", "")
    to = action.get("to", [])
    if desc and to:
        to_action = to[0] if to else {}
        if isinstance(to_action, dict) and "key_code" in to_action:
            mods = to_action.get("modifiers", [])
            mod_str = _friendly_mods(mods) if mods else ""
            key_str = _friendly_key(to_action["key_code"])
            label = desc.split(": ", 1)[-1] if ": " in desc else desc
            return f"{label} ({mod_str}{key_str})"
        return desc.split(": ", 1)[-1] if ": " in desc else desc
    if desc:
        return desc.split(": ", 1)[-1] if ": " in desc else desc
    return str(action)[:60]


def _styled_action(action_str: str) -> Text:
    """Return a rich Text with the category prefix styled."""
    for cat, style in CAT_STYLES.items():
        prefix = f"{cat}: "
        if action_str.startswith(prefix):
            t = Text()
            t.append(f"[{cat}]", style=style)
            t.append(f" {action_str[len(prefix):]}")
            return t
    return Text(action_str)


def extract_sublayers(rules: list) -> dict:
    sublayers = {}
    for rule in rules:
        desc = rule.get("description", "")
        if "Hyper Key sublayer" not in desc:
            continue
        name = desc.split("'")[-2] if "'" in desc else desc
        entries = []
        for manip in rule.get("manipulators", []):
            from_key = manip.get("from", {}).get("key_code", "")
            if from_key == name:
                continue
            to_list = manip.get("to", [])
            if not to_list:
                continue
            action_str = _describe_action(to_list[0])
            entries.append((from_key, action_str))
        sublayers[name] = entries
    return sublayers


def extract_standalone(rules: list) -> list:
    standalone = []
    for rule in rules:
        desc = rule.get("description", "")
        if "Hyper Key sublayer" in desc or "Hyper Key (" in desc:
            continue
        entries = []
        for m in rule.get("manipulators", []):
            from_key = m.get("from", {}).get("key_code", "")
            from_mods = m.get("from", {}).get("modifiers", {})
            mandatory = from_mods.get("mandatory", []) if isinstance(from_mods, dict) else []
            conditions = m.get("conditions", [])
            scope = "Global"
            for c in conditions:
                bundles = c.get("bundle_identifiers", [])
                if bundles:
                    scope = ", ".join(
                        b.replace("^com\\.", "").replace("$", "").replace("\\.", ".")
                        for b in bundles
                    )
            trigger = _friendly_mods(mandatory) + _friendly_key(from_key)
            to_list = m.get("to", [])
            action_str = _describe_action(to_list[0]) if to_list else "-"
            entries.append((trigger, action_str, scope))
        standalone.append((desc.replace("GenX: ", ""), entries))
    return standalone


def render_layer(console: Console, layer: str, entries: list) -> None:
    label, color = LAYER_INFO.get(layer, (layer, "white"))
    title = f"[bold {color}]\u2328  {label} Layer [{_friendly_key(layer)}][/bold {color}]"

    table = Table(
        title=title,
        show_header=True,
        header_style=f"bold {color}",
        border_style="dim",
        padding=(0, 1),
        expand=True,
    )
    table.add_column("Key", justify="center", style=f"bold {color}", no_wrap=True, width=8)
    table.add_column("Shortcut", style="dim", no_wrap=True, width=14)
    table.add_column("Action", ratio=1)

    for from_key, action_str in entries:
        shortcut = f"Hyper+{_friendly_key(layer)}+{_friendly_key(from_key)}"
        table.add_row(
            _friendly_key(from_key),
            shortcut,
            _styled_action(action_str),
        )

    console.print(table)
    console.print()


def render_standalone(console: Console, standalone: list) -> None:
    console.print()
    table = Table(
        title="[bold bright_white]\u2699  Standalone Rules[/bold bright_white]",
        show_header=True,
        header_style="bold bright_white",
        border_style="dim",
        padding=(0, 1),
        expand=True,
    )
    table.add_column("Rule", style="bold", ratio=1)
    table.add_column("Trigger", justify="center", style="cyan", no_wrap=True, width=12)
    table.add_column("Action", ratio=1)
    table.add_column("Scope", justify="center", style="dim italic", width=18)

    for desc, entries in standalone:
        for i, (trigger, action_str, scope) in enumerate(entries):
            rule_cell = desc if i == 0 else ""
            table.add_row(rule_cell, trigger, _styled_action(action_str), scope)
        if entries:
            table.add_section()

    console.print(table)


def render_legend(console: Console) -> None:
    items = []
    for cat, style in CAT_STYLES.items():
        items.append(Text.assemble((f" [{cat}] ", style), " = ", (cat, "dim")))
    console.print(Panel(Columns(items, padding=(0, 2)), title="Legend", border_style="dim"))
    console.print()


def show_config(
    target_layer: str | None = None, profile: str = DEFAULT_PROFILE
) -> None:
    rules = generate_rules(profile)
    sublayers = extract_sublayers(rules)
    standalone = extract_standalone(rules)
    console = Console()

    if not sublayers and not standalone:
        console.print("[dim]No rules found.[/dim]")
        return

    # Header
    console.print()
    console.print(
        Panel.fit(
            f"[bold bright_white]{profile}[/bold bright_white]  "
            "[dim]Karabiner-Elements Configuration[/dim]\n"
            "[bright_magenta]Hyper Key[/bright_magenta] = "
            "Caps Lock \u2192 \u2303\u2325\u21e7\u2318  "
            "[dim]|  Tap = Esc[/dim]",
            border_style="bright_magenta",
        )
    )
    console.print()

    # Legend
    render_legend(console)

    # Sublayers
    if target_layer:
        if target_layer not in sublayers:
            console.print(f"[red]Layer '{target_layer}' not found.[/red]")
            console.print(f"[dim]Available: {', '.join(sorted(sublayers.keys()))}[/dim]")
            return
        render_layer(console, target_layer, sublayers[target_layer])
    else:
        for layer in sublayers:
            render_layer(console, layer, sublayers[layer])

    # Standalone rules
    if not target_layer and standalone:
        render_standalone(console, standalone)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pretty print a generated Karabiner profile."
    )
    parser.add_argument(
        "-l", "--layer",
        metavar="LAYER",
        help="Show only a specific layer (e.g. o, b, w, s)",
    )
    parser.add_argument(
        "-p", "--profile",
        choices=PROFILE_NAMES,
        default=DEFAULT_PROFILE,
        help=f"Profile to display (default: {DEFAULT_PROFILE})",
    )
    args = parser.parse_args()
    show_config(args.layer, args.profile)


if __name__ == "__main__":
    main()
