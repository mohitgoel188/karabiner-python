# 🧠 PoweredX Karabiner Config (Python Edition)

A fully modular, Python-based **Karabiner-Elements configuration builder** that mirrors and extends the functionality of the [original](github.com/mxstbr/karabiner/) TypeScript `rules.ts` setup — with added flexibility, safety, and readability.

---

## 🚀 Features

- ✅ Generate **complex Karabiner rules** using Python
- 🧩 Define **Hyper key layers** programmatically (`b`, `o`, `w`, `s`, etc.)
- ⚙️ Non-destructive updates to existing `karabiner.json`
- 🧠 Detect duplicate layer keys automatically
- 💡 Pretty print configuration using `rich`
- 🧱 Modular design — easy to customize, extend, or integrate
- 💾 Stores configuration under `karabiner/karabiner.json`
- 🪶 Compatible with **Ruff** (PEP 8 + clean imports)

---

## 🧰 Project Structure

```
karabiner-python/
│
├── build.py             # Build and merge karabiner.json profiles
├── rules.py             # Defines all Hyper layers and key mappings
├── models.py            # Dataclasses defining rule structures
├── utils.py             # App/window/shell helper utilities
├── raycast_utils.py     # Raycast-specific helpers
├── show_config.py       # Pretty display of generated config
└── karabiner/
    └── karabiner.json   # Generated output (auto-created)
```

---

## ⚙️ Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/karabiner-python.git
   cd karabiner-python
   ```

2. Delete the default `~/.config/karabiner` folder
3. Create a symlink with `ln -s [PATH_TO_REPO]/karabiner ~/.config` (where `[PATH_TO_REPO]` is your local path to where you cloned the repository)
4. [Restart karabiner_console_user_server](https://karabiner-elements.pqrs.org/docs/manual/misc/configuration-file-path/) with `` launchctl kickstart -k gui/`id -u`/org.pqrs.karabiner.karabiner_console_user_server ``

---

## 🏗️ Building the Configuration

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

## 🔍 Viewing the Configuration

Use the built-in visualizer to display your config in a clean, structured way:

```bash
python show_config.py
```

You can also filter by **specific layers**:

```bash
python show_config.py -l o
```

Example output:
```
Layer: O (Open)
────────────────────────────
Shortcut | Function                     | Action
o+g      | Open Google Chrome           | 🖥️ open -a 'Google Chrome.app'
o+s      | Open Slack                   | 🖥️ open -a 'Slack.app'
...
```

---

## 🧩 Customization Guide

You can easily add or modify key layers in `rules.py`.

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

## 🧱 Extending Rules

- **To add new window actions:**  
  Update the `window()` helper in `utils.py`
  
- **To add new Raycast actions:**  
  Use the `raycast()` helper from `raycast_utils.py`

Example:
```python
raycast("raycast/system", "toggle-dark-mode", background=True)
```

---

## 🧼 Linting and Style

This project follows **Ruff’s default rules**:

- PEP8 compliant
- No unused imports
- Line length ≤ 88
- Consistent double quotes

You can check formatting with:

```bash
ruff check .
```

---

## 💾 Output Location

All configuration files are stored in:
```
karabiner/karabiner.json
```

To use this with **Karabiner-Elements**, copy the file to:

```
~/.config/karabiner/karabiner.json
```

---

## 🧠 Example Profiles

| Profile | Description |
|----------|--------------|
| **Default** | Always blank fallback profile |
| **PoweredX** | Active Hyper-layer automation profile |

---

## 🧰 Utilities Overview

| Helper | Purpose |
|---------|----------|
| `app("Slack")` | Open Slack app |
| `open_url("https://example.com")` | Open a URL |
| `window("left-half")` | Trigger Rectangle window action |
| `raycast("ext/path", "command")` | Trigger Raycast command |
| `shell("echo hi")` | Run custom shell command |

---

## 💡 Developer Notes

- Each sublayer is defined as a Python dictionary of key mappings.
- Duplicate keys within a layer will trigger a console warning.
- Merging logic is designed to preserve community rules automatically.
- All layers are prefixed with a global **Hyper Key** (`⌃⌥⇧⌘`).

---

## 🪄 Example Workflow

1. Modify `rules.py` → add or tweak mappings  
2. Run build:
   ```bash
   python build.py --override
   ```
3. Preview config:
   ```bash
   python show_config.py
   ```
4. Copy `karabiner/karabiner.json` to your Karabiner config directory.

---

## 📜 License

MIT License © 2025  
You’re free to fork, modify, and share — just keep it open.

---

## ❤️ Contributing

Contributions are welcome!

If you:
- Add a new helper (e.g., Alfred, VSCode)
- Optimize rule generation
- Enhance visualization

Please open a PR with your changes.

---

**Built with Python 🐍, Tea ☕, and Karabiner ❤️**
