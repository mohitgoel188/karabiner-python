# FILE: build.py
import argparse
import json
from pathlib import Path

from rules import generate_rules, MARKER


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


def get_karabiner_path() -> Path:
    """Ensure karabiner directory exists and return its config path."""
    karabiner_dir = Path("karabiner")
    karabiner_dir.mkdir(exist_ok=True)
    return karabiner_dir / "karabiner.json"


def modify_existing_karabiner(
    dry_run: bool = False,
    verbose: bool = False,
    override: bool = False,
) -> None:
    """Safely merge or override PoweredX rules in karabiner/karabiner.json."""
    path = get_karabiner_path()
    config = json.loads(path.read_text()) if path.exists() else {"profiles": []}
    profiles = config.get("profiles", [])
    ensure_default_profile(profiles)

    poweredx_profile = next(
        (p for p in profiles if p.get("name") == "PoweredX"), None
    )
    if poweredx_profile is None:
        poweredx_profile = {
            "name": "PoweredX",
            "complex_modifications": {"rules": []},
            "selected": True,
        }
        profiles.append(poweredx_profile)

    existing_rules = poweredx_profile.get("complex_modifications", {}).get("rules", [])
    new_rules = generate_rules()

    if override:
        if verbose:
            print("[Verbose] Override mode active. Replacing all PoweredX rules.")
        modified_rules = [r["description"] for r in new_rules]
        poweredx_profile["complex_modifications"]["rules"] = new_rules
    else:
        preserved = [
            r for r in existing_rules if MARKER not in r.get("description", "")
        ]
        replaced = [
            r for r in existing_rules if MARKER in r.get("description", "")
        ]
        merged_rules = preserved + new_rules

        if verbose:
            print(f"[Verbose] Found {len(existing_rules)} existing rules.")
            print(f"[Verbose] Replaced {len(replaced)} PoweredX rule(s).")
            print(f"[Verbose] Preserved {len(preserved)} other rule(s).")

        modified_rules = [r["description"] for r in new_rules]
        poweredx_profile["complex_modifications"]["rules"] = merged_rules

    poweredx_profile["selected"] = True
    config["profiles"] = profiles

    if dry_run:
        print("\n--- Dry Run Output ---")
        preview = {
            "config_path": str(path),
            "profile_name": poweredx_profile["name"],
            "override": override,
            "rules_modified": modified_rules,
            "total_rules_after_merge": len(
                poweredx_profile["complex_modifications"]["rules"]
            ),
        }
        print(json.dumps(preview, indent=2))
        print("--- End of Dry Run ---\n")
        return

    path.write_text(json.dumps(config, indent=4))
    print(
        f"✅ {'Overridden' if override else 'Merged'} {MARKER} rules into '{path}' safely."
    )
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
    args = parser.parse_args()

    modify_existing_karabiner(
        dry_run=args.dry_run,
        verbose=args.verbose,
        override=args.override,
    )


if __name__ == "__main__":
    main()
