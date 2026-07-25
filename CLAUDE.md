# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

Python-based Karabiner-Elements configuration builder. Generates `karabiner/karabiner.json` from Python rule definitions. Inspired by [mxstbr/karabiner](https://github.com/mxstbr/karabiner) (TypeScript), rewritten in Python with added merge safety and visualization.

## Commands

```bash
# Build/update karabiner.json (writes to karabiner/karabiner.json)
python build.py

# Build flags
python build.py --dry-run          # Preview without writing
python build.py --verbose          # Show merge details
python build.py --override         # Replace all rules in EVERY profile (vs merge)

# Profile selection (all profiles are always rebuilt; these pick the selected one)
python build.py                    # selects MacX (the default)
python build.py --linx             # selects LinX
python build.py --poweredx         # selects PoweredX
python build.py --profile LinX     # equivalent long form

# View generated config (requires rich)
python -m viewers.show_config              # All layers, MacX by default
python -m viewers.show_config -l o         # Single layer
python -m viewers.show_config -p LinX      # A different profile
python -m viewers.show_config_html         # Interactive HTML viewer

# Inspect / reconcile the live config against what the generator produces
python tools/kbsync.py backup
python tools/kbsync.py compare /tmp/karabiner.snapshot.json

# Lint
ruff check .
```

## Dependencies

- Python >=3.14, managed with `uv` (see `pyproject.toml` and `uv.lock`)
- Runtime dependency: `rich` (for `viewers/show_config.py` visualization only)
- No test framework configured

## Architecture

The build pipeline flows: **src/rules/** -> **build.py** -> `karabiner/karabiner.json`

- **build.py** - CLI entry point. Reads existing `karabiner.json`, then builds/refreshes every profile in `PROFILE_NAMES` via `ensure_profile()` and selects one (default `MacX`). Merge mode (default) keeps non-MARKER rules intact; override mode replaces everything. Only `complex_modifications.rules` is ever rewritten, so hand-made profile settings (PoweredX's `simple_modifications`, LinX's `devices`) survive rebuilds; `devices`/`virtual_hid_keyboard` are seeded on first creation only. A `karabiner_cli` lint gate validates the LinX and MacX layers before writing.
- **src/rules/__init__.py** - `generate_rules(profile)` dispatches through `_PROFILE_RULES` to one of `_poweredx_rules()` / `_linx_rules()` / `_macx_rules()`, all sharing `_genx_core()`. Exports `MARKER` (`"GenX"`), `PROFILE_NAMES`, `DEFAULT_PROFILE`. **Rule order within each profile is semantically significant** — later rules see earlier rules' output.
- **src/rules/sublayers.py** - Defines all hyper sublayer key mappings (b, o, w, s, v, c, r, spacebar).
- **src/rules/hyper.py** - Hyper base key rule and double-shift caps lock rule.
- **src/rules/pycharm.py** - PyCharm-specific key swaps (Cmd/Ctrl swap, Shift+Enter/Option+Enter swap). PoweredX only.
- **src/rules/linx.py** - Linux muscle-memory layer (LinX): Left ⌘↔⌃ swap plus volume/brightness, workspace, iTerm and Firefox chord rules. MacX reuses three of these builders.
- **src/rules/macx.py** - Native-macOS layer (MacX): `build_globe_control_swap_rule()` swaps globe/fn ↔ Left Control scoped to the built-in keyboard, plus `build_macx_layer()` for the lint gate.
- **tools/kbsync.py** - Snapshot / compare / verify the live config against the generated one, for folding manual UI edits back into source.
- **src/helpers.py** - Helper functions (`app()`, `open_url()`, `window()`, `swap_cmd_ctrl()`, `tuple_dict()`) that return Karabiner action dicts. All shell commands are quoted with `shlex.quote()`.
- **src/raycast.py** - Single helper `raycast()` that builds Raycast deep-link shell commands.
- **src/engine.py** - `create_hyper_sublayers()` expands sublayer mappings into Karabiner manipulator rules with proper variable conditions for mutual exclusion.
- **src/models.py** - `Rule` dataclass for structuring Karabiner JSON.
- **viewers/show_config.py** - Rich table viewer. Parses sublayer structure from rule descriptions.
- **viewers/show_config_html.py** - Interactive HTML viewer with keyboard layout visualization.

## Key Concepts

- **Hyper Key**: Caps Lock sets a `hyper` **variable** (not real modifiers — the `⌃⌥⇧⌘` in its description is cosmetic). Pressing Caps Lock alone sends Escape. Because it is variable-driven, no modifier remapping in any profile can disturb the hyper layer.
- **Sublayers**: Each letter key (b, o, w, s, v, c, r, spacebar) under Hyper activates a "sublayer" via Karabiner variables. Sublayers are mutually exclusive (enforced by `create_hyper_sublayers()`).
- **MARKER pattern**: All generated rules include `"GenX"` in their description. This lets `build.py` merge mode replace only generated rules while preserving manually-added or community rules.
- **Descriptions are de-facto stable IDs**: `carry_over_enabled()` preserves each rule's UI on/off toggle by matching on `description`, so **renaming a description silently resets that toggle**. MacX reuses LinX builders verbatim, which is why MacX rules carry `GenX LinX:` descriptions — renaming them would reset LinX's toggles.
- **Profiles**: `Default` (blank), `PoweredX` (original GenX), `LinX` (Linux muscle-memory, Left ⌘↔⌃ swap), `MacX` (native macOS modifiers + built-in-keyboard globe↔Ctrl swap; **the default selection**).
- **Device scoping**: Karabiner reports the built-in keyboard with **no vendor_id/product_id** (`karabiner_cli --list-connected-devices` shows `{"is_keyboard": true}`). So targeting it requires a `device_if` condition on `is_built_in_keyboard` in a *complex* modification; a profile-level `devices` block cannot express it. Note `simple_modifications` and `fn_function_keys` run **before** complex modifications in Karabiner's pipeline.

## Output

The `karabiner/` directory is gitignored. The generated `karabiner.json` is symlinked to `~/.config/karabiner/` for Karabiner-Elements to pick up.
