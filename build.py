# FILE: build.py
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from src.rules import generate_rules, MARKER
from src.rules.linx import build_linx_layer

KARABINER_CLI = Path(
    "/Library/Application Support/org.pqrs/Karabiner-Elements/bin/karabiner_cli"
)


def lint_rules(rules: list, label: str) -> bool:
    """Validate generated rules with karabiner_cli --lint-complex-modifications.

    Writes the rules to a temp file in complex_modifications asset shape
    ({"title", "rules"}) and lints it. Best-effort: if karabiner_cli is absent
    (e.g. building on a machine without Karabiner-Elements), the check is skipped.
    Returns True when valid or skipped, False when the linter reports problems.
    """
    if not KARABINER_CLI.exists():
        print(f"⚠️  Lint skipped for {label}: karabiner_cli not found.")
        return True

    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=True, encoding="utf-8"
    ) as fh:
        json.dump({"title": label, "rules": rules}, fh)
        fh.flush()
        result = subprocess.run(
            [str(KARABINER_CLI), "--lint-complex-modifications", fh.name],
            capture_output=True,
            text=True,
        )

    output = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        print(f"✅ Lint passed for {label} ({len(rules)} rule(s)).")
        return True
    print(f"❌ Lint FAILED for {label}:\n{output}")
    return False


def ensure_default_profile(profiles: list) -> None:
    """Ensure that a blank 'Default' profile always exists."""
    if not any(p.get("name") == "Default" for p in profiles):
        profiles.append(
            {
                "name": "Default",
                "selected": False,
                "complex_modifications": {"rules": []},
            }
        )


def set_selected_profile(profiles: list, target_name: str) -> None:
    """Mark exactly one profile as selected, deselecting all others."""
    for profile in profiles:
        profile["selected"] = profile.get("name") == target_name


def merge_marker_rules(profile: dict, new_rules: list, override: bool) -> list:
    """Merge MARKER-tagged rules into a profile, preserving community rules.

    Returns the descriptions of the rules that were written, for reporting.
    """
    existing_rules = profile.get("complex_modifications", {}).get("rules", [])
    if override:
        profile["complex_modifications"]["rules"] = new_rules
        return [r["description"] for r in new_rules]

    preserved = [r for r in existing_rules if MARKER not in r.get("description", "")]
    profile.setdefault("complex_modifications", {})["rules"] = preserved + new_rules
    return [r["description"] for r in new_rules]


def ensure_linx_profile(profiles: list, override: bool, verbose: bool) -> dict:
    """Build or refresh the LinX profile (GenX + Linux muscle-memory layer).

    LinX deliberately carries no ``simple_modifications`` — the corner-key remap is
    handled by the Left Cmd<->Ctrl swap rule, not by the PoweredX fn rotation.
    """
    linx_profile = next((p for p in profiles if p.get("name") == "LinX"), None)
    if linx_profile is None:
        linx_profile = {
            "name": "LinX",
            "virtual_hid_keyboard": {"keyboard_type_v2": "ansi"},
            "complex_modifications": {"rules": []},
            "selected": False,
        }
        profiles.append(linx_profile)

    written = merge_marker_rules(linx_profile, generate_rules(linx=True), override)
    if verbose:
        print(f"[Verbose] LinX profile now holds {len(written)} GenX/LinX rule(s).")
    return linx_profile


def get_karabiner_path() -> Path:
    """Ensure karabiner directory exists and return its config path."""
    karabiner_dir = Path("karabiner")
    karabiner_dir.mkdir(exist_ok=True)
    return karabiner_dir / "karabiner.json"


def modify_existing_karabiner(
    dry_run: bool = False,
    verbose: bool = False,
    override: bool = False,
    linx: bool = False,
) -> None:
    """Safely merge or override Karabiner rules in karabiner/karabiner.json.

    Always refreshes the PoweredX (GenX) profile. When ``linx`` is True, additionally
    builds/refreshes a LinX profile (GenX + Linux muscle-memory layer) and selects it;
    otherwise PoweredX stays selected and any existing LinX profile is deselected
    (never deleted).
    """
    path = get_karabiner_path()
    if path.exists():
        try:
            config = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"Error: {path} contains invalid JSON: {e}")
            return
    else:
        config = {"profiles": []}
    profiles = config.get("profiles", [])
    ensure_default_profile(profiles)

    poweredx_profile = next((p for p in profiles if p.get("name") == "PoweredX"), None)
    if poweredx_profile is None:
        poweredx_profile = {
            "name": "PoweredX",
            "complex_modifications": {"rules": []},
            "selected": False,
        }
        profiles.append(poweredx_profile)

    existing_count = len(
        poweredx_profile.get("complex_modifications", {}).get("rules", [])
    )
    modified_rules = merge_marker_rules(
        poweredx_profile, generate_rules(linx=False), override
    )
    if verbose:
        mode = "Overrode" if override else "Merged"
        print(f"[Verbose] {mode} PoweredX (had {existing_count} rule(s)).")

    if linx:
        ensure_linx_profile(profiles, override, verbose)
        set_selected_profile(profiles, "LinX")
    else:
        set_selected_profile(profiles, "PoweredX")

    config["profiles"] = profiles
    selected = next((p["name"] for p in profiles if p.get("selected")), None)

    # Validate the rules this builder adds before writing to disk. The pre-existing
    # GenX hyper sublayers use a lenient structure Karabiner accepts at runtime but
    # the strict linter rejects, so we lint only the Linux-muscle-memory layer here.
    if linx and not lint_rules(build_linx_layer(MARKER), "LinX layer"):
        print("⚠️  Lint reported problems above; aborting write. Fix rules and retry.")
        return

    if dry_run:
        print("\n--- Dry Run Output ---")
        preview = {
            "config_path": str(path),
            "linx": linx,
            "override": override,
            "selected_profile": selected,
            "profiles": [p.get("name") for p in profiles],
            "poweredx_rules_modified": modified_rules,
            "total_poweredx_rules": len(
                poweredx_profile["complex_modifications"]["rules"]
            ),
        }
        if linx:
            linx_profile = next(p for p in profiles if p.get("name") == "LinX")
            preview["total_linx_rules"] = len(
                linx_profile["complex_modifications"]["rules"]
            )
        print(json.dumps(preview, indent=2))
        print("--- End of Dry Run ---\n")
        return

    path.write_text(json.dumps(config, indent=4))
    print(
        f"✅ {'Overrode' if override else 'Merged'} {MARKER} rules into '{path}' safely."
    )
    if linx:
        print("✅ Built/refreshed 'LinX' profile (GenX + Linux layer) and selected it.")
    print(f"✅ Selected profile: {selected}.")
    print("✅ Ensured blank 'Default' profile exists.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge or override PoweredX Karabiner rules safely."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without saving"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed merge info"
    )
    parser.add_argument(
        "--override", action="store_true", help="Completely replace PoweredX rules"
    )
    parser.add_argument(
        "--linx",
        action="store_true",
        help="Also build/select the LinX profile (GenX + Linux muscle-memory layer)",
    )
    args = parser.parse_args()

    modify_existing_karabiner(
        dry_run=args.dry_run,
        verbose=args.verbose,
        override=args.override,
        linx=args.linx,
    )


if __name__ == "__main__":
    main()
