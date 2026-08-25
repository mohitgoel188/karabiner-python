# PoweredX Karabiner Config (Python Edition)

A fully modular, Python-based **Karabiner-Elements configuration builder** that mirrors and extends the functionality of the [original](github.com/mxstbr/karabiner/) TypeScript `rules.ts` setup — with added flexibility, safety, and readability.

---

## Features

- Generate **complex Karabiner rules** using Python
- Define **Hyper key layers** programmatically (`b`, `o`, `w`, `s`, etc.)
- Non-destructive updates to existing `karabiner.json`
- Detect duplicate layer keys automatically
- Pretty print configuration using `rich`
- Modular design — easy to customize, extend, or integrate
- Stores configuration under `karabiner/karabiner.json`
- Compatible with **Ruff** (PEP 8 + clean imports)

---

## Project Structure

```
karabiner-python/
├── build.py                  # CLI entry point — merges/overrides karabiner.json
│
├── src/
│   ├── models.py             # Rule dataclass
│   ├── helpers.py            # app(), open_url(), window(), swap_cmd_ctrl(), tuple_dict()
│   ├── raycast.py            # raycast() deep-link helper
│   ├── engine.py             # create_hyper_sublayers() — core sublayer transform
│   └── rules/
│       ├── __init__.py       # generate_rules(profile) — per-profile assembly, MARKER
│       ├── sublayers.py      # Sublayer key mappings (b, o, w, s, v, c, r)
│       ├── hyper.py          # Hyper base key + double-shift caps lock
│       ├── pycharm.py        # PyCharm-specific key swaps (PoweredX only)
│       ├── linx.py           # Linux muscle-memory layer (LinX)
│       └── macx.py           # Native-macOS layer + built-in globe↔Ctrl swap (MacX)
│
├── viewers/
│   ├── show_config.py        # Rich table viewer (-p/--profile)
│   └── show_config_html.py   # Interactive HTML viewer (-p/--profile)
│
├── tools/
│   └── kbsync.py             # Snapshot / compare / verify live config vs generated
│
└── karabiner/
    └── karabiner.json        # Generated output (auto-created, gitignored)
```

---

## Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/karabiner-python.git
   cd karabiner-python
   ```

2. Delete the default `~/.config/karabiner` folder
3. Create a symlink with `ln -s [PATH_TO_REPO]/karabiner ~/.config` (where `[PATH_TO_REPO]` is your local path to where you cloned the repository)
4. [Restart karabiner_console_user_server](https://karabiner-elements.pqrs.org/docs/manual/misc/configuration-file-path/) with `` launchctl kickstart -k gui/`id -u`/org.pqrs.karabiner.karabiner_console_user_server ``

---

## Building the Configuration

To generate or update your Karabiner config:

```bash
python build.py
```

This will:

- Ensure the `karabiner/` directory exists
- Create or update `karabiner/karabiner.json`
- Build/refresh **all three** profiles (PoweredX, LinX, MacX) safely
- Select **MacX** (the default — see [Profiles](#profiles))
- Preserve community-imported rules
- Create a blank `Default` profile if missing

Every profile is rebuilt on every run so they never drift apart. The flags below only
change **which one is selected**; no profile is ever deleted.

### Optional Flags

| Flag | Description |
|------|--------------|
| `--dry-run` | Preview changes without writing to disk |
| `--verbose` | Show detailed information about rule merges |
| `--override` | Replace all rules in **every** profile instead of merging. Drops any non-`GenX` rules you added by hand or imported from the community. |
| `--profile {PoweredX,LinX,MacX}` | Profile to select after building (default: `MacX`) |
| `--macx` | Shorthand for `--profile MacX` — the default |
| `--linx` | Shorthand for `--profile LinX` |
| `--poweredx` | Shorthand for `--profile PoweredX` |

Example:
```bash
python build.py --dry-run --verbose
python build.py --linx              # build everything, switch to LinX
```

---

## Viewing the Configuration

**[Live Interactive Viewer](https://mohitgoel188.github.io/karabiner-python/viewers/config_viewer.html)** — visual keyboard layout with practice mode, search, and layer navigation.

Or use the CLI viewers:

```bash
# Rich table viewer (all layers, MacX by default)
python -m viewers.show_config

# Single layer
python -m viewers.show_config -l o

# A different profile
python -m viewers.show_config -p LinX

# Regenerate interactive HTML viewer
python -m viewers.show_config_html
python -m viewers.show_config_html -p PoweredX
```

---

## Customization Guide

You can easily add or modify key layers in `src/rules/sublayers.py`.

Example:

```python
# Add a new "x" layer for quick tools
"x": tuple_dict([
    ("c", app("Calculator")),
    ("n", app("Notes")),
    ("p", app("Preview")),
])
```

Then rebuild:
```bash
python build.py --override
```

---

## Extending Rules

- **To add new app/URL/window actions:**
  Use the helpers in `src/helpers.py`

- **To add new Raycast actions:**
  Use the `raycast()` helper from `src/raycast.py`

- **To add app-specific key swaps:**
  Create a new file in `src/rules/` (see `pycharm.py` as an example)

Example:
```python
raycast("raycast/system", "toggle-dark-mode", background=True)
```

---

## Linting and Style

This project follows **Ruff's default rules**:

- PEP8 compliant
- No unused imports
- Line length <= 88
- Consistent double quotes

You can check formatting with:

```bash
ruff check .
```

---

## Output Location

All configuration files are stored in:
```
karabiner/karabiner.json
```

To use this with **Karabiner-Elements**, symlink or copy the file to:

```
~/.config/karabiner/karabiner.json
```

---

## Profiles

All three generated profiles are rebuilt on every run; only the selection changes.

| Profile | Description |
|----------|--------------|
| **Default** | Always blank fallback profile |
| **PoweredX** | Hyper-layer automation profile (GenX) |
| **LinX** | GenX + a Linux muscle-memory layer (Left ⌘↔⌃ swap) |
| **MacX** | GenX + native macOS modifiers + built-in-keyboard globe↔Ctrl swap — **selected by default** |

All three share the same Hyper Key core: Caps Lock → Hyper (tap = Escape), the `b`/`o`/`w`/`s`/`v`/`c`/`r`/`spacebar`
sublayers, and double-tap Right-Shift → Caps Lock. That core is driven by a `hyper`
*variable* off `caps_lock` rather than by real modifiers, so no amount of modifier remapping
in a profile can disturb it.

### `--macx` (native macOS, the default)

**MacX** is for running a Mac as a Mac: **⌘ stays ⌘ and ⌃ stays ⌃**, with no swap anywhere.
It exists to reconcile two keyboards whose bottom rows disagree.

| | Bottom-left row |
|---|---|
| MacBook built-in | `globe` `⌃` `⌥` `⌘` |
| Optimus 4-in-1 (external) | `⌃` `Fn` `⌥` `⌘` |

The Optimus has `left_control` in the corner where a Mac has globe, and its `Fn` is
firmware-only — Karabiner never receives an event from it. MacX therefore swaps
**globe ↔ Left Control on the built-in keyboard only**, so the MacBook's corner key becomes
`left_control` too: one muscle memory for both boards, and the Optimus keeps a real Control key.

Scoping uses a `device_if` condition on `is_built_in_keyboard` rather than
`vendor_id`/`product_id`. That is not just for portability across Macs — `karabiner_cli
--list-connected-devices` reports the internal keyboard as `{"is_keyboard": true}` with **no
vendor or product id at all**, so an id-based match is impossible. It is also why the remap is
a complex modification and not a profile-level `devices` block, which can only key on concrete
identifiers. MacX carries no `simple_modifications`.

MacX keeps `Cmd+Ctrl+Arrows` → volume/brightness, `Ctrl+Alt+Arrows` → space switching,
PC-style Home/End, and the ⌃⌘T iTerm launcher. On the built-in keyboard the corner key is now
Control, so volume becomes **⌘ + corner + Arrow** — the identical gesture to the Optimus.

It **omits** everything that only made sense alongside a Cmd↔Ctrl swap: LinX's swap itself,
LinX's iTerm `Ctrl+T`/`Ctrl+V` and Firefox `Ctrl+Shift+I`/`C` compensations, the PyCharm
cmd/ctrl and Shift+Enter↔Opt+Enter swaps, and the global ⌘D↔⌃D swap. PyCharm's stock macOS
keymap is already correct with no swap in play.

#### Known limitations

Because the built-in Control key now emits a Karabiner-posted `keyboard_fn`, behaviours macOS
ties to the *real* internal keyboard may not follow it: the globe input-source switcher and
emoji picker, `fn+Delete` forward-delete, `fn+Arrows` for PageUp/Down, hold-fn to reveal the
F-row, and double-tap-fn dictation (a hardware gesture that will not survive at all).
Separately, Karabiner's `fn_function_keys` stage runs *before* complex modifications, so
`corner+F1..F12` may fire a media action **and** post a stray Control. Both are fixable with
targeted manipulators once you know which ones you actually miss.

### `--linx` (Linux muscle-memory layer)

`python build.py --linx` selects the **LinX** profile.
LinX keeps every GenX feature (Hyper Key + sublayers, double-tap Right-Shift → Caps Lock,
iTerm ⌘⌃T) and adds a Linux-style layer so the corner key (physical Left Ctrl) drives macOS
shortcuts like Linux Ctrl:

- **Swap Left ⌘ ↔ Left ⌃** everywhere except standalone terminals (terminals keep real Ctrl
  for SIGINT). PyCharm is intentionally included in the swap.
- **Volume/Brightness** via `Cmd+Ctrl+Arrows` (mirrors Linux `Ctrl+Super+Arrows`).
- **PC-style Home/End** → line start/end (except terminals and PyCharm).

To avoid double-remapping, LinX **omits** the conflicting GenX pieces — the PyCharm cmd/ctrl
swap and Shift+Enter↔Opt+Enter (handled by the PyCharm "LinX (Mac)" keymap), the global
⌘D↔⌃D swap, and the PoweredX `fn→cmd→ctrl→fn` `simple_modifications` rotation. LinX carries no
`simple_modifications`.

Running plain `python build.py` (no flag) selects **MacX** and leaves the others present but
deselected — switch between them anytime from the Karabiner-Elements menu bar, or with
`karabiner_cli --select-profile <name>`.

---

## Utilities Overview

| Helper | Purpose |
|---------|----------|
| `app("Slack")` | Open Slack app |
| `open_url("https://example.com")` | Open a URL |
| `window("left-half")` | Trigger Rectangle window action |
| `raycast("ext/path", "command")` | Trigger Raycast command |
| `swap_cmd_ctrl("d", MARKER)` | Swap Cmd+D and Ctrl+D globally (PoweredX only) |

---

## Developer Notes

- Each sublayer is defined as a Python dictionary of key mappings.
- Duplicate keys within a layer will trigger a console warning.
- Merging logic is designed to preserve community rules automatically.
- All layers are prefixed with a global **Hyper Key** (`Ctrl+Opt+Shift+Cmd`).
- All shell commands are quoted with `shlex.quote()` for safety.

---

## Example Workflow

1. Modify `src/rules/sublayers.py` — add or tweak mappings
2. Run build:
   ```bash
   python build.py --override
   ```
3. Preview config:
   ```bash
   python -m viewers.show_config
   ```
4. Karabiner picks up changes via the symlink automatically.

---

## License

MIT License (c) 2025
You're free to fork, modify, and share — just keep it open.

---

## Acknowledgments

Special thanks to:
- Jesse Skelton's [Video Tutorials](https://youtu.be/uaJSjgVEhMQ?si=2olcwLeZQ3q7AtJQ)
- MXSTBR's [Karabiner Repo](https://github.com/mxstbr/karabiner)

---

## Contributing

Contributions are welcome!

If you:
- Add a new helper (e.g., Alfred, VSCode)
- Optimize rule generation
- Enhance visualization

Please open a PR with your changes.
