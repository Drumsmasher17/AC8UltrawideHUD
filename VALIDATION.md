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
- Camera components and level-sequence players are enumerated once at bootstrap,
  then tracked by creation notifications and pruned when invalid.
- Checks run every 500 ms on the game thread, not every rendered frame.
- Stable checks follow a short ownership chain, read viewport size and compare
  numeric identity/resolution. No layout getters/writes on unchanged instances.
- Camera checks iterate tracked objects every 500 ms and may reapply projection
  settings even when the HUD is unchanged.
- One startup log and at most six warning messages per initialization.
- Distribution contains Lua source, enabled.txt, documentation/license and comparison images.

## Remaining live validation

The added cinematic camera changes require in-game testing, including cutscenes,
gameplay camera transitions and changing aspect ratio. Constraints are disabled
at all aspect ratios; projection overrides apply only above 2.4:1. Previous
camera settings are not restored on return to a narrower viewport.

Typical 21:9 resolutions (2560x1080 and 3440x1440) are below the strictly
greater-than-2.4:1 projection threshold; 5120x1440 (32:9) is above it. The user
reported no visible black bars or unusual FOV in the 21:9 cutscenes they reviewed
from before these changes. The extra projection correction is unnecessary for
those already-correct cutscenes; this does not establish that all 21:9 cutscenes
are unaffected by the separate constraint-removal behavior. HUD and mask fixes
remain applicable at 21:9.

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
