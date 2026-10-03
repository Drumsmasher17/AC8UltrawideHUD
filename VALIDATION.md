# Validation

## Verified

- On 2026-10-03, the user confirmed the portrait-mask fix resolves target boxes
  disappearing in clear sky beside an active portrait in third-person view.
- Portrait mocks cover mask/drawing agreement at 21:9 and 32:9, restoration at
  16:9, late construction, unknown layouts, failed-write rollback and stable checks.

- User confirmed the automatic radar correction worked in-game after installation.
- User confirmed the radar background correction and its reversal. Each became
  visible after collapsing and expanding the radar, rather than immediately.
- Radar mocks cover 21:9/32:9 compensation, return to 16:9, late construction,
  and no repeated child searches or writes during stable gameplay.
- User visually confirmed the MainCanvas adjustment in multiple gameplay missions.
- A previous installed automatic build reached gameplay and applied the layout.
- Review of its log exposed repeated `already has the required width` messages.
  Native-address comparison replaces the Lua-wrapper comparison implicated by
  that behaviour. Routine application/status messages have also been removed.
- Mock regression: 1,000 checks with fresh unequal Lua wrappers around the same
  native address produce no additional scans, layout validation, writes or logs.
- Tests cover a new slot while the old slot remains valid; changing resolution;
  returning to 16:9; zero viewport; non-gameplay HUD; unsupported layout;
  replacement GameInstance; old callback ownership after reload; repeated and
  intermittent error suppression.

## Runtime audit

- No F6 or other keybinds, menu code, screenshot capture, or file I/O.
- One native bootstrap lookup for GameInstance; future instances use notification.
- Checks run every 500 ms on the game thread, not every rendered frame.
- Stable checks follow a short ownership chain, read viewport size and compare
  numeric identity/resolution. No layout getters/writes on unchanged instances.
- One startup log and at most five warning messages per initialization.
- Distribution contains Lua source, enabled.txt, documentation/license and comparison images.

## Remaining live validation

Portrait transitions and the portrait correction in cockpit/HUD-only views have
not been separately confirmed. The alternate event portrait panel is unchanged.

The radar mask is refreshed by the game on radar mode changes; changing resolution
while a radar is open may require collapsing and expanding it once.

32:9 has mock coverage but has not been visually tested. Actual frame-time cost
is unmeasured; absence of recurring
scans/logging is not a guarantee that no game/rendering event can cause a hitch.

A game update introducing different HUD dimensions is intentionally unsupported
until inspected. The mod does not continuously fight native code that overwrites
an unchanged canvas. Unknown layouts remain unmodified.
