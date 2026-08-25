# FILE: build.py
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from src.rules import (
    DEFAULT_PROFILE,
    LINX,
    MACX,
    MARKER,
    POWEREDX,
    PROFILE_NAMES,
    generate_rules,
)

# Profile-level settings the generator seeds on FIRST creation only, so anything you
# later change in the Karabiner UI survives every rebuild.
ANSI_KEYBOARD = {"keyboard_type_v2": "ansi"}

# The Optimus reports as a keyboard AND a pointing device, and Karabiner ignores pointing
# devices by default — without this entry it would not be grabbed at all. These ids are
# the physical keyboard's, so they stay valid on any Mac.
OPTIMUS_DEVICE = [
    {
        "identifiers": {
            "is_keyboard": True,
            "is_pointing_device": True,
            "vendor_id": 12994,
            "product_id": 26145,
        },
        "ignore": False,
    }
]

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


def carry_over_enabled(existing_rules: list, new_rules: list) -> None:
    """Preserve the user's per-rule on/off toggles across rebuilds.

    Karabiner persists a disabled Complex Modification as a rule-level
    ``"enabled": false`` (an enabled rule just omits the key). For every
    regenerated rule that already exists (matched by description), copy the
    existing enabled-state so a rebuild never silently flips a toggle the user
    set in the UI. Brand-new rules keep whatever default the generator gave them
    (e.g. the open-iTerm launcher ships ``"enabled": false``).
    """
    existing_by_desc = {
        r["description"]: r for r in existing_rules if "description" in r
    }
    for rule in new_rules:
        existing = existing_by_desc.get(rule.get("description"))
        if existing is None:
            continue
        if "enabled" in existing:
            rule["enabled"] = existing["enabled"]
        else:
            rule.pop("enabled", None)


def merge_marker_rules(profile: dict, new_rules: list, override: bool) -> list:
    """Merge MARKER-tagged rules into a profile, preserving community rules.

    Returns the descriptions of the rules that were written, for reporting.
    """
    existing_rules = profile.get("complex_modifications", {}).get("rules", [])
    carry_over_enabled(existing_rules, new_rules)
    if override:
        profile.setdefault("complex_modifications", {})["rules"] = new_rules
        return [r["description"] for r in new_rules]

    preserved = [r for r in existing_rules if MARKER not in r.get("description", "")]
    profile.setdefault("complex_modifications", {})["rules"] = preserved + new_rules
    return [r["description"] for r in new_rules]


def ensure_profile(
    profiles: list,
    name: str,
    override: bool,
    verbose: bool,
    *,
    devices: list | None = None,
) -> dict:
    """Build or refresh one named profile, creating it if absent.

    Only ``complex_modifications.rules`` is rewritten, so hand-made profile-level settings
    survive every rebuild: PoweredX's ``simple_modifications`` fn rotation, LinX's
    ``devices`` block, mouse settings, and so on. ``devices`` is seeded on first creation
    only, for the same reason.

    MacX is deliberately created WITHOUT ``simple_modifications``: its globe/Control remap
    is a device-scoped complex modification, because Karabiner reports no vendor/product id
    for the built-in keyboard and so cannot target it from a ``devices`` block.
    """
    profile = next((p for p in profiles if p.get("name") == name), None)
    if profile is None:
        profile = {
            "name": name,
            "virtual_hid_keyboard": dict(ANSI_KEYBOARD),
            "complex_modifications": {"rules": []},
            "selected": False,
        }
        if devices is not None:
            profile["devices"] = [dict(d) for d in devices]
        profiles.append(profile)

    existing_count = len(profile.get("complex_modifications", {}).get("rules", []))
    written = merge_marker_rules(profile, generate_rules(name), override)
    if verbose:
        mode = "Overrode" if override else "Merged"
        print(
            f"[Verbose] {mode} {name}: {len(written)} {MARKER} rule(s) "
            f"(had {existing_count})."
        )
    return profile


def get_karabiner_path() -> Path:
    """Ensure karabiner directory exists and return its config path."""
    karabiner_dir = Path("karabiner")
    karabiner_dir.mkdir(exist_ok=True)
    return karabiner_dir / "karabiner.json"


def modify_existing_karabiner(
    dry_run: bool = False,
    verbose: bool = False,
    override: bool = False,
    select: str = DEFAULT_PROFILE,
) -> None:
    """Safely merge or override Karabiner rules in karabiner/karabiner.json.

    Every profile in PROFILE_NAMES (PoweredX, LinX, MacX) is rebuilt on each run so they
    never drift apart; only which one is ``selected`` differs between invocations.
    Profiles are never deleted, and the blank Default profile is always kept.
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

    rule_counts: dict[str, int] = {}
    for name in PROFILE_NAMES:
        profile = ensure_profile(
            profiles,
            name,
            override,
            verbose,
            devices=OPTIMUS_DEVICE if name == MACX else None,
        )
        rule_counts[name] = len(profile["complex_modifications"]["rules"])

    set_selected_profile(profiles, select)
    config["profiles"] = profiles

    # Validate every generated rule — hyper sublayers included — before writing to disk.
    # This used to lint only the LinX/MacX layers, on the theory that the sublayers used a
    # lenient shape the strict linter rejected. They were in fact malformed, and Karabiner
    # rejected them at runtime too; the gate is now wide enough to catch that class of bug.
    layers = tuple((f"{name} profile", generate_rules(name)) for name in PROFILE_NAMES)
    # A list comprehension, not a generator: report every layer even if an early one fails.
    if not all([lint_rules(rules, label) for label, rules in layers]):
        print("⚠️  Lint reported problems above; aborting write. Fix rules and retry.")
        return

    if dry_run:
        print("\n--- Dry Run Output ---")
        print(
            json.dumps(
                {
                    "config_path": str(path),
                    "override": override,
                    "selected_profile": select,
                    "profiles": [p.get("name") for p in profiles],
                    "rules_per_profile": rule_counts,
                },
                indent=2,
            )
        )
        print("--- End of Dry Run ---\n")
        return

    path.write_text(json.dumps(config, indent=4))
    print(
        f"✅ {'Overrode' if override else 'Merged'} {MARKER} rules into '{path}' safely."
    )
    for name in PROFILE_NAMES:
        print(f"✅ {name}: {rule_counts[name]} rule(s).")
    print(f"✅ Selected profile: {select}.")
    print("✅ Ensured blank 'Default' profile exists.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build the PoweredX / LinX / MacX Karabiner profiles safely. All three are "
            f"rebuilt on every run; the flags below only choose which one is selected "
            f"(default: {DEFAULT_PROFILE})."
        )
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without saving"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed merge info"
    )
    parser.add_argument(
        "--override",
        action="store_true",
        help=(
            f"Replace all rules in EVERY profile instead of merging. Drops any non-"
            f"{MARKER} rules you added by hand or from the community."
        ),
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--profile",
        choices=PROFILE_NAMES,
        help=f"Profile to select after building (default: {DEFAULT_PROFILE})",
    )
    group.add_argument(
        "--macx",
        dest="select",
        action="store_const",
        const=MACX,
        help="Select MacX (native macOS modifiers) — the default",
    )
    group.add_argument(
        "--linx",
        dest="select",
        action="store_const",
        const=LINX,
        help="Select LinX (Linux muscle-memory layer)",
    )
    group.add_argument(
        "--poweredx",
        dest="select",
        action="store_const",
        const=POWEREDX,
        help="Select PoweredX (the original GenX set)",
    )
    parser.set_defaults(select=None)
    args = parser.parse_args()

    modify_existing_karabiner(
        dry_run=args.dry_run,
        verbose=args.verbose,
        override=args.override,
        select=args.profile or args.select or DEFAULT_PROFILE,
    )


if __name__ == "__main__":
    main()
