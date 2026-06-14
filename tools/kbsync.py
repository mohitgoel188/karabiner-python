#!/usr/bin/env python3
"""kbsync — detect and verify manual edits to the live Karabiner config.

The live Karabiner-Elements config (``~/.config/karabiner/karabiner.json``, a
symlink into this repo's ``karabiner/`` dir) is *generated* by ``build.py``. Any
tweak a user makes in the Karabiner UI lives only in that generated file, so the
next ``build.py`` run silently clobbers it. This tool is the mechanical half of
the "fold manual edits back into source" workflow:

  1. ``backup``  — snapshot the live config BEFORE rebuilding (the rebuild
                   overwrites it; without a snapshot the edits are gone).
  2. ``compare`` — after rebuilding, diff snapshot vs regenerated config and
                   report field-level changes, separating real behavior changes
                   from cosmetic description-only renames.
  3. ``verify``  — after editing source and rebuilding again, assert the
                   regenerated config reproduces the snapshot's behavior.

Stdlib only, so it runs under the repo venv or bare python. The interpretation
step (mapping a reported change back to the ``src/rules/*.py`` builder that emits
it) is left to the caller — see the karabiner-config-sync skill.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

# Behavioral identity ignores these rule-level keys when comparing rule bodies.
# "description" is a human label — a rule can be renamed in the UI without any
# behavior change, so description-only diffs are reported as cosmetic, not real.
_COSMETIC_RULE_KEYS = {"description"}


def _default_live_path() -> Path:
    """Resolve the live config, preferring the symlinked user config."""
    user_config = Path.home() / ".config" / "karabiner" / "karabiner.json"
    if user_config.exists():
        return user_config
    return Path("karabiner") / "karabiner.json"


def _load(path: Path) -> dict[str, Any]:
    with path.open() as handle:
        return json.load(handle)


def _profiles_by_name(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        p.get("name", f"<unnamed-{i}>"): p
        for i, p in enumerate(config.get("profiles", []))
    }


def _rule_body(rule: dict[str, Any]) -> str:
    """Canonical JSON of a rule excluding cosmetic keys (for behavior compare)."""
    body = {k: v for k, v in rule.items() if k not in _COSMETIC_RULE_KEYS}
    return json.dumps(body, sort_keys=True)


def _diff_paths(old: Any, new: Any, prefix: str = "") -> list[tuple[str, Any, Any]]:
    """Recursively collect (json_path, old_value, new_value) leaf differences."""
    changes: list[tuple[str, Any, Any]] = []
    if isinstance(old, dict) and isinstance(new, dict):
        for key in sorted(set(old) | set(new)):
            changes.extend(
                _diff_paths(
                    old.get(key, _MISSING),
                    new.get(key, _MISSING),
                    f"{prefix}.{key}" if prefix else key,
                )
            )
    elif isinstance(old, list) and isinstance(new, list):
        for idx in range(max(len(old), len(new))):
            o = old[idx] if idx < len(old) else _MISSING
            n = new[idx] if idx < len(new) else _MISSING
            changes.extend(_diff_paths(o, n, f"{prefix}[{idx}]"))
    elif old != new:
        changes.append((prefix or "(root)", old, new))
    return changes


class _Missing:
    def __repr__(self) -> str:
        return "<absent>"


_MISSING = _Missing()


def _match_rules(
    old_rules: list[dict], new_rules: list[dict]
) -> tuple[list[tuple[dict, dict]], list[dict], list[dict]]:
    """Pair rules across two configs.

    Match by description first; for leftovers of equal length, fall back to
    positional matching (the generator is order-stable, so a renamed rule keeps
    its slot). Returns (matched_pairs, only_in_old, only_in_new).
    """
    old_by_desc = {r.get("description"): r for r in old_rules}
    new_by_desc = {r.get("description"): r for r in new_rules}
    matched: list[tuple[dict, dict]] = []
    for desc, old_rule in old_by_desc.items():
        if desc in new_by_desc:
            matched.append((old_rule, new_by_desc[desc]))

    matched_old_ids = {id(o) for o, _ in matched}
    matched_new_ids = {id(n) for _, n in matched}
    leftover_old = [r for r in old_rules if id(r) not in matched_old_ids]
    leftover_new = [r for r in new_rules if id(r) not in matched_new_ids]

    # Positional fallback: same number of unmatched on both sides -> assume a
    # rename in place rather than an add+remove.
    if leftover_old and len(leftover_old) == len(leftover_new):
        matched.extend(zip(leftover_old, leftover_new))
        return matched, [], []
    return matched, leftover_old, leftover_new


def _compare_profile(name: str, old: dict[str, Any], new: dict[str, Any]) -> list[str]:
    lines: list[str] = []

    if bool(old.get("selected")) != bool(new.get("selected")):
        lines.append(f"  selected: {old.get('selected')} -> {new.get('selected')}")

    for key in (
        "simple_modifications",
        "devices",
        "fn_function_keys",
        "virtual_hid_keyboard",
    ):
        for path, o, n in _diff_paths(
            old.get(key, _MISSING), new.get(key, _MISSING), key
        ):
            lines.append(f"  {path}: {o!r} -> {n!r}")

    old_rules = old.get("complex_modifications", {}).get("rules", [])
    new_rules = new.get("complex_modifications", {}).get("rules", [])
    matched, only_old, only_new = _match_rules(old_rules, new_rules)

    for rule in only_old:
        lines.append(
            f"  RULE ONLY IN SNAPSHOT (rebuild dropped it): {rule.get('description')!r}"
        )
    for rule in only_new:
        lines.append(
            f"  RULE ONLY IN REBUILD (generator added it): {rule.get('description')!r}"
        )

    for old_rule, new_rule in matched:
        desc = old_rule.get("description") or new_rule.get("description")
        body_changed = _rule_body(old_rule) != _rule_body(new_rule)
        desc_changed = old_rule.get("description") != new_rule.get("description")
        if body_changed:
            lines.append(f"  RULE CHANGED (real/behavioral): {desc!r}")
            for path, o, n in _diff_paths(old_rule, new_rule):
                if path == "description":
                    continue
                lines.append(f"      {path}: {o!r} -> {n!r}")
        if desc_changed and not body_changed:
            lines.append(
                f"  RULE RENAMED (cosmetic only, behavior identical): "
                f"{old_rule.get('description')!r} -> {new_rule.get('description')!r}"
            )
        elif desc_changed and body_changed:
            lines.append(
                f"      (also renamed: {old_rule.get('description')!r} -> {new_rule.get('description')!r})"
            )
    return lines


def cmd_backup(args: argparse.Namespace) -> int:
    live = Path(args.live) if args.live else _default_live_path()
    if not live.exists():
        print(f"ERROR: live config not found at {live}", file=sys.stderr)
        return 2
    dest = Path(args.out) if args.out else Path("/tmp") / "karabiner.snapshot.json"
    shutil.copy2(live, dest)
    print(
        f"Snapshotted live config:\n  from {live}\n  to   {dest}  ({dest.stat().st_size} bytes)"
    )
    print(
        f"\nNext: rebuild (e.g. `.venv/bin/python build.py --linx`), then:\n  python tools/kbsync.py compare {dest} <live>"
    )
    return 0


def _resolve_pair(args: argparse.Namespace) -> tuple[Path, Path]:
    old = Path(args.snapshot)
    new = Path(args.live) if args.live else _default_live_path()
    return old, new


def cmd_compare(args: argparse.Namespace) -> int:
    old_path, new_path = _resolve_pair(args)
    old, new = _load(old_path), _load(new_path)
    old_profiles, new_profiles = _profiles_by_name(old), _profiles_by_name(new)

    print(
        f"Comparing snapshot vs current config:\n  snapshot: {old_path}\n  current : {new_path}\n"
    )
    targets = (
        [args.profile]
        if args.profile
        else sorted(set(old_profiles) | set(new_profiles))
    )

    any_change = False
    for name in targets:
        if name not in old_profiles:
            print(f"PROFILE ADDED: {name}")
            any_change = True
            continue
        if name not in new_profiles:
            print(f"PROFILE REMOVED: {name}")
            any_change = True
            continue
        lines = _compare_profile(name, old_profiles[name], new_profiles[name])
        if lines:
            any_change = True
            print(f"PROFILE {name}:")
            print("\n".join(lines))
            print()

    if not any_change:
        print("No differences. The current config already matches the snapshot.")
    else:
        print(
            "Interpret each 'RULE CHANGED (real/behavioral)' above: locate the "
            "src/rules/*.py builder that emits that rule and apply the change there.\n"
            "'RULE RENAMED (cosmetic only)' means behavior already matches — only "
            "the label differs; folding it in also resets that rule's enabled "
            "toggle (carry_over_enabled matches by description)."
        )
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    old_path, new_path = _resolve_pair(args)
    old, new = _load(old_path), _load(new_path)
    old_profiles, new_profiles = _profiles_by_name(old), _profiles_by_name(new)
    targets = (
        [args.profile]
        if args.profile
        else sorted(set(old_profiles) | set(new_profiles))
    )

    residual: list[str] = []
    for name in targets:
        if name not in old_profiles or name not in new_profiles:
            residual.append(f"PROFILE PRESENCE MISMATCH: {name}")
            continue
        lines = _compare_profile(name, old_profiles[name], new_profiles[name])
        if args.ignore_description:
            lines = [
                line for line in lines if "RULE RENAMED (cosmetic only" not in line
            ]
        if lines:
            residual.append(f"PROFILE {name}:\n" + "\n".join(lines))

    if residual:
        print("NOT IN SYNC — residual differences:\n")
        print("\n\n".join(residual))
        return 1
    scope = " (ignoring cosmetic renames)" if args.ignore_description else ""
    print(f"IN SYNC — regenerated config reproduces the snapshot's behavior{scope}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_backup = sub.add_parser(
        "backup", help="Snapshot the live config BEFORE rebuilding."
    )
    p_backup.add_argument(
        "--live",
        help="Path to live config (default: ~/.config/karabiner/karabiner.json).",
    )
    p_backup.add_argument(
        "--out", help="Snapshot destination (default: /tmp/karabiner.snapshot.json)."
    )
    p_backup.set_defaults(func=cmd_backup)

    p_compare = sub.add_parser(
        "compare", help="Field-level diff: snapshot vs current config."
    )
    p_compare.add_argument(
        "snapshot", help="Path to the snapshot taken before rebuild."
    )
    p_compare.add_argument(
        "--live", help="Current config (default: ~/.config/karabiner/karabiner.json)."
    )
    p_compare.add_argument("--profile", help="Limit to one profile (e.g. LinX).")
    p_compare.set_defaults(func=cmd_compare)

    p_verify = sub.add_parser(
        "verify", help="Assert current config reproduces the snapshot's behavior."
    )
    p_verify.add_argument("snapshot", help="Path to the snapshot taken before rebuild.")
    p_verify.add_argument(
        "--live", help="Current config (default: ~/.config/karabiner/karabiner.json)."
    )
    p_verify.add_argument("--profile", help="Limit to one profile (e.g. LinX).")
    p_verify.add_argument(
        "--ignore-description",
        action="store_true",
        help="Treat cosmetic rule renames as in-sync (behavior-only check).",
    )
    p_verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
