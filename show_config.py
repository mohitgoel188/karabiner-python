# FILE: show_config.py
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from rules import generate_rules


def extract_sublayers(rules: list) -> dict:
    """Extract sublayer names, descriptions, and key mappings."""
    sublayers = {}
    for rule in rules:
        desc = rule.get("description", "")
        if "Hyper Key sublayer" not in desc:
            continue

        sublayer_name = desc.split("'")[-2] if "'" in desc else desc
        sublayers[sublayer_name] = {"description": desc, "entries": []}

        for manip in rule.get("manipulators", []):
            from_key = manip.get("from", {}).get("key_code", "")
            desc_text = manip.get("description", "")

            to_list = manip.get("to", [])
            if not to_list:
                key_action = "-"
            else:
                to_action = to_list[0]
                if isinstance(to_action, dict):
                    if "shell_command" in to_action:
                        key_action = to_action["shell_command"]
                    elif "key_code" in to_action:
                        mods = to_action.get("modifiers", [])
                        mod_str = f" ({'+'.join(mods)})" if mods else ""
                        key_action = f"{to_action['key_code']}{mod_str}"
                    else:
                        key_action = str(to_action)
                else:
                    key_action = str(to_action)

            sublayers[sublayer_name]["entries"].append(
                (from_key, desc_text or "-", key_action)
            )

    return sublayers


def display_sublayers(sublayers: dict, target: str | None = None) -> None:
    """Pretty print sublayer mappings with sublayer descriptions."""
    console = Console()
    console.print(
        Panel.fit("[bold blue]PoweredX Karabiner Rules (Built from source)[/bold blue]")
    )

    def render_layer(layer: str, data: dict) -> None:
        desc = data.get("description", "")
        entries = data.get("entries", [])

        console.print(
            Panel.fit(f"[bold green]{layer.upper()}[/bold green]\n{desc}", title="Layer Info")
        )
        table = Table(show_header=True, header_style="bold magenta", expand=False)
        table.add_column("Shortcut", justify="center", style="cyan", no_wrap=True)
        table.add_column("Function", style="yellow")
        table.add_column("Action", style="magenta")

        for key, desc_text, action in entries:
            combo = f"{layer}+{key}" if key else layer
            table.add_row(combo, desc_text, action)

        console.print(table)
        console.print("\n")

    if target:
        if target not in sublayers:
            console.print(f"❌ Layer '{target}' not found.")
            return
        render_layer(target, sublayers[target])
    else:
        for layer, data in sorted(sublayers.items()):
            render_layer(layer, data)


def show_config(target_layer: str | None = None) -> None:
    """Display PoweredX configuration directly from generated rules."""
    rules = generate_rules()
    sublayers = extract_sublayers(rules)

    if not sublayers:
        print("ℹ️  No Hyper sublayer rules found.")
        return

    display_sublayers(sublayers, target_layer)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pretty print PoweredX Karabiner configuration from source rules."
    )
    parser.add_argument(
        "-l",
        "--layer",
        metavar="LAYER",
        type=str,
        help="Show only a specific layer (e.g. o, b, w, s, etc.)",
    )
    args = parser.parse_args()
    show_config(args.layer)


if __name__ == "__main__":
    main()
