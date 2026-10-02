# Installation

1. Install a game-compatible UE4SS build. This mod requires
   `LoopInGameThreadWithDelay`, `NotifyOnNewObject`, `ExecuteInGameThread`,
   `ModRef` shared variables, and reflected UMG APIs. It has been developed with
   the local UE4SS build identifying itself as 3.0.1 Beta, Git SHA 03dbd5c0;
   compatibility with other builds is not established.
2. Extract the release ZIP into your active UE4SS `Mods` directory.
3. Verify the resulting paths are `Mods/AC8UltrawideHUD/Scripts/main.lua` and
   `Mods/AC8UltrawideHUD/enabled.txt`.
4. Disable any earlier AC8HUDProbe experiment, then restart the game.

No keybinds or settings are needed. The gameplay HUD adjusts after it becomes
available. Menu layouts are intentionally unchanged.

To uninstall, remove the AC8UltrawideHUD folder and restart the game. To disable
temporarily, remove enabled.txt; if you also added an entry to mods.txt, disable
that entry too. Restarting recreates the game's original layout.

If it does not activate, inspect UE4SS.log for the AC8UltrawideHUD startup line
and any compatibility warning. Do not install two copies of the mod.
