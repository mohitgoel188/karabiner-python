# FILE: src/rules/macx.py
"""Native-macOS layer for the MacX profile.

MacX keeps Apple's own modifier semantics: there is no Cmd<->Ctrl swap anywhere, so
⌘C/⌘V and Ctrl+C-as-SIGINT behave exactly as macOS intends. It reuses the
profile-neutral conveniences from the LinX layer (volume/brightness chords, workspace
switching, PC-style Home/End) and adds one hardware-normalising rule: on the BUILT-IN
keyboard only, the globe/fn key and Left Control trade places.

Why: the external "Optimus 4-in-1" keyboard has left_control in the bottom-left corner
where a MacBook has globe/fn, and its own Fn is firmware-only (Karabiner never sees an
event from it). Scoping the swap to the built-in keyboard makes the MacBook's corner key
left_control too — one muscle memory for both boards — while leaving the Optimus
untouched so it keeps a real Control key.
"""

from src.rules.linx import (
    build_home_end_rule,
    build_volume_brightness_rule,
    build_workspace_switch_rule,
)

# The MacBook's globe/fn key arrives on the Apple Vendor Top Case usage page rather than
# as a normal key_code. Karabiner also accepts the legacy `key_code: "fn"` spelling,
# which some keyboards report instead, so both are handled below.
_GLOBE_KEY: dict[str, str] = {"apple_vendor_top_case_key_code": "keyboard_fn"}


def _built_in_keyboard_if() -> list[dict]:
    """device_if condition matching only the MacBook's internal keyboard.

    Deliberately identifier-based (``is_built_in_keyboard``) rather than
    vendor_id/product_id: ``karabiner_cli --list-connected-devices`` reports the internal
    keyboard as ``{"is_keyboard": true}`` with no vendor or product id at all, so an
    id-based match is impossible, not merely unportable. It is also why this has to be a
    complex-modification condition and not a profile-level ``devices`` block, which can
    only be keyed on concrete identifiers.
    """
    return [{"type": "device_if", "identifiers": [{"is_built_in_keyboard": True}]}]


def build_globe_control_swap_rule(marker: str) -> dict:
    """Swap globe/fn <-> Left Control, on the built-in keyboard only.

    Keep this FIRST in the MacX rule list: the chord rules below it match left_control
    and should see the rewritten corner key. No loop risk — a manipulator's ``to`` events
    are posted downstream and never re-fed into the manipulator list, so globe->control
    cannot be re-matched by the control->globe manipulator (the same construct
    build_swap_cmd_ctrl_rule already uses).
    """
    built_in = _built_in_keyboard_if()
    return {
        "description": (
            f"{marker} MacX: Swap globe/fn <-> Left Control on the BUILT-IN keyboard "
            "only (external keyboards keep a real Control key). Keep this rule first."
        ),
        "manipulators": [
            {
                "type": "basic",
                "from": {**_GLOBE_KEY, "modifiers": {"optional": ["any"]}},
                "to": [{"key_code": "left_control"}],
                "conditions": built_in,
            },
            {
                # Alias for built-in boards that report the plain `fn` key_code instead
                # of the top-case usage above. Harmless when dead: a given event matches
                # only the first manipulator that accepts it.
                "type": "basic",
                "from": {"key_code": "fn", "modifiers": {"optional": ["any"]}},
                "to": [{"key_code": "left_control"}],
                "conditions": built_in,
            },
            {
                "type": "basic",
                "from": {
                    "key_code": "left_control",
                    "modifiers": {"optional": ["any"]},
                },
                "to": [dict(_GLOBE_KEY)],
                "conditions": built_in,
            },
        ],
    }


def build_macx_layer(marker: str) -> list[dict]:
    """Build the MacX layer rules in Karabiner evaluation order.

    The lint-safe subset, mirroring build_linx_layer: the hyper sublayers use a lenient
    shape the strict linter rejects, and the ⌘⌥T iTerm launcher is assembled in
    generate_rules(), so neither appears here. The globe/Control swap leads so the chord
    rules below it see the rewritten left_control.
    """
    return [
        build_globe_control_swap_rule(marker),
        build_volume_brightness_rule(marker),
        build_workspace_switch_rule(marker),
        build_home_end_rule(marker),
    ]
