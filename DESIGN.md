# Design

A calm, dark tool UI. The music data carries the colour; the chrome around it stays quiet.

## Tokens (`static/style.css`, `:root`)

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0b0b12` | page background |
| `--surface` / `--surface-2` | `#12121b` / `#1a1a28` | cards, dialog |
| `--border` / `--border-strong` | `#2c2c44` / `#66668a` | dividers / control borders (3:1 or more) |
| `--text` / `--text-muted` | `#e6e6ee` / `#a3a3b8` | body text / hints, footer (7.5:1) |
| `--accent` | `#ff6b81` | brand, links, focus ring (6.8:1) |
| `--accent-fill` | `#cf3150` | primary button fill, white text 5.0:1 |
| `--ok` `--info` `--warn` `--danger` `--violet` | | status badges and note roles, always with a text label |

Radii: 6 px controls, 10 px messages, 14 px cards. Font: the system UI stack, no web fonts.

## Rules

- `color-scheme: dark` on `:root` and in the meta tag, so form controls and scrollbars match.
- Every control has a visible label; placeholders only show an example value.
- Focus: one `:focus-visible` outline in `--accent`, never `outline: none`.
- Text contrast at least 4.5:1, control borders and focus ring at least 3:1.
- Hover scale effects only under `prefers-reduced-motion: no-preference`; spinners slow down
  under `reduce`.
- Destructive actions confirm in a native `<dialog>` with the safe action focused.
- No inline event handlers and no script without the per-request CSP nonce.
- Check at 390 px and at desktop width: no horizontal scroll.
