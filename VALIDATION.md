# Validation

## Verified

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
- One startup log and at most three warning messages per initialization.
- Distribution contains Lua source, enabled.txt and documentation/license only.

## Remaining live validation

The final address-comparison revision has not yet been run in the game. Before
describing it as fully tested, launch, enter a mission, change missions without
hotkeys, and check that the layout is correct in both. Confirm UE4SS.log has no
repeated mod messages. Actual frame-time cost is unmeasured; absence of recurring
scans/logging is not a guarantee that no game/rendering event can cause a hitch.

A game update introducing different HUD dimensions is intentionally unsupported
until inspected. The mod does not continuously fight native code that overwrites
an unchanged canvas. Unknown layouts remain unmodified.
