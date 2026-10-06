# AC8 Ultrawide HUD 0.1.4

Moves the gameplay HUD toward the edges of an ultrawide screen while preserving text/icon sizes and the central HUD position. Includes radar and communication-portrait mask corrections.

## Changes

- Retains the portrait-mask fix introduced in 0.1.3, confirmed in-game in third-person view.
- Adds cinematic camera adjustments intended to remove camera bars and improve framing on very wide displays.
- The extra cinematic projection correction activates only above **2.4:1**, such as 32:9. Typical 21:9 resolutions (2560x1080 and 3440x1440) are below that threshold and do not need this extra correction if cutscenes already look correct.
- Separately, camera aspect-ratio constraints are disabled at all ratios to attempt black-bar removal. This may have no visible effect on cutscenes that already display correctly.
- Existing HUD, radar and portrait fixes remain applicable at 21:9.

## Install or update

UE4SS must already be installed. Close the game, extract **AC8UltrawideHUD-0.1.4.zip**, and copy its `AC8UltrawideHUD` folder into `Game/Binaries/Win64/UE4SS/Mods/`, replacing the existing mod files. Restart the game; no configuration or hotkeys are required.

## Validation and limitations

Automated HUD lifecycle, mask-position and camera-behavior tests pass. The new cinematic changes still require in-game validation, and 32:9 has not been visually tested. Camera overrides are not restored when switching back to a narrower aspect ratio during the same session.

Portrait transitions and the portrait correction in cockpit/HUD-only views have not been separately confirmed. The alternate event portrait panel is unchanged. After changing resolution with the radar open, collapse and expand it once to refresh its mask.

Download the mod ZIP to install. The `.zip.sha256` file verifies that download. The optional **GitHub-source ZIP** contains the repository sources and is not the installation package.
