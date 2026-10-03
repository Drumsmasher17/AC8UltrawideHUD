# Release notes

## Unreleased — portrait mask correction (live validation pending)

- Fixes enemy target boxes disappearing in clear sky beside the speaking-character
  portrait in third-person view on ultrawide screens.
- Aligns the portrait mask with the visible portrait without moving or resizing it.

The fix was confirmed in-game by the user. 32:9 has automated mock coverage but
has not been visually tested.

## 0.1.2

- Corrects the radar background mask's horizontal position on ultrawide screens.
- Applies automatically with the gameplay HUD; no shortcut is required.
- Preserves the radar's visible position and size.

The automatic correction was confirmed in-game. If resolution
changes while the radar is open, collapse and expand it to refresh its mask.

## 0.1.1

- Gameplay HUD adjusts automatically to ultrawide aspect ratios.
- Keeps existing icon/text sizes and left/centre/right anchors.
- Checks current HUD ownership and viewport every 500 ms without recurring
  global-object enumeration.
- Compares native UObject addresses, avoiding false changes from fresh Lua wrappers.
- Removes experimental screenshot keybinds and all menu modifications.
- Removes successful-application logging and limits compatibility/error warnings.

The gameplay layout change has been visually confirmed in multiple missions.
Automated lifecycle behaviour has mock coverage. No frame-time benchmark has
been performed.
