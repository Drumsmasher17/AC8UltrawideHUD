# AC8 Ultrawide HUD

Widens the gameplay HUD's centred 3840×2160 MainCanvas to match the viewport
aspect ratio, retaining height, child sizes and existing left/centre/right anchors.
Menus, aircraft selection, shaders, camera FOV and targeting projection canvases
are not modified.

## Comparisons

Each image shows the original HUD above and the ultrawide HUD below.

### Third person

![Third-person HUD comparison: original above, ultrawide below](AC8Ultrawide_ThirdPerson.png)

### Cockpit

![Cockpit HUD comparison: original above, ultrawide below](AC8Ultrawide_Cockpit.png)

### HUD only

![HUD-only comparison: original above, ultrawide below](AC8Ultrawide_HUDOnly.png)

## Installation

Copy the `AC8UltrawideHUD` folder from the release zip into the active UE4SS Mods
directory and restart the game. See [installation instructions](INSTALL.md).
Requires a UE4SS build exposing
`LoopInGameThreadWithDelay`, `NotifyOnNewObject`, and reflected UMG APIs.
No keys or configuration are required. Remove `enabled.txt` and restart to disable.

The mod checks the current player controller → HUD → AlwaysVisibleCanvas →
MainCanvas every 500 ms on the game thread. It applies once per new canvas or
viewport resolution change. It preserves the original width at 16:9 or narrower.
There is one bootstrap GameInstance lookup; subsequent GameInstances are tracked
by construction notification. Stable checks do not scan global objects, write
files, or change widget properties. Object identity uses the underlying Unreal
address rather than Lua wrapper equality. Logging is limited to one startup line
and at most one warning for each of three failure categories per mod initialization.
Successful checks and applications produce no log output.

Only the observed centred 3840×2160 layout is accepted. Unknown layouts are skipped.
This release has no menu fixes or diagnostic capture hotkeys. Do not enable the
old AC8HUDProbe alongside it. A restart clears any earlier menu experiments.

Manual HUD resizing was confirmed in multiple missions. Automated lifecycle and
resolution handling have mock coverage; actual automatic mission transitions
still require in-game validation. Polling cost has not been benchmarked. Expect
up to roughly 500 ms after widgets become ready before application, longer while
the game thread is blocked. Native code resetting the same canvas without an
instance/resolution change is not continuously overridden.

## Development

Python is only required to test/package the mod, not to play:

```sh
python -m pip install -r requirements-dev.txt
python tests/test_lifecycle.py
python package.py
```

The release archive is generated under `dist/`. Tests simulate UObject lifetime,
fresh Lua wrappers, viewport changes, reload ownership and bounded error logging.
They do not measure UE4SS reflection overhead or rendering frame times.
See [validation notes](VALIDATION.md) and [release notes](CHANGELOG.md).

## Development credit

GPT wrote the code and investigated the game's HUD layout. The project maintainer
directed the work and tested the results in-game.

## License

This project's own code and documentation are dedicated to the public domain
under **CC0 1.0 Universal**. You are welcome to fork, copy, modify, redistribute,
and release your own version, including for commercial use. No permission or
credit is required.

The complete CC0 text is provided in the standalone [LICENSE](LICENSE) file.
This dedication covers the project's own contributions; it does not cover
third-party software or the game's content shown in the screenshots. UE4SS and
game files are not bundled.
