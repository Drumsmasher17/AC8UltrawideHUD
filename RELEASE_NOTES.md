# AC8 Ultrawide HUD 0.1.3

Fixes enemy target boxes disappearing in clear sky beside the speaking-character
portrait in third-person view on ultrawide screens. The portrait mask now follows
the ultrawide layout while the visible portrait stays in the same position and size.
The fix has been confirmed in-game.

## Install or update

UE4SS must already be installed. Close the game, extract
`AC8UltrawideHUD-0.1.3.zip`, and copy its `AC8UltrawideHUD` folder into
`Game/Binaries/Win64/UE4SS/Mods/`, replacing the existing mod files when updating.
Launch the game; no configuration or hotkeys are required.

## Validation and limitations

Automated lifecycle and mask-position tests pass, including 21:9, 32:9 and return
to 16:9. 32:9 has not been visually tested. Portrait transitions and the portrait
correction in cockpit/HUD-only views have not been separately confirmed. The
alternate event portrait panel is unchanged. After changing resolution with the
radar open, collapse and expand it once to refresh its mask.

Download the mod ZIP for installation. The GitHub-source ZIP is for repository
import, not installation. The `.zip.sha256` file verifies the mod download.
