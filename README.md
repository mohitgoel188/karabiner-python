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
│       ├── __init__.py       # generate_rules() — assembles everything, exports MARKER
│       ├── sublayers.py      # Sublayer key mappings (b, o, w, s, v, c, r)
│       ├── hyper.py          # Hyper base key + double-shift caps lock
│       └── pycharm.py        # PyCharm-specific key swaps
│
├── viewers/
│   ├── show_config.py        # Rich table viewer
│   └── show_config_html.py   # Interactive HTML viewer
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
- Merge your PoweredX profile safely
- Preserve community-imported rules
- Create a blank `Default` profile if missing

### Optional Flags

| Flag | Description |
|------|--------------|
| `--dry-run` | Preview changes without writing to disk |
| `--verbose` | Show detailed information about rule merges |
| `--override` | Completely replace PoweredX rules |

Example:
```bash
python build.py --dry-run --verbose
```

---

## Viewing the Configuration

**[Live Interactive Viewer](https://mohitgoel188.github.io/karabiner-python/viewers/config_viewer.html)** — visual keyboard layout with practice mode, search, and layer navigation.

Or use the CLI viewers:

```bash
# Rich table viewer (all layers)
python -m viewers.show_config

# Single layer
python -m viewers.show_config -l o

# Regenerate interactive HTML viewer
python -m viewers.show_config_html
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

| Profile | Description |
|----------|--------------|
| **Default** | Always blank fallback profile |
| **PoweredX** | Active Hyper-layer automation profile |

---

## Utilities Overview

| Helper | Purpose |
|---------|----------|
| `app("Slack")` | Open Slack app |
| `open_url("https://example.com")` | Open a URL |
| `window("left-half")` | Trigger Rectangle window action |
| `raycast("ext/path", "command")` | Trigger Raycast command |
| `swap_cmd_ctrl("d", MARKER)` | Swap Cmd+D and Ctrl+D globally |

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
